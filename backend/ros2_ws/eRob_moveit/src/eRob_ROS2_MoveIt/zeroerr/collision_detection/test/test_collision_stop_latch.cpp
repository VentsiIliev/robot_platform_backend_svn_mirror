#include "zeroerr/collision_stop_latch.hpp"
#include "zeroerr/collision_event_diagnostics.hpp"
#include <cassert>
#include <iostream>

int main()
{
  zeroerr::CollisionStopLatch latch;
  // Exact regression: logging-only collision, then active response enabled.
  latch.set_active_response(false);
  assert(latch.should_process(true));
  assert(latch.begin_event());
  assert(!latch.needs_stop());
  assert(!latch.should_process(true));
  latch.set_active_response(true);
  assert(!latch.should_process(false));  // Enabling alone never fabricates a collision.
  assert(latch.should_process(true));
  assert(latch.begin_event());
  assert(latch.needs_stop());
  // A busy publisher does not consume the response. Retry with the same event.
  for (int i=0; i<10; ++i) {
    assert(latch.should_process(true));
    assert(!latch.begin_event());
    assert(latch.needs_stop());
  }
  assert(!latch.should_process(false));  // No delayed stop after exceedance clears.
  latch.mark_stop_published();
  assert(!latch.should_process(true));
  latch.set_active_response(false);
  latch.set_active_response(true);
  assert(!latch.should_process(true));  // A sent stop still requires acknowledgement.
  latch.reset();
  latch.set_active_response(true);
  assert(latch.should_process(true) && latch.begin_event() && latch.needs_stop());
  latch.mark_stop_published();
  assert(!latch.should_process(true));
  // Distinguish a retried publication from a second collision in diagnostics.
  zeroerr::CollisionEventSnapshot event;
  event.triggered_joint=1;event.event_id=4;event.stop_published=true;
  event.stop_publication_update=true;
  const std::vector<std::string> names{"Joint_1","Joint_2","Joint_3","Joint_4","Joint_5","Joint_6"};
  const auto json=zeroerr::collision_event_json(event,names,0);
  assert(json["event"]=="collision_stop_published");
  assert(json["event_id"]==4 && json["stop_published"]==true);
  std::cout<<"Passive-to-active response, publication retries, acknowledgement and diagnostic identity passed\n";
}
