#include "zeroerr/collision_observer_recovery.hpp"

#include <cassert>
#include <iostream>
#include <limits>

int main()
{
  zeroerr::CollisionObserverRecovery recovery;
  using Values = zeroerr::CollisionObserverRecovery::Values;
  Values measured{};
  measured.fill(2.5);
  Values auxiliary{};
  Values velocity{};
  Values residual{};
  Values threshold{};
  threshold.fill(4.0);
  for (int i = 0; i < 32; ++i) {
    assert(!recovery.calibrate(measured, auxiliary, velocity, 0.125, 8.0, 20, 0.02));
  }
  velocity[1] = 0.1;
  assert(!recovery.calibrate(measured, auxiliary, velocity, 0.125, 8.0, 20, 0.02));
  assert(recovery.warmup_samples == 0 && recovery.warmup_elapsed_sec == 0.0);
  velocity.fill(0.0);
  for (int i = 0; i < 63; ++i) {
    assert(!recovery.calibrate(measured, auxiliary, velocity, 0.125, 8.0, 20, 0.02));
  }
  assert(recovery.calibrate(measured, auxiliary, velocity, 0.125, 8.0, 20, 0.02));
  assert(recovery.baseline_valid);
  const auto baseline = recovery.baseline_offset;
  for (double value : baseline) {assert(value == 2.5);}
  recovery.rearm();
  measured.fill(100.0);
  assert(recovery.calibrate(measured, auxiliary, velocity, 0.001, 8.0, 20, 0.02));
  assert(recovery.baseline_offset == baseline);  // A drive interruption alone does not recalibrate.
  assert(recovery.warmup_samples == 0);
  for (int i = 0; i < 3; ++i) {
    assert(!recovery.ready_to_release(residual, threshold, velocity, 0.125, 0.5, 0.02));
  }
  assert(recovery.ready_to_release(residual, threshold, velocity, 0.125, 0.5, 0.02));
  recovery.rearm();
  for (int i = 0; i < 3; ++i) {
    assert(!recovery.ready_to_release(residual, threshold, velocity, 0.125, 0.5, 0.02));
  }
  residual[2] = 3.3;  // Below the trip threshold: no separate recovery margin.
  assert(recovery.ready_to_release(residual, threshold, velocity, 0.125, 0.5, 0.02));
  residual[2] = 100.0;
  for (int i = 0; i < 200; ++i) {
    assert(!recovery.ready_to_release(residual, threshold, velocity, 0.125, 0.5, 0.02));
  }
  assert(recovery.baseline_offset == baseline);
  residual.fill(0.0);
  velocity[3] = 0.1;
  assert(!recovery.ready_to_release(residual, threshold, velocity, 10.0, 0.5, 0.02));
  velocity.fill(0.0);
  residual[0] = std::numeric_limits<double>::quiet_NaN();
  assert(!recovery.ready_to_release(residual, threshold, velocity, 10.0, 0.5, 0.02));
  // Previously tripped joints use the same threshold on every acknowledgement.
  recovery.rearm();
  threshold[5] = 3.5;
  residual.fill(0.0);
  residual[5] = 3.585;
  assert(!recovery.ready_to_release(residual, threshold, velocity, 0.5, 0.5, 0.02));
  residual[5] = 3.5;  // Equality still blocks release, matching trip detection.
  assert(!recovery.ready_to_release(residual, threshold, velocity, 0.5, 0.5, 0.02));
  residual[5] = -3.49;
  assert(!recovery.ready_to_release(residual, threshold, velocity, 0.25, 0.5, 0.02));
  assert(recovery.ready_to_release(residual, threshold, velocity, 0.25, 0.5, 0.02));
  assert(recovery.baseline_offset == baseline);
  recovery.rearm();
  residual[5] = 3.49;
  assert(recovery.ready_to_release(residual, threshold, velocity, 0.5, 0.5, 0.02));
  // Repeated ordinary releases must never learn away persistent contact.
  for (int attempt = 0; attempt < 3; ++attempt) {
    recovery.acknowledge(false);
    measured.fill(100.0);
    residual[5] = 4.0;
    for (int i = 0; i < 100; ++i) {
      assert(recovery.calibrate(measured, auxiliary, velocity, 0.125, 8.0, 20, 0.02));
      assert(!recovery.ready_to_release(residual, threshold, velocity, 0.125, 0.5, 0.02));
    }
    assert(recovery.baseline_offset == baseline);
    assert(recovery.warmup_samples == 0);
  }
  // Only explicit recalibration invalidates a valid baseline.
  recovery.acknowledge(true);
  measured.fill(0.0);
  measured[5] = -4.445;
  for (int i = 0; i < 63; ++i) {
    assert(!recovery.calibrate(measured, auxiliary, velocity, 0.125, 8.0, 20, 0.02));
  }
  assert(recovery.calibrate(measured, auxiliary, velocity, 0.125, 8.0, 20, 0.02));
  assert(std::abs(recovery.baseline_offset[5] + 4.445) < 1e-9);
  residual.fill(0.0);
  assert(recovery.ready_to_release(residual, threshold, velocity, 0.5, 0.5, 0.02));
  recovery.invalidate_baseline();
  residual.fill(0.0);
  assert(!recovery.baseline_valid);
  assert(!recovery.ready_to_release(residual, threshold, velocity, 10.0, 0.5, 0.02));
  std::cout << "Continuous calibration, retained baseline, contact/motion refusal and settled readiness passed\n";
}
