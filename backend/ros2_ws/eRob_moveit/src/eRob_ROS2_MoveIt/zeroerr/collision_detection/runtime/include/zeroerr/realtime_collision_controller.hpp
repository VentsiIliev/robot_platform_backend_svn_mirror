#pragma once

#include <array>
#include <atomic>
#include <chrono>
#include <memory>
#include <string>
#include <vector>

#include <controller_interface/controller_interface.hpp>
#include <control_msgs/msg/dynamic_joint_state.hpp>
#include <kdl/chaindynparam.hpp>
#include <kdl/chainidsolver_recursive_newton_euler.hpp>
#include <kdl/jntarray.hpp>
#include <kdl/jntspaceinertiamatrix.hpp>
#include <realtime_tools/realtime_publisher.hpp>
#include <realtime_tools/realtime_buffer.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <std_msgs/msg/string.hpp>
#include "zeroerr/collision_event_diagnostics.hpp"
#include "zeroerr/collision_observer_recovery.hpp"

namespace zeroerr
{

class RealtimeCollisionController final : public controller_interface::ControllerInterface
{
public:
  controller_interface::CallbackReturn on_init() override;
  controller_interface::InterfaceConfiguration command_interface_configuration() const override;
  controller_interface::InterfaceConfiguration state_interface_configuration() const override;
  controller_interface::CallbackReturn on_configure(
    const rclcpp_lifecycle::State & previous_state) override;
  controller_interface::CallbackReturn on_activate(
    const rclcpp_lifecycle::State & previous_state) override;
  controller_interface::CallbackReturn on_deactivate(
    const rclcpp_lifecycle::State & previous_state) override;
  controller_interface::return_type update(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

private:
  static constexpr std::size_t kJointCount = 6;
  using JointVector = std::array<double, kJointCount>;
  using ThresholdCoefficients = std::array<double, 9>;
  using MotionCoefficients = std::array<double, 6>;

  struct RuntimeConfig
  {
    bool detection_enabled{true};
    bool active_stop_enabled{false};
    bool diagnostics_enabled{true};
    bool dynamic_threshold_enabled{true};
    bool detection_suppressed{false};
    double sensitivity_percent{100.0};
    double confirm_duration_sec{0.025};
    double threshold_max_ratio{3.5};
    double threshold_decay_sec{0.35};
    JointVector static_floor{};
  };

  bool load_model();
  bool load_config();
  void apply_config_message(const std_msgs::msg::String::SharedPtr message);
  void acknowledge_collision(const std_msgs::msg::String::SharedPtr message);
  void publish_config_state(const RuntimeConfig & config);
  bool read_inputs(
    JointVector & position, JointVector & velocity, JointVector & torque,
    bool & drives_operational);
  bool update_observer(
    const JointVector & position, const JointVector & velocity,
    const JointVector & acceleration, const JointVector & measured,
    double dt_sec);
  double dynamic_threshold(
    std::size_t index, double velocity, double acceleration, double dt_sec,
    const RuntimeConfig & config);
  void reset_observer();
  void rearm_observer(bool recalibrate = false);
  void capture_collision_diagnostics(
    const rclcpp::Time & time, double dt_sec, const RuntimeConfig & config,
    const JointVector & position, const JointVector & velocity,
    const JointVector & acceleration, const JointVector & torque,
    const JointVector & compensated_torque, int triggered_joint,
    std::uint64_t event_id, bool stop_attempted, bool stop_published);
  void drain_collision_diagnostics();
  void publish_diagnostics(
    const rclcpp::Time & time, std::chrono::nanoseconds elapsed, bool publish_plot);

  std::vector<std::string> joint_names_;
  std::string base_link_;
  std::string tip_link_;
  std::string config_path_;
  double observer_gain_{10.0};
  double filter_alpha_{0.7};
  double plot_period_sec_{0.0005};
  double timing_period_sec_{0.01};
  double warmup_sec_{8.0};
  double rearm_settle_sec_{0.5};
  double drive_stable_sec_{2.0};
  double warmup_velocity_limit_{0.02};
  std::size_t warmup_min_samples_{20};

  KDL::Chain chain_;
  std::unique_ptr<KDL::ChainDynParam> dynamics_;
  std::unique_ptr<KDL::ChainIdSolver_RNE> inverse_dynamics_;
  KDL::JntArray q_{kJointCount};
  KDL::JntArray dq_{kJointCount};
  KDL::JntArray ddq_{kJointCount};
  KDL::JntArray gravity_{kJointCount};
  KDL::JntArray expected_kdl_{kJointCount};
  KDL::JntSpaceInertiaMatrix mass_{kJointCount};
  KDL::JntSpaceInertiaMatrix mass_plus_{kJointCount};
  KDL::JntSpaceInertiaMatrix mass_minus_{kJointCount};
  std::vector<KDL::Wrench> external_wrenches_;

  JointVector previous_velocity_{};
  JointVector filtered_acceleration_{};
  JointVector momentum_integral_{};
  JointVector residual_{};
  JointVector filtered_residual_{};
  JointVector expected_torque_{};
  JointVector observer_auxiliary_torque_{};
  JointVector sample_position_{};
  JointVector sample_torque_{};
  bool training_sample_valid_{false};
  JointVector friction_correction_{};
  JointVector position_correction_{};
  JointVector motion_correction_{};
  CollisionObserverRecovery recovery_;
  JointVector static_floor_{};
  JointVector threshold_{};
  JointVector threshold_envelope_velocity_positive_{};
  JointVector threshold_envelope_velocity_negative_{};
  JointVector threshold_envelope_acceleration_positive_{};
  JointVector threshold_envelope_acceleration_negative_{};
  JointVector training_velocity_limit_{};
  JointVector training_acceleration_limit_{};
  JointVector exceedance_sec_{};
  JointVector friction_coulomb_{};
  JointVector friction_viscous_{};
  JointVector friction_coulomb_positive_{};
  JointVector friction_coulomb_negative_{};
  JointVector friction_static_positive_{};
  JointVector friction_static_negative_{};
  JointVector motion_velocity_limit_{};
  JointVector motion_acceleration_limit_{};
  std::array<ThresholdCoefficients, kJointCount> threshold_coefficients_{};
  std::array<ThresholdCoefficients, kJointCount> position_coefficients_{};
  std::array<MotionCoefficients, kJointCount> motion_coefficients_{};
  double friction_deadband_{0.01};
  double friction_transition_velocity_{0.01};
  double friction_stribeck_velocity_{0.05};
  double acceleration_filter_cutoff_hz_{40.0};

  struct PeakSample
  {
    double absolute_residual{-1.0};
    double velocity{0.0};
    double acceleration{0.0};
    double measured_torque{0.0};
    double expected_torque{0.0};
    double residual{0.0};
    double threshold{0.0};
    JointVector position{};
  };
  std::array<PeakSample, kJointCount> peak_samples_{};

  CollisionDiagnosticQueue<CollisionEventSnapshot, 16> collision_diagnostic_queue_;
  std::array<CollisionTraceSample, 25> collision_history_{};
  std::size_t collision_history_count_{0};
  std::size_t collision_history_next_{0};
  double collision_history_elapsed_sec_{0.0};
  double observer_ready_age_sec_{0.0};
  std::uint64_t collision_event_sequence_{0};
  std::uint64_t observer_reset_count_{0};
  std::uint64_t acknowledgement_count_{0};
  bool have_previous_sample_{false};
  bool observer_ready_{false};
  bool observer_initialized_{false};
  bool stop_latched_{false};
  double drives_operational_elapsed_sec_{0.0};
  double diagnostics_elapsed_sec_{0.0};
  double timing_elapsed_sec_{0.0};
  std::uint64_t update_count_{0};
  std::uint64_t overrun_count_{0};
  std::chrono::nanoseconds max_update_time_{0};

  std::shared_ptr<realtime_tools::RealtimePublisher<sensor_msgs::msg::JointState>>
    residual_publisher_;
  std::shared_ptr<realtime_tools::RealtimePublisher<sensor_msgs::msg::JointState>>
    threshold_publisher_;
  std::shared_ptr<realtime_tools::RealtimePublisher<std_msgs::msg::String>>
    timing_publisher_;
  std::shared_ptr<realtime_tools::RealtimePublisher<std_msgs::msg::String>>
    stop_publisher_;
  std::shared_ptr<realtime_tools::RealtimePublisher<control_msgs::msg::DynamicJointState>>
    state_publisher_;
  std::shared_ptr<realtime_tools::RealtimePublisher<control_msgs::msg::DynamicJointState>>
    peak_publisher_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr config_state_publisher_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr config_subscription_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr acknowledgement_subscription_;
  rclcpp::TimerBase::SharedPtr config_state_timer_;
  rclcpp::TimerBase::SharedPtr collision_diagnostic_timer_;
  realtime_tools::RealtimeBuffer<RuntimeConfig> runtime_config_;
  RuntimeConfig non_rt_config_{};
  std::string config_state_json_;
  bool publish_timing_this_cycle_{false};
  std::atomic<unsigned int> reset_requested_{0U};
  std::array<std::string, kJointCount> stop_payloads_{};
};

}  // namespace zeroerr
