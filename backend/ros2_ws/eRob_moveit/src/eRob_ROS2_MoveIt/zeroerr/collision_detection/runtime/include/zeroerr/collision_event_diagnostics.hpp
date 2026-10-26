#pragma once

#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <type_traits>
#include <vector>
#include <string>

#include <nlohmann/json.hpp>

namespace zeroerr
{
using CollisionJointValues = std::array<double, 6>;

inline CollisionJointValues observer_residual_for_plot(
  const CollisionJointValues & residual, bool initialized)
{
  if (initialized) {return residual;}
  CollisionJointValues unavailable;
  unavailable.fill(std::numeric_limits<double>::quiet_NaN());
  return unavailable;
}

struct CollisionTraceSample
{
  std::int64_t ros_time_ns{0};
  CollisionJointValues residual{};
  CollisionJointValues threshold{};
};

struct CollisionEventSnapshot
{
  std::uint64_t event_id{0};
  std::uint64_t observer_resets{0};
  std::uint64_t acknowledgements{0};
  std::uint64_t updates{0};
  std::uint64_t overruns{0};
  std::int64_t ros_time_ns{0};
  int triggered_joint{-1};  // -1 is an observer-ready transition, not a collision.
  bool observer_ready{false};
  bool baseline_valid{false};
  bool observer_initialized{false};
  double rearm_settled_sec{0.0};
  bool detection_enabled{false};
  bool detection_suppressed{false};
  bool active_stop_enabled{false};
  bool dynamic_threshold_enabled{false};
  bool stop_publish_attempted{false};
  bool stop_published{false};
  bool stop_publication_update{false};
  double dt_sec{0.0};
  double observer_ready_age_sec{0.0};
  double warmup_elapsed_sec{0.0};
  std::size_t warmup_samples{0};
  double confirm_duration_sec{0.0};
  double sensitivity_percent{0.0};
  double threshold_max_ratio{0.0};
  double threshold_decay_sec{0.0};
  CollisionJointValues position{};
  CollisionJointValues velocity{};
  CollisionJointValues acceleration{};
  CollisionJointValues measured_torque{};
  CollisionJointValues compensated_torque{};
  CollisionJointValues expected_torque{};
  CollisionJointValues friction_correction{};
  CollisionJointValues position_correction{};
  CollisionJointValues motion_correction{};
  CollisionJointValues baseline_offset{};
  CollisionJointValues raw_residual{};
  CollisionJointValues filtered_residual{};
  CollisionJointValues threshold{};
  CollisionJointValues static_floor{};
  CollisionJointValues exceedance_sec{};
  CollisionJointValues velocity_envelope_positive{};
  CollisionJointValues velocity_envelope_negative{};
  CollisionJointValues acceleration_envelope_positive{};
  CollisionJointValues acceleration_envelope_negative{};
  std::array<CollisionTraceSample, 25> history{};
  std::size_t history_count{0};
  std::size_t history_next{0};
};

// One producer (controller update), one consumer (non-RT diagnostic timer).
// A full queue drops diagnostics only; it never waits or affects the stop path.
template<typename T, std::size_t Capacity>
class CollisionDiagnosticQueue
{
  static_assert(Capacity > 1);
  static_assert(std::atomic<std::size_t>::is_always_lock_free);
  static_assert(std::atomic<std::uint64_t>::is_always_lock_free);
  static_assert(std::is_trivially_copyable<T>::value);

public:
  bool try_push(const T & value) noexcept
  {
    const auto head = head_.load(std::memory_order_relaxed);
    const auto next = (head + 1) % Capacity;
    if (next == tail_.load(std::memory_order_acquire)) {
      dropped_.fetch_add(1, std::memory_order_relaxed);
      return false;
    }
    entries_[head] = value;
    head_.store(next, std::memory_order_release);
    return true;
  }

  bool try_pop(T & value) noexcept
  {
    const auto tail = tail_.load(std::memory_order_relaxed);
    if (tail == head_.load(std::memory_order_acquire)) {return false;}
    value = entries_[tail];
    tail_.store((tail + 1) % Capacity, std::memory_order_release);
    return true;
  }

  std::uint64_t dropped() const noexcept {return dropped_.load(std::memory_order_relaxed);}

private:
  std::array<T, Capacity> entries_{};
  std::atomic<std::size_t> head_{0};
  std::atomic<std::size_t> tail_{0};
  std::atomic<std::uint64_t> dropped_{0};
};

// Called only by the non-RT timer. No JSON allocation/formatting in update().
inline nlohmann::json collision_event_json(
  const CollisionEventSnapshot & event, const std::vector<std::string> & names,
  std::uint64_t dropped_events)
{
  nlohmann::json result{
    {"schema_version", 1}, {"event_id", event.event_id},
    {"event", event.triggered_joint < 0 ? "observer_ready" :
      event.stop_publication_update ? "collision_stop_published" : "collision_detected"},
    {"detected_at_ros_ns", event.ros_time_ns},
    {"observer_resets", event.observer_resets}, {"acknowledgements", event.acknowledgements},
    {"observer_ready", event.observer_ready},
    {"baseline_valid", event.baseline_valid},
    {"observer_initialized", event.observer_initialized},
    {"rearm_settled_ms", event.rearm_settled_sec * 1000.0},
    {"observer_ready_age_ms", event.observer_ready_age_sec * 1000.0},
    {"warmup_elapsed_ms", event.warmup_elapsed_sec * 1000.0},
    {"warmup_samples", event.warmup_samples},
    {"detection_enabled", event.detection_enabled},
    {"detection_suppressed", event.detection_suppressed},
    {"active_stop_enabled", event.active_stop_enabled},
    {"dynamic_threshold_enabled", event.dynamic_threshold_enabled},
    {"confirm_duration_ms", event.confirm_duration_sec * 1000.0},
    {"sensitivity_percent", event.sensitivity_percent},
    {"threshold_max_ratio", event.threshold_max_ratio},
    {"threshold_decay_sec", event.threshold_decay_sec},
    {"stop_publish_attempted", event.stop_publish_attempted},
    {"stop_published", event.stop_published},
    {"control_dt_ms", event.dt_sec * 1000.0},
    {"updates", event.updates}, {"overruns", event.overruns},
    {"dropped_diagnostic_events", dropped_events},
    {"joint_order", names}, {"joints", nlohmann::json::array()},
    {"pre_event_history", nlohmann::json::array()}};
  result["triggered_joint"] = event.triggered_joint < 0 ? nlohmann::json(nullptr) :
    nlohmann::json(names.at(static_cast<std::size_t>(event.triggered_joint)));
  for (std::size_t i = 0; i < 6; ++i) {
    result["joints"].push_back({
      {"joint", names.at(i)}, {"position_rad", event.position[i]},
      {"velocity_rad_s", event.velocity[i]}, {"acceleration_rad_s2", event.acceleration[i]},
      {"measured_torque_nm", event.measured_torque[i]},
      {"compensated_torque_nm", event.compensated_torque[i]},
      {"expected_torque_nm", event.expected_torque[i]},
      {"friction_correction_nm", event.friction_correction[i]},
      {"position_correction_nm", event.position_correction[i]},
      {"motion_correction_nm", event.motion_correction[i]},
      {"baseline_offset_nm", event.baseline_offset[i]},
      {"raw_residual_nm", event.raw_residual[i]},
      {"filtered_residual_nm", event.filtered_residual[i]},
      {"threshold_nm", event.threshold[i]}, {"static_floor_nm", event.static_floor[i]},
      {"exceedance_ms", event.exceedance_sec[i] * 1000.0},
      {"velocity_envelope_positive_rad_s", event.velocity_envelope_positive[i]},
      {"velocity_envelope_negative_rad_s", event.velocity_envelope_negative[i]},
      {"acceleration_envelope_positive_rad_s2", event.acceleration_envelope_positive[i]},
      {"acceleration_envelope_negative_rad_s2", event.acceleration_envelope_negative[i]}});
  }
  const auto start = event.history_count == event.history.size() ? event.history_next : 0;
  for (std::size_t i = 0; i < event.history_count; ++i) {
    const auto & sample = event.history[(start + i) % event.history.size()];
    result["pre_event_history"].push_back({
      {"age_ms", static_cast<double>(event.ros_time_ns - sample.ros_time_ns) / 1.0e6},
      {"residual_nm", sample.residual}, {"threshold_nm", sample.threshold}});
  }
  return result;
}
}  // namespace zeroerr
