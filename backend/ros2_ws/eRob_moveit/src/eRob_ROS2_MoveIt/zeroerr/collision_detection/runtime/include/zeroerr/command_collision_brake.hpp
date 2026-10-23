#pragma once

#include <array>
#include <algorithm>
#include <cmath>
#include <ruckig/ruckig.hpp>

namespace zeroerr
{
// ROS-independent, fixed-storage generator. Called once at collision takeover,
// never at the Python callback's older measured-state timestamp.
class CommandCollisionBrake
{
public:
  static constexpr size_t axes = 6;
  static constexpr size_t points = 1201;
  using Vector = std::array<double, axes>;
  struct Sample {double time; Vector position, velocity, acceleration;};
  struct Limits {Vector velocity, acceleration, jerk, lower, upper;};

  bool calculate(const Vector & q, const Vector & v, const Vector & a,
    const Vector & measured, const Limits & limits, double max_duration,
    double max_travel, double max_tracking_error)
  {
    ruckig::InputParameter<axes> input;
    input.control_interface = ruckig::ControlInterface::Velocity;
    input.synchronization = ruckig::Synchronization::Time;
    for (size_t i = 0; i < axes; ++i) {
      if (!std::isfinite(q[i]) || !std::isfinite(v[i]) || !std::isfinite(a[i]) ||
        !std::isfinite(measured[i]) || !std::isfinite(limits.velocity[i]) ||
        !std::isfinite(limits.acceleration[i]) || !std::isfinite(limits.jerk[i]) ||
        limits.velocity[i] <= 0 || limits.acceleration[i] <= 0 || limits.jerk[i] <= 0 ||
        std::isnan(limits.lower[i]) || std::isnan(limits.upper[i]) ||
        limits.lower[i] >= limits.upper[i] ||
        std::abs(q[i] - measured[i]) > max_tracking_error) {return false;}
    }
    if (!std::isfinite(max_duration) || max_duration <= 0 || max_duration > .6 ||
      !std::isfinite(max_travel) || max_travel <= 0 ||
      !std::isfinite(max_tracking_error) || max_tracking_error <= 0) {return false;}
    input.current_position = q;
    input.current_velocity = v;
    input.current_acceleration = a;
    input.target_position = q;
    input.target_velocity.fill(0.0);
    input.target_acceleration.fill(0.0);
    input.max_velocity = limits.velocity;
    input.max_acceleration = limits.acceleration;
    input.max_jerk = limits.jerk;
    try {
      if (generator_.calculate(input, trajectory_) < 0) {return false;}
    } catch (...) {return false;}
    duration_ = std::max(.0005, trajectory_.get_duration());
    if (!std::isfinite(duration_) || duration_ > max_duration) {return false;}
    // Fixed storage and <= 0.5 ms spacing. Conservatively enclose each interval
    // using its initial velocity and the acceleration bound, including recovery
    // from a pre-existing acceleration above the configured limit.
    const double dt = duration_ / (points - 1);
    for (size_t row = 0; row < points; ++row) {
      auto & out = samples_[row];
      out.time = row == points - 1 ? duration_ : row * dt;
      trajectory_.at_time(out.time, out.position, out.velocity, out.acceleration);
      for (size_t i = 0; i < axes; ++i) {
        const double margin = row == points - 1 ? 0.0 :
          std::abs(out.velocity[i]) * dt + .5 * std::max(
          std::abs(a[i]), limits.acceleration[i]) * dt * dt;
        if (!std::isfinite(out.position[i]) || !std::isfinite(out.velocity[i]) ||
          !std::isfinite(out.acceleration[i]) ||
          out.position[i] - margin < limits.lower[i] ||
          out.position[i] + margin > limits.upper[i] ||
          std::abs(out.position[i] - measured[i]) + margin > max_travel ||
          std::abs(out.velocity[i]) > limits.velocity[i] + 1e-8) {return false;}
      }
    }
    return true;
  }
  const std::array<Sample, points> & samples() const {return samples_;}
  double duration() const {return duration_;}
private:
  ruckig::Ruckig<axes> generator_;
  ruckig::Trajectory<axes> trajectory_;
  std::array<Sample, points> samples_{};
  double duration_{0.0};
};
}  // namespace zeroerr
