#include "zeroerr/realtime_collision_controller.hpp"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <limits>

#include <ament_index_cpp/get_package_share_directory.hpp>
#include <kdl_parser/kdl_parser.hpp>
#include <nlohmann/json.hpp>
#include <pluginlib/class_list_macros.hpp>

namespace zeroerr
{
namespace
{
constexpr double kGravity = -9.81;
constexpr double kPi = 3.14159265358979323846;

template<typename ContainerT>
void load_joint_array(
  const nlohmann::json & source, const char * key, ContainerT & destination)
{
  if (!source.contains(key) || !source.at(key).is_array()) {
    return;
  }
  const auto & values = source.at(key);
  for (std::size_t index = 0; index < destination.size() && index < values.size(); ++index) {
    destination[index] = values.at(index).get<double>();
  }
}
}  // namespace

controller_interface::CallbackReturn RealtimeCollisionController::on_init()
{
  joint_names_ = auto_declare<std::vector<std::string>>(
    "joints", {"Joint_1", "Joint_2", "Joint_3", "Joint_4", "Joint_5", "Joint_6"});
  base_link_ = auto_declare<std::string>("base_link", "base_link");
  tip_link_ = auto_declare<std::string>("tip_link", "tool0");
  config_path_ = auto_declare<std::string>("collision_config_path", "");
  observer_gain_ = auto_declare<double>("observer_gain", 10.0);
  filter_alpha_ = auto_declare<double>("filter_alpha", 0.7);
  acceleration_filter_cutoff_hz_ =
    auto_declare<double>("acceleration_filter_cutoff_hz", 40.0);
  plot_period_sec_ = auto_declare<double>("plot_period_sec", 0.0005);
  timing_period_sec_ = auto_declare<double>("timing_period_sec", 0.01);
  warmup_sec_ = auto_declare<double>("warmup_sec", 8.0);
  drive_stable_sec_ = auto_declare<double>("drive_stable_sec", 2.0);
  warmup_velocity_limit_ = auto_declare<double>("warmup_velocity_limit", 0.02);
  warmup_min_samples_ = static_cast<std::size_t>(
    std::max<std::int64_t>(1, auto_declare<std::int64_t>("warmup_min_samples", 20)));
  static_floor_.fill(10.0);
  training_velocity_limit_.fill(std::numeric_limits<double>::infinity());
  training_acceleration_limit_.fill(std::numeric_limits<double>::infinity());
  motion_velocity_limit_.fill(std::numeric_limits<double>::infinity());
  motion_acceleration_limit_.fill(std::numeric_limits<double>::infinity());
  return controller_interface::CallbackReturn::SUCCESS;
}

controller_interface::InterfaceConfiguration
RealtimeCollisionController::command_interface_configuration() const
{
  return {controller_interface::interface_configuration_type::NONE, {}};
}

controller_interface::InterfaceConfiguration
RealtimeCollisionController::state_interface_configuration() const
{
  controller_interface::InterfaceConfiguration config;
  config.type = controller_interface::interface_configuration_type::INDIVIDUAL;
  for (const auto & joint : joint_names_) {
    config.names.push_back(joint + "/position");
    config.names.push_back(joint + "/velocity");
    config.names.push_back(joint + "/torque_sensor");
    config.names.push_back(joint + "/statusword");
    config.names.push_back(joint + "/error_code");
  }
  return config;
}

controller_interface::CallbackReturn RealtimeCollisionController::on_configure(
  const rclcpp_lifecycle::State &)
{
  if (joint_names_.size() != kJointCount || !load_model() || !load_config()) {
    return controller_interface::CallbackReturn::ERROR;
  }
  auto node = get_node();
  residual_publisher_ = std::make_shared<
    realtime_tools::RealtimePublisher<sensor_msgs::msg::JointState>>(
    node->create_publisher<sensor_msgs::msg::JointState>(
      "/zeroerr/collision_monitor/plot/external_torque", rclcpp::SensorDataQoS()));
  threshold_publisher_ = std::make_shared<
    realtime_tools::RealtimePublisher<sensor_msgs::msg::JointState>>(
    node->create_publisher<sensor_msgs::msg::JointState>(
      "/zeroerr/collision_monitor/plot/external_torque_threshold", rclcpp::SensorDataQoS()));
  timing_publisher_ = std::make_shared<
    realtime_tools::RealtimePublisher<std_msgs::msg::String>>(
    node->create_publisher<std_msgs::msg::String>(
      "/zeroerr/collision_rt/timing", rclcpp::SystemDefaultsQoS()));
  stop_publisher_ = std::make_shared<
    realtime_tools::RealtimePublisher<std_msgs::msg::String>>(
    node->create_publisher<std_msgs::msg::String>(
      "/zeroerr/collision_monitor/stop_request", rclcpp::SystemDefaultsQoS()));
  state_publisher_ = std::make_shared<
    realtime_tools::RealtimePublisher<control_msgs::msg::DynamicJointState>>(
    node->create_publisher<control_msgs::msg::DynamicJointState>(
      "/zeroerr/collision_monitor/state", rclcpp::SystemDefaultsQoS()));
  peak_publisher_ = std::make_shared<
    realtime_tools::RealtimePublisher<control_msgs::msg::DynamicJointState>>(
    node->create_publisher<control_msgs::msg::DynamicJointState>(
      "/zeroerr/collision_rt/peak_samples", rclcpp::SensorDataQoS()));
  config_state_publisher_ = node->create_publisher<std_msgs::msg::String>(
    "/zeroerr/collision_monitor/config_state", rclcpp::QoS(1).transient_local().reliable());
  config_subscription_ = node->create_subscription<std_msgs::msg::String>(
    "/zeroerr/collision_monitor/config", rclcpp::QoS(10).reliable(),
    std::bind(&RealtimeCollisionController::apply_config_message, this, std::placeholders::_1));
  acknowledgement_subscription_ = node->create_subscription<std_msgs::msg::String>(
    "/zeroerr/collision_monitor/acknowledged", rclcpp::QoS(10).reliable(),
    std::bind(&RealtimeCollisionController::acknowledge_collision, this, std::placeholders::_1));
  config_state_timer_ = node->create_wall_timer(
    std::chrono::milliseconds(500), [this]() {publish_config_state(non_rt_config_);});
  for (std::size_t index = 0; index < kJointCount; ++index) {
    stop_payloads_[index] = "{\"joint\":\"" + joint_names_[index] +
      "\",\"detector\":\"cpp_realtime_dynamics\",\"mode\":\"active\"}";
  }
  residual_publisher_->msg_.name = joint_names_;
  residual_publisher_->msg_.position.resize(kJointCount);
  threshold_publisher_->msg_.name = joint_names_;
  threshold_publisher_->msg_.position.resize(kJointCount);
  timing_publisher_->msg_.data.reserve(256);
  stop_publisher_->msg_.data.reserve(128);
  state_publisher_->msg_.joint_names = joint_names_;
  state_publisher_->msg_.interface_values.resize(kJointCount);
  for (auto & interfaces : state_publisher_->msg_.interface_values) {
    interfaces.interface_names = {"observer_ready"};
    interfaces.values.resize(1);
  }
  peak_publisher_->msg_.joint_names = joint_names_;
  peak_publisher_->msg_.interface_values.resize(kJointCount);
  for (auto & interfaces : peak_publisher_->msg_.interface_values) {
    interfaces.interface_names = {
      "position_1", "position_2", "position_3", "position_4", "position_5", "position_6",
      "velocity", "acceleration", "measured_torque", "expected_torque",
      "external_torque", "threshold"};
    interfaces.values.resize(12);
  }
  reset_observer();
  publish_config_state(non_rt_config_);
  RCLCPP_INFO(
    node->get_logger(), "Realtime collision controller configured as sole collision observer");
  return controller_interface::CallbackReturn::SUCCESS;
}

controller_interface::CallbackReturn RealtimeCollisionController::on_activate(
  const rclcpp_lifecycle::State &)
{
  reset_observer();
  return controller_interface::CallbackReturn::SUCCESS;
}

controller_interface::CallbackReturn RealtimeCollisionController::on_deactivate(
  const rclcpp_lifecycle::State &)
{
  reset_observer();
  return controller_interface::CallbackReturn::SUCCESS;
}

bool RealtimeCollisionController::load_model()
{
  KDL::Tree tree;
  if (!kdl_parser::treeFromString(get_robot_description(), tree) ||
    !tree.getChain(base_link_, tip_link_, chain_) || chain_.getNrOfJoints() != kJointCount)
  {
    RCLCPP_ERROR(get_node()->get_logger(), "Unable to build six-axis KDL collision chain");
    return false;
  }
  dynamics_ = std::make_unique<KDL::ChainDynParam>(
    chain_, KDL::Vector(0.0, 0.0, kGravity));
  inverse_dynamics_ = std::make_unique<KDL::ChainIdSolver_RNE>(
    chain_, KDL::Vector(0.0, 0.0, kGravity));
  external_wrenches_.assign(chain_.getNrOfSegments(), KDL::Wrench::Zero());
  return true;
}

bool RealtimeCollisionController::load_config()
{
  try {
    if (config_path_.empty()) {
      config_path_ = ament_index_cpp::get_package_share_directory("zeroerr") +
        "/config/collision_monitor_config.json";
    }
    std::ifstream input(config_path_);
    if (!input) {
      throw std::runtime_error("cannot open " + config_path_);
    }
    nlohmann::json config;
    input >> config;
    config["effort_following_error_detection_enabled"] = false;
    non_rt_config_.detection_enabled = config.value("detection_enabled", true);
    non_rt_config_.active_stop_enabled = config.value("active_stop_enabled", false);
    non_rt_config_.diagnostics_enabled = config.value("diagnostics_enabled", true);
    non_rt_config_.dynamic_threshold_enabled = config.value("dynamic_threshold_enabled", true);
    non_rt_config_.detection_suppressed = config.value("collision_detection_suppressed", false);
    non_rt_config_.confirm_duration_sec =
      std::max(0.0, config.value("confirm_duration_ms", 25.0)) * 1.0e-3;
    non_rt_config_.sensitivity_percent =
      std::clamp(config.value("collision_sensitivity_percent", 100.0), 50.0, 200.0);
    non_rt_config_.threshold_max_ratio =
      std::clamp(config.value("dynamic_threshold_max_ratio", 3.5), 1.0, 20.0);
    non_rt_config_.threshold_decay_sec =
      std::max(0.01, config.value("dynamic_threshold_decay_sec", 0.35));
    load_joint_array(config, "external_torque_thresholds", static_floor_);
    non_rt_config_.static_floor = static_floor_;
    load_joint_array(config, "friction_coulomb_nm", friction_coulomb_);
    load_joint_array(config, "friction_viscous_nm_per_rad_s", friction_viscous_);
    friction_coulomb_positive_ = friction_coulomb_;
    friction_coulomb_negative_ = friction_coulomb_;
    friction_static_positive_ = friction_coulomb_;
    friction_static_negative_ = friction_coulomb_;
    load_joint_array(config, "friction_coulomb_positive_nm", friction_coulomb_positive_);
    load_joint_array(config, "friction_coulomb_negative_nm", friction_coulomb_negative_);
    load_joint_array(config, "friction_static_positive_nm", friction_static_positive_);
    load_joint_array(config, "friction_static_negative_nm", friction_static_negative_);
    friction_deadband_ = std::max(
      0.0, config.value("friction_velocity_deadband_rad_s", 0.01));
    friction_transition_velocity_ = std::max(
      1.0e-5, config.value("friction_transition_velocity_rad_s", 0.01));
    friction_stribeck_velocity_ = std::max(
      friction_transition_velocity_, config.value("friction_stribeck_velocity_rad_s", 0.05));
    for (std::size_t index = 0; index < kJointCount; ++index) {
      const auto name = joint_names_[index];
      if (config.contains("dynamic_threshold_coefficients") &&
        config["dynamic_threshold_coefficients"].contains(name))
      {
        load_joint_array(
          config["dynamic_threshold_coefficients"], name.c_str(),
          threshold_coefficients_[index]);
      }
      if (config.contains("dynamic_threshold_training_limits") &&
        config["dynamic_threshold_training_limits"].contains(name))
      {
        const auto & limits = config["dynamic_threshold_training_limits"][name];
        training_velocity_limit_[index] = limits.at(0).get<double>();
        training_acceleration_limit_[index] = limits.at(1).get<double>();
      }
      if (config.contains("position_correction_coefficients") &&
        config["position_correction_coefficients"].contains(name))
      {
        load_joint_array(
          config["position_correction_coefficients"], name.c_str(),
          position_coefficients_[index]);
      }
      if (config.contains("motion_residual_correction_coefficients") &&
        config["motion_residual_correction_coefficients"].contains(name))
      {
        load_joint_array(
          config["motion_residual_correction_coefficients"], name.c_str(),
          motion_coefficients_[index]);
      }
      if (config.contains("motion_residual_correction_limits") &&
        config["motion_residual_correction_limits"].contains(name))
      {
        const auto & limits = config["motion_residual_correction_limits"][name];
        motion_velocity_limit_[index] = limits.at(0).get<double>();
        motion_acceleration_limit_[index] = limits.at(1).get<double>();
      }
    }
    config_state_json_ = config.dump();
    runtime_config_.writeFromNonRT(non_rt_config_);
  } catch (const std::exception & error) {
    RCLCPP_ERROR(get_node()->get_logger(), "Collision config load failed: %s", error.what());
    return false;
  }
  return true;
}

void RealtimeCollisionController::apply_config_message(
  const std_msgs::msg::String::SharedPtr message)
{
  try {
    auto state = nlohmann::json::parse(config_state_json_);
    const auto update = nlohmann::json::parse(message->data);
    if (!update.is_object()) {
      return;
    }
    for (auto item = update.begin(); item != update.end(); ++item) {
      state[item.key()] = item.value();
    }
    state["effort_following_error_detection_enabled"] = false;
    auto next = non_rt_config_;
    next.detection_enabled = state.value("detection_enabled", true);
    next.active_stop_enabled = state.value("active_stop_enabled", false);
    next.diagnostics_enabled = state.value("diagnostics_enabled", true);
    next.dynamic_threshold_enabled = state.value("dynamic_threshold_enabled", true);
    next.detection_suppressed = state.value("collision_detection_suppressed", false);
    next.confirm_duration_sec =
      std::max(0.0, state.value("confirm_duration_ms", 25.0)) * 1.0e-3;
    next.sensitivity_percent = std::clamp(
      state.value("collision_sensitivity_percent", 100.0), 50.0, 200.0);
    next.threshold_max_ratio = std::clamp(
      state.value("dynamic_threshold_max_ratio", 3.5), 1.0, 20.0);
    next.threshold_decay_sec = std::max(
      0.01, state.value("dynamic_threshold_decay_sec", 0.35));
    load_joint_array(state, "external_torque_thresholds", next.static_floor);
    std::ofstream output(config_path_);
    if (!output) {
      throw std::runtime_error("cannot persist " + config_path_);
    }
    output << state.dump(2) << '\n';
    non_rt_config_ = next;
    config_state_json_ = state.dump();
    runtime_config_.writeFromNonRT(non_rt_config_);
    publish_config_state(non_rt_config_);
  } catch (const std::exception & error) {
    RCLCPP_ERROR(get_node()->get_logger(), "Rejected collision config update: %s", error.what());
  }
}

void RealtimeCollisionController::acknowledge_collision(
  const std_msgs::msg::String::SharedPtr)
{
  reset_requested_.store(true, std::memory_order_release);
}

void RealtimeCollisionController::publish_config_state(const RuntimeConfig &)
{
  if (!config_state_publisher_) {
    return;
  }
  std_msgs::msg::String message;
  message.data = config_state_json_;
  config_state_publisher_->publish(message);
}

bool RealtimeCollisionController::read_inputs(
  JointVector & position, JointVector & velocity, JointVector & torque,
  bool & drives_operational)
{
  constexpr std::size_t interface_count = 5;
  if (state_interfaces_.size() != kJointCount * interface_count) {
    return false;
  }
  drives_operational = true;
  for (std::size_t index = 0; index < kJointCount; ++index) {
    const auto offset = index * interface_count;
    const auto q_value = state_interfaces_[offset].get_optional<double>(1);
    const auto dq_value = state_interfaces_[offset + 1].get_optional<double>(1);
    const auto torque_value = state_interfaces_[offset + 2].get_optional<double>(1);
    const auto statusword = state_interfaces_[offset + 3].get_optional<double>(1);
    const auto error_code = state_interfaces_[offset + 4].get_optional<double>(1);
    if (!q_value || !dq_value || !torque_value || !std::isfinite(*q_value) ||
      !std::isfinite(*dq_value) || !std::isfinite(*torque_value) || !statusword ||
      !error_code || !std::isfinite(*statusword) || !std::isfinite(*error_code))
    {
      return false;
    }
    position[index] = *q_value;
    velocity[index] = *dq_value;
    torque[index] = *torque_value;
    drives_operational = drives_operational &&
      ((static_cast<std::uint16_t>(*statusword) & 0x0004U) != 0U) &&
      static_cast<std::int32_t>(*error_code) == 0;
  }
  return true;
}

bool RealtimeCollisionController::update_observer(
  const JointVector & position, const JointVector & velocity,
  const JointVector & acceleration, const JointVector & measured, const double dt_sec)
{
  for (std::size_t index = 0; index < kJointCount; ++index) {
    q_(index) = position[index];
    dq_(index) = velocity[index];
    ddq_(index) = acceleration[index];
  }
  if (dynamics_->JntToMass(q_, mass_) < 0 || dynamics_->JntToGravity(q_, gravity_) < 0 ||
    inverse_dynamics_->CartToJnt(q_, dq_, ddq_, external_wrenches_, expected_kdl_) < 0)
  {
    return false;
  }

  JointVector momentum{};
  JointVector auxiliary{};
  for (std::size_t row = 0; row < kJointCount; ++row) {
    expected_torque_[row] = expected_kdl_(row);
    auxiliary[row] = gravity_(row);
    for (std::size_t column = 0; column < kJointCount; ++column) {
      momentum[row] += mass_(row, column) * velocity[column];
    }
  }

  constexpr double delta = 1.0e-5;
  for (std::size_t axis = 0; axis < kJointCount; ++axis) {
    q_(axis) += delta;
    if (dynamics_->JntToMass(q_, mass_plus_) < 0) {return false;}
    q_(axis) -= 2.0 * delta;
    if (dynamics_->JntToMass(q_, mass_minus_) < 0) {return false;}
    q_(axis) += delta;
    double quadratic = 0.0;
    for (std::size_t row = 0; row < kJointCount; ++row) {
      for (std::size_t column = 0; column < kJointCount; ++column) {
        quadratic += velocity[row] *
          ((mass_plus_(row, column) - mass_minus_(row, column)) / (2.0 * delta)) *
          velocity[column];
      }
    }
    auxiliary[axis] -= 0.5 * quadratic;
  }

  if (!observer_ready_) {
    warmup_elapsed_sec_ += dt_sec;
    const bool stationary = std::all_of(
      velocity.begin(), velocity.end(), [this](double value) {
        return std::abs(value) < warmup_velocity_limit_;
      });
    if (stationary) {
      ++warmup_samples_;
      for (std::size_t index = 0; index < kJointCount; ++index) {
        warmup_sum_[index] += measured[index] - auxiliary[index];
      }
    }
    if (warmup_elapsed_sec_ >= warmup_sec_ && warmup_samples_ >= warmup_min_samples_) {
      for (std::size_t index = 0; index < kJointCount; ++index) {
        warmup_offset_[index] = warmup_sum_[index] / static_cast<double>(warmup_samples_);
        momentum_integral_[index] = momentum[index];
      }
      observer_ready_ = true;
    }
    return true;
  }

  for (std::size_t index = 0; index < kJointCount; ++index) {
    momentum_integral_[index] +=
      (measured[index] - warmup_offset_[index] - auxiliary[index] - residual_[index]) * dt_sec;
    residual_[index] = observer_gain_ * (momentum_integral_[index] - momentum[index]);
    filtered_residual_[index] = filter_alpha_ * residual_[index] +
      (1.0 - filter_alpha_) * filtered_residual_[index];
  }
  return true;
}

double RealtimeCollisionController::dynamic_threshold(
  const std::size_t index, double velocity, double acceleration, const double dt_sec,
  const RuntimeConfig & config)
{
  velocity = std::clamp(
    velocity, -training_velocity_limit_[index], training_velocity_limit_[index]);
  acceleration = std::clamp(
    acceleration, -training_acceleration_limit_[index], training_acceleration_limit_[index]);
  const double decay = std::exp(-dt_sec / config.threshold_decay_sec);
  auto update_envelope = [decay](double value, double & envelope) {
      envelope = std::max(value, envelope * decay);
    };
  update_envelope(std::max(velocity, 0.0), threshold_envelope_velocity_positive_[index]);
  update_envelope(std::max(-velocity, 0.0), threshold_envelope_velocity_negative_[index]);
  update_envelope(std::max(acceleration, 0.0), threshold_envelope_acceleration_positive_[index]);
  update_envelope(std::max(-acceleration, 0.0), threshold_envelope_acceleration_negative_[index]);
  const std::array<double, 9> features{
    1.0,
    threshold_envelope_velocity_positive_[index],
    threshold_envelope_velocity_negative_[index],
    threshold_envelope_acceleration_positive_[index],
    threshold_envelope_acceleration_negative_[index],
    std::pow(threshold_envelope_velocity_positive_[index], 2),
    std::pow(threshold_envelope_velocity_negative_[index], 2),
    std::pow(threshold_envelope_acceleration_positive_[index], 2),
    std::pow(threshold_envelope_acceleration_negative_[index], 2)};
  double fitted = 0.0;
  for (std::size_t feature = 0; feature < features.size(); ++feature) {
    fitted += threshold_coefficients_[index][feature] * features[feature];
  }
  const double base = config.dynamic_threshold_enabled ? std::min(
    std::max(config.static_floor[index], fitted),
    config.static_floor[index] * config.threshold_max_ratio) : config.static_floor[index];
  return base * (100.0 / config.sensitivity_percent);
}

controller_interface::return_type RealtimeCollisionController::update(
  const rclcpp::Time & time, const rclcpp::Duration & period)
{
  const auto started = std::chrono::steady_clock::now();
  const double dt_sec = std::max(period.seconds(), 1.0e-6);
  if (reset_requested_.exchange(false, std::memory_order_acq_rel)) {
    reset_observer();
  }
  const auto * config_ptr = runtime_config_.readFromRT();
  if (config_ptr == nullptr) {
    return controller_interface::return_type::OK;
  }
  const RuntimeConfig & config = *config_ptr;
  JointVector position{};
  JointVector velocity{};
  JointVector torque{};
  bool drives_operational = false;
  if (!read_inputs(position, velocity, torque, drives_operational)) {
    reset_observer();
    return controller_interface::return_type::OK;
  }
  if (!drives_operational) {
    reset_observer();
    return controller_interface::return_type::OK;
  }
  drives_operational_elapsed_sec_ += dt_sec;
  if (drives_operational_elapsed_sec_ < drive_stable_sec_) {
    return controller_interface::return_type::OK;
  }
  JointVector acceleration{};
  if (have_previous_sample_) {
    const double acceleration_alpha = 1.0 - std::exp(
      -2.0 * kPi * std::max(0.1, acceleration_filter_cutoff_hz_) * dt_sec);
    for (std::size_t index = 0; index < kJointCount; ++index) {
      const double raw_acceleration =
        (velocity[index] - previous_velocity_[index]) / dt_sec;
      filtered_acceleration_[index] += acceleration_alpha *
        (raw_acceleration - filtered_acceleration_[index]);
      acceleration[index] = filtered_acceleration_[index];
    }
  }
  previous_velocity_ = velocity;
  have_previous_sample_ = true;
  JointVector compensated_torque = torque;
  const double q2 = position[1];
  const double q3 = position[2];
  const double q4 = position[3];
  const double q23 = q2 + q3;
  const double q234 = q23 + q4;
  const std::array<double, 9> position_features{
    1.0, std::sin(q2), std::cos(q2), std::sin(q23), std::cos(q23),
    std::sin(q234), std::cos(q234), std::sin(q3), std::cos(q3)};
  for (std::size_t index = 0; index < kJointCount; ++index) {
    const double speed = std::abs(velocity[index]);
    const double direction = std::tanh(
      velocity[index] / friction_transition_velocity_);
    const bool positive = velocity[index] >= 0.0;
    const double coulomb = positive ?
      friction_coulomb_positive_[index] : friction_coulomb_negative_[index];
    const double static_friction = positive ?
      friction_static_positive_[index] : friction_static_negative_[index];
    const double stribeck = std::exp(-std::pow(
      speed / friction_stribeck_velocity_, 2));
    const double friction = direction *
      (coulomb + (static_friction - coulomb) * stribeck) +
      friction_viscous_[index] * velocity[index];
    double position_correction = 0.0;
    for (std::size_t feature = 0; feature < position_features.size(); ++feature) {
      position_correction += position_coefficients_[index][feature] * position_features[feature];
    }
    const double limited_velocity = std::clamp(
      velocity[index], -motion_velocity_limit_[index], motion_velocity_limit_[index]);
    const double limited_acceleration = std::clamp(
      acceleration[index], -motion_acceleration_limit_[index],
      motion_acceleration_limit_[index]);
    const double velocity_positive = std::max(limited_velocity, 0.0);
    const double velocity_negative = std::max(-limited_velocity, 0.0);
    const std::array<double, 6> motion_features{
      velocity_positive, velocity_negative,
      velocity_positive * velocity_positive, velocity_negative * velocity_negative,
      std::max(limited_acceleration, 0.0), std::max(-limited_acceleration, 0.0)};
    double motion_correction = 0.0;
    for (std::size_t feature = 0; feature < motion_features.size(); ++feature) {
      motion_correction += motion_coefficients_[index][feature] * motion_features[feature];
    }
    compensated_torque[index] -= friction + position_correction + motion_correction;
  }
  if (!update_observer(position, velocity, acceleration, compensated_torque, dt_sec)) {
    reset_observer();
    return controller_interface::return_type::OK;
  }

  if (observer_ready_) {
    for (std::size_t index = 0; index < kJointCount; ++index) {
      threshold_[index] = dynamic_threshold(
        index, velocity[index], acceleration[index], dt_sec, config);
      const double magnitude = std::abs(filtered_residual_[index]);
      if (magnitude > peak_samples_[index].absolute_residual) {
        auto & peak = peak_samples_[index];
        peak.absolute_residual = magnitude;
        peak.position = position;
        peak.velocity = velocity[index];
        peak.acceleration = acceleration[index];
        peak.measured_torque = torque[index];
        peak.expected_torque = expected_torque_[index];
        peak.residual = filtered_residual_[index];
        peak.threshold = threshold_[index];
      }
    }
  }

  if (observer_ready_ && config.detection_enabled && !config.detection_suppressed) {
    bool any_exceeded = false;
    std::size_t first_exceeded = 0;
    for (std::size_t index = 0; index < kJointCount; ++index) {
      if (std::abs(filtered_residual_[index]) >= threshold_[index]) {
        exceedance_sec_[index] += dt_sec;
        if (!any_exceeded && exceedance_sec_[index] >= config.confirm_duration_sec) {
          any_exceeded = true;
          first_exceeded = index;
        }
      } else {
        exceedance_sec_[index] = 0.0;
      }
    }
    if (any_exceeded && !stop_latched_) {
      stop_latched_ = true;
      if (config.active_stop_enabled && stop_publisher_ && stop_publisher_->trylock()) {
        stop_publisher_->msg_.data = stop_payloads_[first_exceeded];
        stop_publisher_->unlockAndPublish();
      }
    }
  } else {
    exceedance_sec_.fill(0.0);
  }

  const auto elapsed = std::chrono::steady_clock::now() - started;
  const auto elapsed_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(elapsed);
  ++update_count_;
  max_update_time_ = std::max(max_update_time_, elapsed_ns);
  if (elapsed_ns > std::chrono::duration_cast<std::chrono::nanoseconds>(
      std::chrono::duration<double>(dt_sec)))
  {
    ++overrun_count_;
  }
  diagnostics_elapsed_sec_ += dt_sec;
  timing_elapsed_sec_ += dt_sec;
  publish_timing_this_cycle_ = timing_elapsed_sec_ >= timing_period_sec_;
  if (publish_timing_this_cycle_) {
    timing_elapsed_sec_ = 0.0;
  }
  if (config.diagnostics_enabled && diagnostics_elapsed_sec_ >= plot_period_sec_) {
    diagnostics_elapsed_sec_ = 0.0;
    publish_diagnostics(time, elapsed_ns, true);
  } else if (publish_timing_this_cycle_) {
    publish_diagnostics(time, elapsed_ns, false);
  }
  return controller_interface::return_type::OK;
}

void RealtimeCollisionController::reset_observer()
{
  previous_velocity_.fill(0.0);
  filtered_acceleration_.fill(0.0);
  momentum_integral_.fill(0.0);
  residual_.fill(0.0);
  filtered_residual_.fill(0.0);
  warmup_sum_.fill(0.0);
  warmup_offset_.fill(0.0);
  exceedance_sec_.fill(0.0);
  have_previous_sample_ = false;
  observer_ready_ = false;
  stop_latched_ = false;
  warmup_elapsed_sec_ = 0.0;
  drives_operational_elapsed_sec_ = 0.0;
  warmup_samples_ = 0;
  diagnostics_elapsed_sec_ = 0.0;
  peak_samples_.fill(PeakSample{});
}

void RealtimeCollisionController::publish_diagnostics(
  const rclcpp::Time & time, const std::chrono::nanoseconds elapsed, const bool publish_plot)
{
  auto publish_joint_values = [&](auto & publisher, const JointVector & values) {
      if (publisher && publisher->trylock()) {
        publisher->msg_.header.stamp = time;
        publisher->msg_.name = joint_names_;
        publisher->msg_.position.assign(values.begin(), values.end());
        publisher->unlockAndPublish();
      }
    };
  if (publish_plot) {
    publish_joint_values(residual_publisher_, filtered_residual_);
    publish_joint_values(threshold_publisher_, threshold_);
  }
  if (publish_timing_this_cycle_ && state_publisher_ && state_publisher_->trylock()) {
    state_publisher_->msg_.header.stamp = time;
    for (auto & interfaces : state_publisher_->msg_.interface_values) {
      interfaces.values[0] = observer_ready_ ? 1.0 : 0.0;
    }
    state_publisher_->unlockAndPublish();
  }
  if (
    publish_timing_this_cycle_ && observer_ready_ && peak_publisher_ &&
    peak_publisher_->trylock())
  {
    peak_publisher_->msg_.header.stamp = time;
    for (std::size_t index = 0; index < kJointCount; ++index) {
      auto & values = peak_publisher_->msg_.interface_values[index].values;
      const auto & peak = peak_samples_[index];
      for (std::size_t axis = 0; axis < kJointCount; ++axis) {
        values[axis] = peak.position[axis];
      }
      values[6] = peak.velocity;
      values[7] = peak.acceleration;
      values[8] = peak.measured_torque;
      values[9] = peak.expected_torque;
      values[10] = peak.residual;
      values[11] = peak.threshold;
      peak_samples_[index] = PeakSample{};
    }
    peak_publisher_->unlockAndPublish();
  }
  if (publish_timing_this_cycle_ && timing_publisher_ && timing_publisher_->trylock()) {
    std::array<char, 256> payload{};
    const int length = std::snprintf(
      payload.data(), payload.size(),
      "{\"updates\":%llu,\"overruns\":%llu,\"last_update_us\":%.3f,"
      "\"max_update_us\":%.3f,\"observer_ready\":%s,\"observer\":\"cpp_realtime\"}",
      static_cast<unsigned long long>(update_count_),
      static_cast<unsigned long long>(overrun_count_), elapsed.count() / 1000.0,
      max_update_time_.count() / 1000.0, observer_ready_ ? "true" : "false");
    if (length > 0) {
      timing_publisher_->msg_.data.assign(
        payload.data(), static_cast<std::size_t>(length));
    }
    timing_publisher_->unlockAndPublish();
  }
}

}  // namespace zeroerr

PLUGINLIB_EXPORT_CLASS(
  zeroerr::RealtimeCollisionController, controller_interface::ControllerInterface)
