#pragma once

#include <array>
#include <cmath>
#include <cstddef>

namespace zeroerr
{
// Recovery policy only. Momentum integration and stopping remain in the controller.
struct CollisionObserverRecovery
{
  using Values = std::array<double, 6>;
  Values baseline_offset{};
  Values warmup_sum{};
  bool baseline_valid{false};
  double warmup_elapsed_sec{0.0};
  std::size_t warmup_samples{0};
  double settled_sec{0.0};

  void rearm() noexcept
  {
    // Acknowledgement/drive interruption must never learn contact as a new bias.
    warmup_sum.fill(0.0);
    warmup_elapsed_sec = 0.0;
    warmup_samples = 0;
    settled_sec = 0.0;
  }

  void invalidate_baseline() noexcept
  {
    baseline_valid = false;
    baseline_offset.fill(0.0);
    rearm();
  }

  static bool stationary(const Values & velocity, double limit) noexcept
  {
    for (double value : velocity) {
      if (!std::isfinite(value) || std::abs(value) >= limit) {return false;}
    }
    return true;
  }

  bool calibrate(
    const Values & measured, const Values & auxiliary, const Values & velocity,
    double dt_sec, double required_sec, std::size_t minimum_samples, double velocity_limit) noexcept
  {
    if (baseline_valid) {return true;}
    if (!stationary(velocity, velocity_limit)) {
      rearm();  // Require a continuous stationary window, not samples across different poses.
      return false;
    }
    warmup_elapsed_sec += dt_sec;
    ++warmup_samples;
    for (std::size_t i = 0; i < baseline_offset.size(); ++i) {
      warmup_sum[i] += measured[i] - auxiliary[i];
    }
    if (warmup_elapsed_sec < required_sec || warmup_samples < minimum_samples) {return false;}
    for (std::size_t i = 0; i < baseline_offset.size(); ++i) {
      baseline_offset[i] = warmup_sum[i] / static_cast<double>(warmup_samples);
    }
    baseline_valid = true;
    return true;
  }

  bool ready_to_release(
    const Values & residual, const Values & threshold, const Values & velocity,
    double dt_sec, double required_sec, double clear_ratio, double velocity_limit) noexcept
  {
    bool clear = baseline_valid && stationary(velocity, velocity_limit);
    for (std::size_t i = 0; i < residual.size(); ++i) {
      clear = clear && std::isfinite(residual[i]) && std::isfinite(threshold[i]) &&
        threshold[i] > 0.0 && std::abs(residual[i]) < threshold[i] * clear_ratio;
    }
    settled_sec = clear ? settled_sec + dt_sec : 0.0;
    return clear && settled_sec >= required_sec;
  }
};
}  // namespace zeroerr
