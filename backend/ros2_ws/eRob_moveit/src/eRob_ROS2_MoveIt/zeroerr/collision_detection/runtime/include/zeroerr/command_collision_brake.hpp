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

  enum class Failure {
    none, joint_order, state_layout, invalid_state, invalid_limits, tracking_error,
    invalid_configuration, generator_error, generator_exception, invalid_duration,
    duration_limit, invalid_sample, lower_position_limit, upper_position_limit,
    travel_limit, velocity_limit
  };
  struct Rejection {
    Failure reason{Failure::none};
    int joint{-1}, sample{-1}, generator_result{0};
    double time{0.0}, value{0.0}, limit{0.0};
  };
  static const char * failure_name(Failure reason) noexcept
  {
    switch (reason) {
#define BRAKE_REASON(name) case Failure::name: return #name
      BRAKE_REASON(none); BRAKE_REASON(joint_order); BRAKE_REASON(state_layout);
      BRAKE_REASON(invalid_state); BRAKE_REASON(invalid_limits); BRAKE_REASON(tracking_error);
      BRAKE_REASON(invalid_configuration); BRAKE_REASON(generator_error);
      BRAKE_REASON(generator_exception); BRAKE_REASON(invalid_duration);
      BRAKE_REASON(duration_limit); BRAKE_REASON(invalid_sample);
      BRAKE_REASON(lower_position_limit); BRAKE_REASON(upper_position_limit);
      BRAKE_REASON(travel_limit); BRAKE_REASON(velocity_limit);
#undef BRAKE_REASON
    }
    return "unknown";
  }
  const Rejection & rejection() const noexcept {return rejection_;}

  bool calculate(const Vector & q, const Vector & v, const Vector & a,
    const Vector & measured, const Limits & limits, double max_duration,
    double max_travel, double max_tracking_error)
  {
    rejection_ = Rejection{};
    duration_ = 0.0;
    ruckig::InputParameter<axes> input;
    input.control_interface = ruckig::ControlInterface::Velocity;
    input.synchronization = ruckig::Synchronization::Time;
    for (size_t i = 0; i < axes; ++i) {
      if (!std::isfinite(q[i]) || !std::isfinite(v[i]) || !std::isfinite(a[i]) ||
        !std::isfinite(measured[i])) {return reject(Failure::invalid_state, i);}
      if (!std::isfinite(limits.velocity[i]) || !std::isfinite(limits.acceleration[i]) ||
        !std::isfinite(limits.jerk[i]) || limits.velocity[i] <= 0 ||
        limits.acceleration[i] <= 0 || limits.jerk[i] <= 0 ||
        std::isnan(limits.lower[i]) || std::isnan(limits.upper[i]) ||
        limits.lower[i] >= limits.upper[i]) {return reject(Failure::invalid_limits, i);}
      if (std::abs(q[i] - measured[i]) > max_tracking_error) {
        return reject(Failure::tracking_error, i, -1, 0.0,
          std::abs(q[i] - measured[i]), max_tracking_error);
      }
    }
    if (!std::isfinite(max_duration) || max_duration <= 0 || max_duration > .6 ||
      !std::isfinite(max_travel) || max_travel <= 0 ||
      !std::isfinite(max_tracking_error) || max_tracking_error <= 0) {return reject(Failure::invalid_configuration);}
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
      rejection_.generator_result = static_cast<int>(generator_.calculate(input, trajectory_));
      if (rejection_.generator_result < 0) {return reject(Failure::generator_error);}
    } catch (...) {return reject(Failure::generator_exception);}
    duration_ = std::max(.0005, trajectory_.get_duration());
    if (!std::isfinite(duration_)) {return reject(Failure::invalid_duration);}
    if (duration_ > max_duration) {
      return reject(Failure::duration_limit, -1, -1, 0.0, duration_, max_duration);
    }
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
          !std::isfinite(out.acceleration[i])) {
          return reject(Failure::invalid_sample, i, row, out.time);
        }
        if (out.position[i] - margin < limits.lower[i]) {
          return reject(Failure::lower_position_limit, i, row, out.time,
            out.position[i] - margin, limits.lower[i]);
        }
        if (out.position[i] + margin > limits.upper[i]) {
          return reject(Failure::upper_position_limit, i, row, out.time,
            out.position[i] + margin, limits.upper[i]);
        }
        if (std::abs(out.position[i] - measured[i]) + margin > max_travel) {
          return reject(Failure::travel_limit, i, row, out.time,
            std::abs(out.position[i] - measured[i]) + margin, max_travel);
        }
        if (std::abs(out.velocity[i]) > limits.velocity[i] + 1e-8) {
          return reject(Failure::velocity_limit, i, row, out.time,
            std::abs(out.velocity[i]), limits.velocity[i]);
        }
      }
    }
    return true;
  }
  const std::array<Sample, points> & samples() const {return samples_;}
  double duration() const {return duration_;}
private:
  bool reject(Failure reason, int joint = -1, int sample = -1,
    double time = 0.0, double value = 0.0, double limit = 0.0) noexcept
  {
    rejection_.reason = reason;
    rejection_.joint = joint;
    rejection_.sample = sample;
    rejection_.time = time;
    rejection_.value = value;
    rejection_.limit = limit;
    return false;
  }
  Rejection rejection_{};
  ruckig::Ruckig<axes> generator_;
  ruckig::Trajectory<axes> trajectory_;
  std::array<Sample, points> samples_{};
  double duration_{0.0};
};
}  // namespace zeroerr
