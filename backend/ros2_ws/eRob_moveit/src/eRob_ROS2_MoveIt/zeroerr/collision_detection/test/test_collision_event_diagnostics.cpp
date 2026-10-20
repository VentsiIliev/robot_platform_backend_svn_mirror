#include "zeroerr/collision_event_diagnostics.hpp"

#include <cassert>
#include <cmath>
#include <iostream>
#include <thread>

int main()
{
  using namespace zeroerr;
  CollisionJointValues residual{{0.5, -2.0, -0.4, 0.6, -1.6, -4.445}};
  assert(observer_residual_for_plot(residual, true) == residual);
  const auto unavailable = observer_residual_for_plot(residual, false);
  for (double value : unavailable) {assert(std::isnan(value));}
  // Readiness may be false during settling, but initialized torque stays visible.
  assert(observer_residual_for_plot(residual, true)[5] == -4.445);
  CollisionDiagnosticQueue<CollisionEventSnapshot, 3> queue;
  CollisionEventSnapshot event;
  event.event_id = 7;
  event.triggered_joint = 2;
  event.ros_time_ns = 1000000000;
  event.confirm_duration_sec = 0.05;
  event.exceedance_sec[2] = 0.051;
  event.baseline_offset[2] = -1.25;
  event.filtered_residual[2] = -4.5;
  event.threshold[2] = 3.0;
  event.observer_ready_age_sec = 0.06;
  event.stop_published = true;
  event.baseline_valid = true;
  event.observer_initialized = true;
  event.rearm_settled_sec = 0.5;
  // A wrapped trace must be emitted oldest first, with ages relative to detection.
  event.history_count = event.history.size();
  event.history_next = 3;
  for (std::size_t i = 0; i < event.history.size(); ++i) {
    const auto index = (3 + i) % event.history.size();
    event.history[index].ros_time_ns = 750000000 + static_cast<std::int64_t>(i) * 10000000;
    event.history[index].residual[2] = static_cast<double>(i);
  }
  assert(queue.try_push(event));
  event.event_id = 8;
  assert(queue.try_push(event));
  assert(!queue.try_push(event));
  assert(queue.dropped() == 1);
  event.filtered_residual[2] = 100.0;  // Queue holds the trigger snapshot, not live arrays.
  CollisionEventSnapshot captured;
  assert(queue.try_pop(captured));
  assert(captured.event_id == 7);
  assert(captured.filtered_residual[2] == -4.5);
  const std::vector<std::string> names{"Joint_1", "Joint_2", "Joint_3", "Joint_4", "Joint_5", "Joint_6"};
  const auto payload = collision_event_json(captured, names, queue.dropped());
  const auto decoded = nlohmann::json::parse(payload.dump());
  assert(decoded["event"] == "collision_detected");
  assert(decoded["triggered_joint"] == "Joint_3");
  assert(decoded["confirm_duration_ms"] == 50.0);
  assert(decoded["baseline_valid"] == true);
  assert(decoded["observer_initialized"] == true);
  assert(decoded["rearm_settled_ms"] == 500.0);
  assert(decoded["joints"][2]["baseline_offset_nm"] == -1.25);
  assert(decoded["joints"][2]["filtered_residual_nm"] == -4.5);
  assert(decoded["joints"][2]["exceedance_ms"] == 51.0);
  assert(decoded["pre_event_history"][0]["age_ms"] == 250.0);
  assert(decoded["pre_event_history"][24]["age_ms"] == 10.0);
  assert(decoded["pre_event_history"][24]["residual_nm"][2] == 24.0);
  assert(queue.try_pop(captured) && captured.event_id == 8);
  assert(!queue.try_pop(captured));
  captured.triggered_joint = -1;
  captured.history_count = 0;
  const auto ready = collision_event_json(captured, names, 0);
  assert(ready["event"] == "observer_ready");
  assert(ready["triggered_joint"].is_null());
  assert(ready["pre_event_history"].empty());

  // Stress the one-producer/one-consumer handoff, including wraparound/full retries.
  CollisionDiagnosticQueue<CollisionTraceSample, 16> threaded_queue;
  constexpr std::int64_t count = 100000;
  std::thread producer([&]() {
      for (std::int64_t i = 0; i < count; ++i) {
        CollisionTraceSample sample;
        sample.ros_time_ns = i;
        sample.residual.fill(static_cast<double>(i));
        while (!threaded_queue.try_push(sample)) {std::this_thread::yield();}
      }
    });
  for (std::int64_t i = 0; i < count; ++i) {
    CollisionTraceSample sample;
    while (!threaded_queue.try_pop(sample)) {std::this_thread::yield();}
    assert(sample.ros_time_ns == i);
    for (double value : sample.residual) {assert(value == static_cast<double>(i));}
  }
  producer.join();
  std::cout << "Collision snapshot, JSON units, trace ordering and queue concurrency passed\n";
}
