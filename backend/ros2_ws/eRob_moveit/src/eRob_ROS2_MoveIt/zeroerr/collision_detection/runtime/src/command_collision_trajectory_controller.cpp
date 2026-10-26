#include "zeroerr/command_collision_brake.hpp"
#include "zeroerr/sensorless_configuration.hpp"
#include "zeroerr/collision_event_diagnostics.hpp"

#include <joint_trajectory_controller/joint_trajectory_controller.hpp>
#include <ament_index_cpp/get_package_share_directory.hpp>
#include <pluginlib/class_list_macros.hpp>
#include <urdf/model.h>
#include <chrono>
#include <limits>

namespace zeroerr
{
// Standard JTC for all ordinary/operator goals. Only explicitly marked collision
// goals are regenerated from the outgoing command inside the update thread.
class CommandCollisionTrajectoryController final
  : public joint_trajectory_controller::JointTrajectoryController
{
public:
  controller_interface::CallbackReturn on_configure(const rclcpp_lifecycle::State & state) override
  {
    auto result = JointTrajectoryController::on_configure(state);
    if (result != controller_interface::CallbackReturn::SUCCESS) {return result;}
    try {
      if (dof_ != 6 || num_cmd_joints_ != 6 || !has_position_command_interface_) {
        throw std::runtime_error("Command collision brake requires six position-command joints");
      }
      const auto package = ament_index_cpp::get_package_share_directory("zeroerr");
      const std::filesystem::path profile(sensorless_profile_path(package));
      const auto runtime = load_sensorless_config(profile)["runtime"];
      max_duration_ = runtime["EXECUTOR_COLLISION_STOP_MAX_DURATION_S"].as<double>();
      max_travel_ = runtime["EXECUTOR_COLLISION_STOP_MAX_TRAVEL_RAD"].as<double>();
      tracking_limit_ = runtime["EXECUTOR_COLLISION_STOP_TRACKING_TOL_RAD"].as<double>();
      auto limits_path = profile.parent_path() / "joint_limits.yaml";
      if (!std::filesystem::is_regular_file(limits_path)) {
        limits_path = std::filesystem::path(package) / "config/joint_limits.yaml";
      }
      const auto limits = YAML::LoadFile(limits_path.string())["joint_limits"];
      urdf::Model model;
      if (!model.initString(get_robot_description())) {throw std::runtime_error("Missing robot URDF");}
      for (size_t i = 0; i < 6; ++i) {
        const auto raw = limits[params_.joints[i]];
        bounds_.velocity[i] = raw["max_velocity"].as<double>();
        bounds_.acceleration[i] = raw["max_acceleration"].as<double>();
        if (raw["max_deceleration"]) {
          const double deceleration = std::abs(raw["max_deceleration"].as<double>());
          if (!std::isfinite(deceleration) || deceleration <= 0) {
            throw std::runtime_error("Invalid collision deceleration limit");
          }
          bounds_.acceleration[i] = std::min(bounds_.acceleration[i], deceleration);
        }
        bounds_.jerk[i] = raw["max_jerk"].as<double>();
        const auto joint = model.getJoint(params_.joints[i]);
        if (!joint || !joint->limits) {throw std::runtime_error("Missing joint bounds");}
        bounds_.lower[i] = joint->type == urdf::Joint::CONTINUOUS ?
          -std::numeric_limits<double>::infinity() : joint->limits->lower;
        bounds_.upper[i] = joint->type == urdf::Joint::CONTINUOUS ?
          std::numeric_limits<double>::infinity() : joint->limits->upper;
      }
      for (auto & buffer : buffers_) {
        buffer = std::make_shared<trajectory_msgs::msg::JointTrajectory>();
        buffer->joint_names = params_.joints;
        buffer->points.resize(CommandCollisionBrake::points);
        for (auto & point : buffer->points) {
          point.positions.resize(6);
          point.velocities.resize(6);
          point.accelerations.resize(6);
        }
      }
      diagnostics_timer_ = get_node()->create_wall_timer(std::chrono::milliseconds(20), [this]() {
        Diagnostic d;
        while (diagnostics_.try_pop(d)) {
          RCLCPP_WARN(get_node()->get_logger(),
            "[CollisionCommandBrake] accepted=%s generation_us=%.3f duration_s=%.6f "
            "max_command_feedback_error_rad=%.6f source=last_commanded_state "
            "start_position_discontinuity_rad=[%.9f,%.9f,%.9f,%.9f,%.9f,%.9f] "
            "end_positions=[%.6f,%.6f,%.6f,%.6f,%.6f,%.6f]",
            d.accepted ? "true" : "false", d.generation_us, d.duration, d.tracking_error,
            d.step[0], d.step[1], d.step[2], d.step[3], d.step[4], d.step[5],
            d.end[0], d.end[1], d.end[2], d.end[3], d.end[4], d.end[5]);
          if (!d.accepted) {
            const auto & r = d.rejection;
            const char * joint = r.joint >= 0 && r.joint < 6 ?
              params_.joints[r.joint].c_str() : "none";
            RCLCPP_WARN(get_node()->get_logger(),
              "[CollisionCommandBrakeReject] reason=%s joint=%s sample=%d time_s=%.9f "
              "value=%.9f limit=%.9f ruckig_result=%d generated_duration_s=%.9f "
              "max_duration_s=%.6f max_travel_rad=%.6f tracking_limit_rad=%.6f "
              "state_sizes=[%zu,%zu,%zu,%zu]",
              CommandCollisionBrake::failure_name(r.reason), joint, r.sample, r.time,
              r.value, r.limit, r.generator_result, d.duration,
              max_duration_, max_travel_, tracking_limit_,
              d.sizes[0], d.sizes[1], d.sizes[2], d.sizes[3]);
            // All formatting happens outside the real-time update thread.
            for (size_t i = 0; i < 6; ++i) {
              RCLCPP_WARN(get_node()->get_logger(),
                "[CollisionCommandBrakeState] joint=%s commanded_q=%.12f commanded_v=%.12f "
                "commanded_a=%.12f measured_q=%.12f velocity_limit=%.9f "
                "acceleration_limit=%.9f jerk_limit=%.9f lower=%.9f upper=%.9f",
                params_.joints[i].c_str(), d.q[i], d.v[i], d.a[i], d.measured[i],
                bounds_.velocity[i], bounds_.acceleration[i], bounds_.jerk[i],
                bounds_.lower[i], bounds_.upper[i]);
            }
          }
        }
      });
    } catch (const std::exception & error) {
      RCLCPP_ERROR(get_node()->get_logger(), "Cannot configure command collision brake: %s", error.what());
      return controller_interface::CallbackReturn::ERROR;
    }
    return result;
  }

  controller_interface::return_type update(
    const rclcpp::Time & time, const rclcpp::Duration & period) override
  {
    const auto pending = *new_trajectory_msg_.readFromRT();
    const auto current = current_trajectory_->get_trajectory_msg();
    const auto active = *rt_active_goal_.readFromRT();
    // Match JTC's pending-goal gate: never consume the message before its action
    // handle/tolerances are installed. Never mutate the non-RT action message.
    if (pending && pending != current && !(rt_has_pending_goal_ && !active) &&
      pending->header.frame_id == "zeroerr_command_brake_v1")
    {
      const auto started = std::chrono::steady_clock::now();
      Diagnostic diagnostic{};
      CommandCollisionBrake::Vector q{}, v{}, a{}, measured{};
      read_state_from_state_interfaces(state_current_);
      diagnostic.sizes = {last_commanded_state_.positions.size(),
        last_commanded_state_.velocities.size(), last_commanded_state_.accelerations.size(),
        state_current_.positions.size()};
      diagnostic.rejection.reason = pending->joint_names != params_.joints ?
        CommandCollisionBrake::Failure::joint_order : CommandCollisionBrake::Failure::state_layout;
      bool valid = pending->joint_names == params_.joints &&
        last_commanded_state_.positions.size() == 6 &&
        last_commanded_state_.velocities.size() == 6 &&
        last_commanded_state_.accelerations.size() == 6 &&
        state_current_.positions.size() == 6;
      if (valid) {
        for (size_t i = 0; i < 6; ++i) {
          q[i] = last_commanded_state_.positions[i];
          v[i] = last_commanded_state_.velocities[i];
          a[i] = last_commanded_state_.accelerations[i];
          measured[i] = state_current_.positions[i];
          diagnostic.tracking_error = std::max(diagnostic.tracking_error, std::abs(q[i] - measured[i]));
        }
        valid = brake_.calculate(q, v, a, measured, bounds_, max_duration_, max_travel_, tracking_limit_);
        diagnostic.rejection = brake_.rejection();
        diagnostic.duration = brake_.duration();
      }
      diagnostic.q = q;
      diagnostic.v = v;
      diagnostic.a = a;
      diagnostic.measured = measured;
      diagnostic.accepted = valid;
      if (valid) {
        // Alternating, preallocated buffers stay alive across JTC replacement.
        // No vector resizing, ROS publication, file I/O or allocation here.
        buffer_index_ = 1 - buffer_index_;
        auto buffer = buffers_[buffer_index_];
        const auto & samples = brake_.samples();
        for (size_t row = 0; row < samples.size(); ++row) {
          auto & point = buffer->points[row];
          point.time_from_start = rclcpp::Duration::from_seconds(samples[row].time);
          for (size_t i = 0; i < 6; ++i) {
            point.positions[i] = samples[row].position[i];
            point.velocities[i] = samples[row].velocity[i];
            point.accelerations[i] = samples[row].acceleration[i];
          }
        }
        diagnostic.duration = brake_.duration();
        diagnostic.end = samples.back().position;
        for (size_t i = 0; i < 6; ++i) {diagnostic.step[i] = samples.front().position[i] - q[i];}
        new_trajectory_msg_.initRT(buffer);
        // Already in exact local order. Installing here avoids JTC's generic
        // per-point vector remapping/allocation in the takeover cycle. The base
        // update still performs its normal first-sample initialization and all
        // action/tolerance/command handling.
        current_trajectory_->update(buffer);
      } else {
        // Never forward an invalid marked goal to the ordinary time-zero path.
        // Controller-manager error handling deactivates this controller; the
        // collision interlock remains latched. Do not invent a moving hold.
        diagnostic.generation_us = std::chrono::duration<double, std::micro>(
          std::chrono::steady_clock::now() - started).count();
        diagnostics_.try_push(diagnostic);
        return controller_interface::return_type::ERROR;
      }
      diagnostic.generation_us = std::chrono::duration<double, std::micro>(
        std::chrono::steady_clock::now() - started).count();
      diagnostics_.try_push(diagnostic);
    }
    return JointTrajectoryController::update(time, period);
  }
private:
  struct Diagnostic {
    bool accepted{false};
    double generation_us{0}, duration{0}, tracking_error{0};
    CommandCollisionBrake::Vector step{}, end{}, q{}, v{}, a{}, measured{};
    CommandCollisionBrake::Rejection rejection{};
    std::array<size_t, 4> sizes{};
  };
  CommandCollisionBrake brake_;
  CommandCollisionBrake::Limits bounds_{};
  std::array<std::shared_ptr<trajectory_msgs::msg::JointTrajectory>, 2> buffers_;
  size_t buffer_index_{0};
  double max_duration_{0}, max_travel_{0}, tracking_limit_{0};
  CollisionDiagnosticQueue<Diagnostic, 16> diagnostics_;
  rclcpp::TimerBase::SharedPtr diagnostics_timer_;
};
}  // namespace zeroerr
PLUGINLIB_EXPORT_CLASS(zeroerr::CommandCollisionTrajectoryController, controller_interface::ControllerInterface)
