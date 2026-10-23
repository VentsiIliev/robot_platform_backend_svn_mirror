#include "zeroerr/realtime_collision_controller.hpp"
#include "zeroerr/sensorless_configuration.hpp"

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
  config_path_ = auto_declare<std::string>("collision_config_path", "");
  if (config_path_.empty()) {
    config_path_ = sensorless_profile_path(ament_index_cpp::get_package_share_directory("zeroerr"));
  }
  const auto controller = load_sensorless_config(config_path_)["controller"];
  joint_names_ = auto_declare<std::vector<std::string>>("joints", controller["joints"].as<std::vector<std::string>>());
  base_link_ = auto_declare<std::string>("base_link", controller["base_link"].as<std::string>());
  tip_link_ = auto_declare<std::string>("tip_link", controller["tip_link"].as<std::string>());
  observer_gain_ = auto_declare<double>("observer_gain", controller["observer_gain"].as<double>());
  filter_alpha_ = auto_declare<double>("filter_alpha", controller["filter_alpha"].as<double>());
  acceleration_filter_cutoff_hz_ = auto_declare<double>("acceleration_filter_cutoff_hz", controller["acceleration_filter_cutoff_hz"].as<double>());
  plot_period_sec_ = auto_declare<double>("plot_period_sec", controller["plot_period_sec"].as<double>());
  timing_period_sec_ = auto_declare<double>("timing_period_sec", controller["timing_period_sec"].as<double>());
  warmup_sec_ = auto_declare<double>("warmup_sec", controller["warmup_sec"].as<double>());
  rearm_settle_sec_ = auto_declare<double>("rearm_settle_sec", controller["rearm_settle_sec"].as<double>());
  drive_stable_sec_ = auto_declare<double>("drive_stable_sec", controller["drive_stable_sec"].as<double>());
  warmup_velocity_limit_ = auto_declare<double>("warmup_velocity_limit", controller["warmup_velocity_limit"].as<double>());
  rearm_settle_sec_ = std::max(0.1, rearm_settle_sec_);
  warmup_min_samples_ = static_cast<std::size_t>(std::max<std::int64_t>(1,
    auto_declare<std::int64_t>("warmup_min_samples", controller["warmup_min_samples"].as<std::int64_t>())));
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
  stop_publisher_->msg_.data.reserve(256);
  collision_diagnostic_timer_ = node->create_wall_timer(
    std::chrono::milliseconds(20),
    std::bind(&RealtimeCollisionController::drain_collision_diagnostics, this));
  state_publisher_->msg_.joint_names = joint_names_;
  state_publisher_->msg_.interface_values.resize(kJointCount);
  for (auto & interfaces : state_publisher_->msg_.interface_values) {
    interfaces.interface_names = {
      "observer_ready", "baseline_valid", "observer_initialized", "acknowledgement_count",
      "rearm_settled_sec", "filtered_residual_nm", "release_limit_nm",
      "velocity_rad_s", "drives_stable_sec",
      "position", "velocity", "acceleration", "torque_sensor", "measured_torque",
      "expected_torque", "observer_auxiliary_torque", "external_torque"};
    interfaces.values.resize(17);
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
    auto config = sensorless_json(load_sensorless_config(config_path_)["monitor"]);
    config["effort_following_error_detection_enabled"] = false;
    non_rt_config_.detection_enabled = config.at("detection_enabled").get<bool>();
    non_rt_config_.active_stop_enabled = config.at("active_stop_enabled").get<bool>();
    non_rt_config_.diagnostics_enabled = config.at("diagnostics_enabled").get<bool>();
    non_rt_config_.dynamic_threshold_enabled = config.at("dynamic_threshold_enabled").get<bool>();
    non_rt_config_.detection_suppressed = config.at("collision_detection_suppressed").get<bool>();
    non_rt_config_.confirm_duration_sec =
      std::max(0.0, config.at("confirm_duration_ms").get<double>()) * 1.0e-3;
    non_rt_config_.sensitivity_percent =
      std::clamp(config.at("collision_sensitivity_percent").get<double>(), 50.0, 200.0);
    non_rt_config_.threshold_max_ratio =
      std::clamp(config.at("dynamic_threshold_max_ratio").get<double>(), 1.0, 20.0);
    non_rt_config_.threshold_decay_sec =
      std::max(0.01, config.at("dynamic_threshold_decay_sec").get<double>());
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
      0.0, config.at("friction_velocity_deadband_rad_s").get<double>());
    friction_transition_velocity_ = std::max(
      1.0e-5, config.at("friction_transition_velocity_rad_s").get<double>());
    friction_stribeck_velocity_ = std::max(
      friction_transition_velocity_, config.at("friction_stribeck_velocity_rad_s").get<double>());
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
    next.detection_enabled = state.at("detection_enabled").get<bool>();
    next.active_stop_enabled = state.at("active_stop_enabled").get<bool>();
    next.diagnostics_enabled = state.at("diagnostics_enabled").get<bool>();
    next.dynamic_threshold_enabled = state.at("dynamic_threshold_enabled").get<bool>();
    next.detection_suppressed = state.at("collision_detection_suppressed").get<bool>();
    next.confirm_duration_sec =
      std::max(0.0, state.at("confirm_duration_ms").get<double>()) * 1.0e-3;
    next.sensitivity_percent = std::clamp(
      state.at("collision_sensitivity_percent").get<double>(), 50.0, 200.0);
    next.threshold_max_ratio = std::clamp(
      state.at("dynamic_threshold_max_ratio").get<double>(), 1.0, 20.0);
    next.threshold_decay_sec = std::max(
      0.01, state.at("dynamic_threshold_decay_sec").get<double>());
    load_joint_array(state, "external_torque_thresholds", next.static_floor);
    // Normalize persisted/live fields to the values actually applied by the controller.
    state["confirm_duration_ms"] = next.confirm_duration_sec * 1000.0;
    state["collision_sensitivity_percent"] = next.sensitivity_percent;
    state["dynamic_threshold_max_ratio"] = next.threshold_max_ratio;
    state["dynamic_threshold_decay_sec"] = next.threshold_decay_sec;
    // Persistence belongs to the backend configuration application, never the controller.
    non_rt_config_ = next;
    config_state_json_ = state.dump();
    runtime_config_.writeFromNonRT(non_rt_config_);
    publish_config_state(non_rt_config_);
  } catch (const std::exception & error) {
    RCLCPP_ERROR(get_node()->get_logger(), "Rejected collision config update: %s", error.what());
  }
}

void RealtimeCollisionController::acknowledge_collision(
  const std_msgs::msg::String::SharedPtr message)
{
  bool recalibrate = false;
  try {
    const auto request = nlohmann::json::parse(message->data);
    if (!request.is_object()) {throw std::runtime_error("acknowledgement must be an object");}
    recalibrate = request.value("recalibrate", false);
  } catch (const std::exception & error) {
    RCLCPP_ERROR(get_node()->get_logger(), "Invalid observer acknowledgement: %s", error.what());
    return;
  }
  RCLCPP_WARN(
    get_node()->get_logger(),
    "[CollisionObserverReset] acknowledgement received; mode=%s "
    "warmup_sec=%.3f drive_stable_sec=%.3f observer_gain=%.3f filter_alpha=%.3f",
    recalibrate ? "full_calibration" : "retained_baseline",
    warmup_sec_, drive_stable_sec_, observer_gain_, filter_alpha_);
  // Coalesced requests must never downgrade an explicit recalibration.
  reset_requested_.fetch_or(recalibrate ? 3U : 1U, std::memory_order_release);
}

void RealtimeCollisionController::publish_config_state(const RuntimeConfig &)
{
  if (!config_state_publisher_) {
    return;
  }
  std_msgs::msg::String message;
  auto state = nlohmann::json::parse(config_state_json_);
  state["_controller"] = {
    {"joints", joint_names_}, {"base_link", base_link_}, {"tip_link", tip_link_},
    {"observer_gain", observer_gain_}, {"filter_alpha", filter_alpha_},
    {"acceleration_filter_cutoff_hz", acceleration_filter_cutoff_hz_},
    {"plot_period_sec", plot_period_sec_}, {"timing_period_sec", timing_period_sec_},
    {"warmup_sec", warmup_sec_}, {"rearm_settle_sec", rearm_settle_sec_},
    {"drive_stable_sec", drive_stable_sec_}, {"warmup_velocity_limit", warmup_velocity_limit_},
    {"warmup_min_samples", warmup_min_samples_}
  };
  message.data = state.dump();
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

  observer_auxiliary_torque_ = auxiliary;
  if (!observer_initialized_) {
    if (!recovery_.calibrate(
        measured, auxiliary, velocity, dt_sec, warmup_sec_, warmup_min_samples_,
        warmup_velocity_limit_))
    {
      return true;
    }
    // A valid baseline is retained across rearm. Refresh only the dynamic state
    // from the current momentum; residuals must then settle before motion release.
    momentum_integral_ = momentum;
    observer_initialized_ = true;
    return true;
  }

  for (std::size_t index = 0; index < kJointCount; ++index) {
    momentum_integral_[index] +=
      (measured[index] - recovery_.baseline_offset[index] - auxiliary[index] - residual_[index]) * dt_sec;
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
  training_sample_valid_ = false;
  const double dt_sec = std::max(period.seconds(), 1.0e-6);
  timing_elapsed_sec_ += dt_sec;
  publish_timing_this_cycle_ = timing_elapsed_sec_ >= timing_period_sec_;
  if (publish_timing_this_cycle_) {timing_elapsed_sec_ = 0.0;}
  const unsigned int reset_request = reset_requested_.exchange(0U, std::memory_order_acq_rel);
  if (reset_request != 0U) {
    ++acknowledgement_count_;
    rearm_observer((reset_request & 2U) != 0U);
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
    rearm_observer();
    publish_diagnostics(
      time, std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::steady_clock::now() - started), false);
    return controller_interface::return_type::OK;
  }
  if (!drives_operational) {
    rearm_observer();
    publish_diagnostics(
      time, std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::steady_clock::now() - started), false);
    return controller_interface::return_type::OK;
  }
  drives_operational_elapsed_sec_ += dt_sec;
  if (drives_operational_elapsed_sec_ < drive_stable_sec_) {
    publish_diagnostics(
      time, std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::steady_clock::now() - started), false);
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
    friction_correction_[index] = friction;
    position_correction_[index] = position_correction;
    motion_correction_[index] = motion_correction;
    compensated_torque[index] -= friction + position_correction + motion_correction;
  }
  const bool was_observer_ready = observer_ready_;
  if (!update_observer(position, velocity, acceleration, compensated_torque, dt_sec)) {
    reset_observer();
    publish_diagnostics(
      time, std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::steady_clock::now() - started), false);
    return controller_interface::return_type::OK;
  }

  sample_position_ = position;
  sample_torque_ = torque;
  training_sample_valid_ = observer_initialized_;
  if (observer_initialized_) {
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

  if (observer_initialized_ && !observer_ready_) {
    observer_ready_ = recovery_.ready_to_release(
      filtered_residual_, threshold_, velocity, dt_sec, rearm_settle_sec_,
      warmup_velocity_limit_);
  }
  if (observer_ready_) {
    observer_ready_age_sec_ += was_observer_ready ? dt_sec : 0.0;
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
      const auto event_id = ++collision_event_sequence_;
      bool stop_published = false;
      if (config.active_stop_enabled && stop_publisher_ && stop_publisher_->trylock()) {
        std::array<char, 256> payload{};
        const int length = std::snprintf(
          payload.data(), payload.size(), "%.*s,\"diagnostic_event_id\":%llu}",
          static_cast<int>(stop_payloads_[first_exceeded].size() - 1),
          stop_payloads_[first_exceeded].c_str(), static_cast<unsigned long long>(event_id));
        if (length > 0 && static_cast<std::size_t>(length) < payload.size()) {
          stop_publisher_->msg_.data.assign(payload.data(), static_cast<std::size_t>(length));
        } else {
          stop_publisher_->msg_.data = stop_payloads_[first_exceeded];
        }
        stop_publisher_->unlockAndPublish();
        stop_published = true;
      }
      // The stop publication stays first. Diagnostics use only bounded POD copies here.
      capture_collision_diagnostics(
        time, dt_sec, config, position, velocity, acceleration, torque,
        compensated_torque, static_cast<int>(first_exceeded), event_id,
        config.active_stop_enabled, stop_published);
    }
  } else {
    exceedance_sec_.fill(0.0);
  }

  if (observer_ready_ && !was_observer_ready) {
    capture_collision_diagnostics(
      time, dt_sec, config, position, velocity, acceleration, torque,
      compensated_torque, -1, ++collision_event_sequence_, false, false);
  }
  if (observer_ready_) {
    collision_history_elapsed_sec_ += dt_sec;
    if (collision_history_elapsed_sec_ >= 0.01) {
      collision_history_elapsed_sec_ = 0.0;
      collision_history_[collision_history_next_] = {time.nanoseconds(), filtered_residual_, threshold_};
      collision_history_next_ = (collision_history_next_ + 1) % collision_history_.size();
      collision_history_count_ = std::min(collision_history_count_ + 1, collision_history_.size());
    }
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
  if (config.diagnostics_enabled && diagnostics_elapsed_sec_ >= plot_period_sec_) {
    diagnostics_elapsed_sec_ = 0.0;
    publish_diagnostics(time, elapsed_ns, true);
  } else if (publish_timing_this_cycle_) {
    publish_diagnostics(time, elapsed_ns, false);
  }
  return controller_interface::return_type::OK;
}

void RealtimeCollisionController::capture_collision_diagnostics(
  const rclcpp::Time & time, const double dt_sec, const RuntimeConfig & config,
  const JointVector & position, const JointVector & velocity,
  const JointVector & acceleration, const JointVector & torque,
  const JointVector & compensated_torque, const int triggered_joint,
  const std::uint64_t event_id, const bool stop_attempted, const bool stop_published)
{
  CollisionEventSnapshot event;
  event.event_id = event_id;
  event.observer_resets = observer_reset_count_;
  event.acknowledgements = acknowledgement_count_;
  event.updates = update_count_;
  event.overruns = overrun_count_;
  event.ros_time_ns = time.nanoseconds();
  event.triggered_joint = triggered_joint;
  event.observer_ready = observer_ready_;
  event.baseline_valid = recovery_.baseline_valid;
  event.observer_initialized = observer_initialized_;
  event.rearm_settled_sec = recovery_.settled_sec;
  event.detection_enabled = config.detection_enabled;
  event.detection_suppressed = config.detection_suppressed;
  event.active_stop_enabled = config.active_stop_enabled;
  event.dynamic_threshold_enabled = config.dynamic_threshold_enabled;
  event.stop_publish_attempted = stop_attempted;
  event.stop_published = stop_published;
  event.dt_sec = dt_sec;
  event.observer_ready_age_sec = observer_ready_age_sec_;
  event.warmup_elapsed_sec = recovery_.warmup_elapsed_sec;
  event.warmup_samples = recovery_.warmup_samples;
  event.confirm_duration_sec = config.confirm_duration_sec;
  event.sensitivity_percent = config.sensitivity_percent;
  event.threshold_max_ratio = config.threshold_max_ratio;
  event.threshold_decay_sec = config.threshold_decay_sec;
  event.position = position;
  event.velocity = velocity;
  event.acceleration = acceleration;
  event.measured_torque = torque;
  event.compensated_torque = compensated_torque;
  event.expected_torque = expected_torque_;
  event.friction_correction = friction_correction_;
  event.position_correction = position_correction_;
  event.motion_correction = motion_correction_;
  event.baseline_offset = recovery_.baseline_offset;
  event.raw_residual = residual_;
  event.filtered_residual = filtered_residual_;
  event.threshold = threshold_;
  event.static_floor = config.static_floor;
  event.exceedance_sec = exceedance_sec_;
  event.velocity_envelope_positive = threshold_envelope_velocity_positive_;
  event.velocity_envelope_negative = threshold_envelope_velocity_negative_;
  event.acceleration_envelope_positive = threshold_envelope_acceleration_positive_;
  event.acceleration_envelope_negative = threshold_envelope_acceleration_negative_;
  event.history = collision_history_;
  event.history_count = collision_history_count_;
  event.history_next = collision_history_next_;
  collision_diagnostic_queue_.try_push(event);
}

void RealtimeCollisionController::drain_collision_diagnostics()
{
  CollisionEventSnapshot event;
  while (collision_diagnostic_queue_.try_pop(event)) {
    try {
      auto payload = collision_event_json(event, joint_names_, collision_diagnostic_queue_.dropped());
      payload["observer_gain"] = observer_gain_;
      payload["filter_alpha"] = filter_alpha_;
      payload["acceleration_filter_cutoff_hz"] = acceleration_filter_cutoff_hz_;
      payload["warmup_required_sec"] = warmup_sec_;
      payload["drive_stable_required_sec"] = drive_stable_sec_;
      payload["rearm_settle_required_sec"] = rearm_settle_sec_;
      RCLCPP_WARN(get_node()->get_logger(), "[CollisionDiagnostics] %s", payload.dump().c_str());
    } catch (const std::exception & error) {
      RCLCPP_ERROR(get_node()->get_logger(), "Collision diagnostic serialization failed: %s", error.what());
    }
  }
}

void RealtimeCollisionController::reset_observer()
{
  rearm_observer(true);
}

void RealtimeCollisionController::rearm_observer(const bool recalibrate)
{
  recovery_.acknowledge(recalibrate);
  if (have_previous_sample_ || observer_ready_) {++observer_reset_count_;}
  observer_ready_age_sec_ = 0.0;
  collision_history_count_ = 0;
  collision_history_next_ = 0;
  collision_history_elapsed_sec_ = 0.0;
  previous_velocity_.fill(0.0);
  filtered_acceleration_.fill(0.0);
  momentum_integral_.fill(0.0);
  residual_.fill(0.0);
  filtered_residual_.fill(0.0);
  exceedance_sec_.fill(0.0);
  threshold_envelope_velocity_positive_.fill(0.0);
  threshold_envelope_velocity_negative_.fill(0.0);
  threshold_envelope_acceleration_positive_.fill(0.0);
  threshold_envelope_acceleration_negative_.fill(0.0);
  have_previous_sample_ = false;
  observer_ready_ = false;
  observer_initialized_ = false;
  stop_latched_ = false;
  drives_operational_elapsed_sec_ = 0.0;
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
  // Keep timestamps flowing while initialization/drive stabilization prevents
  // observer updates. NaN denotes unavailable torque, rather than letting the
  // plot interpolate a two-second ramp from the old residual to reset zero.
  if (publish_plot || (publish_timing_this_cycle_ && !observer_initialized_)) {
    publish_joint_values(
      residual_publisher_, observer_residual_for_plot(filtered_residual_, observer_initialized_));
    publish_joint_values(threshold_publisher_, threshold_);
  }
  if (publish_timing_this_cycle_ && state_publisher_ && state_publisher_->trylock()) {
    state_publisher_->msg_.header.stamp = time;
    for (std::size_t i = 0; i < kJointCount; ++i) {
      auto & interfaces = state_publisher_->msg_.interface_values[i];
      interfaces.values[0] = observer_ready_ ? 1.0 : 0.0;
      interfaces.values[1] = recovery_.baseline_valid ? 1.0 : 0.0;
      interfaces.values[2] = observer_initialized_ ? 1.0 : 0.0;
      interfaces.values[3] = static_cast<double>(acknowledgement_count_);
      interfaces.values[4] = recovery_.settled_sec;
      interfaces.values[5] = filtered_residual_[i];
      interfaces.values[6] = threshold_[i];
      interfaces.values[7] = previous_velocity_[i];
      interfaces.values[8] = drives_operational_elapsed_sec_;
      // Regular current-cycle samples, independent of peak selection. Never
      // expose a previous cycle as valid after a drive/input/observer failure.
      const bool valid = training_sample_valid_ && observer_ready_;
      const double unavailable = std::numeric_limits<double>::quiet_NaN();
      interfaces.values[9] = valid ? sample_position_[i] : unavailable;
      interfaces.values[10] = valid ? previous_velocity_[i] : unavailable;
      interfaces.values[11] = valid ? filtered_acceleration_[i] : unavailable;
      interfaces.values[12] = valid ? sample_torque_[i] : unavailable;
      interfaces.values[13] = valid ? sample_torque_[i] : unavailable;
      interfaces.values[14] = valid ? expected_torque_[i] : unavailable;
      interfaces.values[15] = valid ? observer_auxiliary_torque_[i] : unavailable;
      interfaces.values[16] = valid ? filtered_residual_[i] : unavailable;
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
