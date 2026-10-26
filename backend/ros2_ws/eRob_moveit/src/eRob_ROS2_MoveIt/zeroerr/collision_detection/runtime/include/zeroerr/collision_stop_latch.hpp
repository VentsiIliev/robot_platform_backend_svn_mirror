#pragma once

namespace zeroerr
{
// Real-time-only state: logging an event must never consume its active response.
class CollisionStopLatch
{
public:
  void set_active_response(bool enabled) noexcept
  {
    // A logging-only event becomes a new active event if exceedance is still
    // confirmed after enabling response. A sent stop still requires acknowledgement.
    if (enabled && !active_response_ && !stop_published_) {event_logged_ = false;}
    active_response_ = enabled;
  }
  bool should_process(bool confirmed_exceedance) const noexcept
  {
    return confirmed_exceedance &&
      (!event_logged_ || (active_response_ && !stop_published_));
  }
  bool begin_event() noexcept
  {
    const bool first = !event_logged_;
    event_logged_ = true;
    return first;
  }
  bool needs_stop() const noexcept {return active_response_ && !stop_published_;}
  void mark_stop_published() noexcept {stop_published_ = true;}
  void reset() noexcept {*this = CollisionStopLatch{};}
private:
  bool event_logged_{false};
  bool stop_published_{false};
  bool active_response_{false};
};
}  // namespace zeroerr
