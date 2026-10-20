// Local C ABI for the dedicated collision brake. No ROS/service round trip.
#include <ruckig/ruckig.hpp>
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <exception>
#include <vector>

extern "C" int erob_collision_brake(
  const double* q, const double* v, const double* a,
  const double* vmax, const double* amax, const double* jmax,
  const double* lower, const double* upper, double max_travel,
  double max_duration, double sample_period, double* output, int capacity,
  char* error, int error_capacity)
{
  auto fail = [&](const char* reason) {
    if (error && error_capacity > 0) {std::snprintf(error, error_capacity, "%s", reason);}
    return -1;
  };
  try {
    if (!q || !v || !a || !vmax || !amax || !jmax || !lower || !upper || !output ||
        capacity < 2 || !std::isfinite(sample_period) || sample_period < 0.002 ||
        !std::isfinite(max_duration) || max_duration <= 0 || max_duration > 5.0 || sample_period > max_duration ||
        !std::isfinite(max_travel) || max_travel <= 0) {return fail("invalid braking policy/buffer");}
    ruckig::InputParameter<6> input;
    input.control_interface = ruckig::ControlInterface::Velocity;
    input.synchronization = ruckig::Synchronization::Time;
    for (size_t i = 0; i < 6; ++i) {
      if (!std::isfinite(q[i]) || !std::isfinite(v[i]) || !std::isfinite(a[i]) ||
          !std::isfinite(vmax[i]) || vmax[i] <= 0 ||
          !std::isfinite(amax[i]) || amax[i] <= 0 ||
          !std::isfinite(jmax[i]) || jmax[i] <= 0 ||
          std::isnan(lower[i]) || std::isnan(upper[i]) || lower[i] >= upper[i] ||
          q[i] < lower[i] || q[i] > upper[i]) {return fail("invalid measured state or joint limits");}
      input.current_position[i] = q[i];
      input.current_velocity[i] = v[i];
      input.current_acceleration[i] = a[i];
      input.target_position[i] = q[i]; // Unconstrained in velocity interface.
      input.target_velocity[i] = 0.0;
      input.target_acceleration[i] = 0.0;
      input.max_velocity[i] = vmax[i];
      input.max_acceleration[i] = amax[i];
      input.max_jerk[i] = jmax[i];
    }
    ruckig::Ruckig<6> generator;
    ruckig::Trajectory<6> trajectory;
    if (generator.calculate(input, trajectory) < 0) {return fail("Ruckig could not generate collision brake");}
    double duration = trajectory.get_duration();
    if (!std::isfinite(duration) || duration > max_duration) {return fail("collision brake exceeds duration budget");}
    if (duration < 1e-10) {
      // Ruckig's zero-duration profile has no position-extrema data.
      for (size_t i = 0; i < 6; ++i) {
        if (std::abs(v[i]) > 1e-8 || std::abs(a[i]) > 1e-8) {return fail("invalid zero-duration collision brake");}
        output[1+i] = output[20+i] = q[i];
        output[7+i] = output[26+i] = 0.0;
        output[13+i] = output[32+i] = 0.0;
      }
      output[0] = 0.0; output[19] = sample_period;
      return 2;
    }
    // Include every jerk switch. Between these boundaries the position is cubic,
    // so the controller's position/velocity/acceleration interpolation is exact.
    std::vector<double> times{0.0, duration, std::max(duration, sample_period)};
    for (double t = sample_period; t < duration; t += sample_period) {times.push_back(t);}
    const auto profiles = trajectory.get_profiles();
    for (const auto& profile : profiles[0]) {
      double bt = 0.0;
      if (profile.brake.duration > 0) {
        for (size_t i = 0; i < 2; ++i) {
          if (profile.brake.t[i] > 0) {
            if (profile.brake.j[i] != 0.0) {
              const double local = -profile.brake.a[i] / profile.brake.j[i];
              if (local > 0 && local < profile.brake.t[i]) {times.push_back(bt+local);}
            }
            bt += profile.brake.t[i];
            if (bt > 0 && bt < duration) {times.push_back(bt);}
          }
        }
      }
      for (double t : profile.t_sum) {
        const double boundary = profile.brake.duration + t;
        if (boundary > 0 && boundary < duration) {times.push_back(boundary);}
      }
    }
    std::sort(times.begin(), times.end());
    times.erase(std::unique(times.begin(), times.end(), [](double x, double y) {return std::abs(x-y) < 1e-8;}), times.end());
    // Do not use get_position_extrema(): this installed Ruckig version's
    // velocity-control profiles do not initialize the position target `pf`.
    // Evaluate exact extrema inside each constant-jerk interval instead.
    const auto boundaries = times;
    std::array<double, 6> p0, v0, a0, p1, v1, a1;
    for (size_t row = 1; row < boundaries.size(); ++row) {
      const double begin = boundaries[row-1], dt = boundaries[row]-begin;
      trajectory.at_time(begin, p0, v0, a0);
      trajectory.at_time(boundaries[row], p1, v1, a1);
      auto add_root = [&](double root) {
        if (std::isfinite(root) && root > 1e-8 && root < dt-1e-8) {times.push_back(begin+root);}
      };
      for (size_t axis = 0; axis < 6; ++axis) {
        const double jerk = (a1[axis]-a0[axis])/dt;
        if (std::abs(jerk) > 1e-10) {
          add_root(-a0[axis]/jerk); // Velocity extremum.
          const double discriminant = a0[axis]*a0[axis]-2*jerk*v0[axis];
          if (discriminant >= 0) {
            add_root((-a0[axis]+std::sqrt(discriminant))/jerk);
            add_root((-a0[axis]-std::sqrt(discriminant))/jerk);
          }
        } else if (std::abs(a0[axis]) > 1e-12) {
          add_root(-v0[axis]/a0[axis]); // Position extremum under constant acceleration.
        }
      }
    }
    std::sort(times.begin(), times.end());
    times.erase(std::unique(times.begin(), times.end(), [](double x, double y) {return std::abs(x-y) < 1e-8;}), times.end());
    // Keep the exact final state even when a numerically close extremum was merged.
    times.back() = std::max(duration, sample_period);
    if (times.size() > static_cast<size_t>(capacity)) {return fail("collision brake exceeds sample capacity");}
    std::array<double, 6> position, velocity, acceleration;
    for (size_t row = 0; row < times.size(); ++row) {
      trajectory.at_time(times[row], position, velocity, acceleration);
      output[row*19] = times[row];
      for (size_t i = 0; i < 6; ++i) {
        if (!std::isfinite(position[i]) || !std::isfinite(velocity[i]) || !std::isfinite(acceleration[i])) {
          return fail("nonfinite collision brake output");
        }
        if (position[i] < lower[i] || position[i] > upper[i]) {return fail("collision brake exceeds joint position limit");}
        if (std::abs(position[i]-q[i]) > max_travel) {return fail("collision brake exceeds joint travel budget");}
        // Velocity control ignores velocity limits in Ruckig; enforce them here.
        if (std::abs(velocity[i]) > vmax[i] + 1e-8) {return fail("collision brake exceeds joint velocity limit");}
        output[row*19+1+i] = position[i];
        output[row*19+7+i] = velocity[i];
        output[row*19+13+i] = acceleration[i];
      }
    }
    return static_cast<int>(times.size());
  } catch (const std::exception& ex) {return fail(ex.what());}
  catch (...) {return fail("unexpected collision brake failure");}
}
