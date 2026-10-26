#include "zeroerr/command_collision_brake.hpp"
#include <joint_trajectory_controller/trajectory.hpp>
#include <cassert>
#include <chrono>
#include <iostream>
#include <atomic>
#include <cstdlib>
#include <new>

static bool count_allocations = false;
static size_t allocations = 0;
__attribute__((noinline)) void * operator new(std::size_t n) {if (count_allocations) {++allocations;} if (auto p=std::malloc(n)) {return p;} throw std::bad_alloc();}
__attribute__((noinline)) void operator delete(void * p) noexcept {std::free(p);}
__attribute__((noinline)) void operator delete(void * p, std::size_t) noexcept {std::free(p);}

using Brake = zeroerr::CommandCollisionBrake;
using Point = trajectory_msgs::msg::JointTrajectoryPoint;
int main()
{
  Brake brake;
  const Brake::Limits limits{{3,3,3,3,3,3},{6,6,6,8,8,10},{30,30,30,80,80,150},
    {-10,-10,-10,-10,-10,-10},{10,10,10,10,10,10}};
  const std::array<Brake::Vector,3> velocities{{
    {-.523555832,-.199795387,-.069970031,.124510342,-.005285053,-1.504238811},
    {-.759040308,.000245677,-.005039376,-.005303030,-.000119842,-.337686141},
    {.672705788,.017784624,.173903419,.157449047,-.002642527,.561875464}}};
  const std::array<Brake::Vector,3> accelerations{{
    {-.583313289,.600767771,.357217487,-.221501089,-.010149296,-.157520462},
    {-3.068317782,.355613835,-.590576454,-.936915661,-.003788153,-1.572683499},
    {-2.779714396,-.072966577,-.818303314,-.828293136,.035935768,-2.587432449}}};
  for(size_t example=0; example<3; ++example) {
    Brake::Vector measured{}, commanded{};
    for(size_t i=0;i<6;++i) {commanded[i]=.01*(i+1);}
    const auto before=std::chrono::steady_clock::now();
    count_allocations=true;
    const bool accepted=brake.calculate(commanded,velocities[example],accelerations[example],measured,limits,.6,.35,.2);
    count_allocations=false;
    assert(accepted);assert(allocations==0);
    const double generation_us=std::chrono::duration<double,std::micro>(std::chrono::steady_clock::now()-before).count();
    auto message=std::make_shared<trajectory_msgs::msg::JointTrajectory>();
    for(const auto & s:brake.samples()) {
      Point p;p.time_from_start=rclcpp::Duration::from_seconds(s.time);
      p.positions.assign(s.position.begin(),s.position.end());
      p.velocities.assign(s.velocity.begin(),s.velocity.end());
      p.accelerations.assign(s.acceleration.begin(),s.acceleration.end());
      message->points.push_back(p);
    }
    Point prior=message->points.front();
    for(size_t i=0;i<6;i++) {
      assert(prior.positions[i]==commanded[i]);
      assert(std::abs(message->points.back().velocities[i])<1e-8);
      assert(std::abs(message->points.back().accelerations[i])<1e-8);
    }
    const rclcpp::Time epoch(100,0,RCL_ROS_TIME);
    joint_trajectory_controller::Trajectory trajectory(epoch,prior,message);
    joint_trajectory_controller::TrajectoryPointConstIter left,right;
    Point out,previous=prior;
    assert(trajectory.sample(epoch,
      joint_trajectory_controller::interpolation_methods::InterpolationMethod::VARIABLE_DEGREE_SPLINE,
      out,left,right));
    for(size_t i=0;i<6;i++) {assert(out.positions[i]==commanded[i]);}
    for(int k=1;k<=1200;k++) {
      const double t=k*.0005;
      assert(trajectory.sample(epoch+rclcpp::Duration::from_seconds(t),
        joint_trajectory_controller::interpolation_methods::InterpolationMethod::VARIABLE_DEGREE_SPLINE,
        out,left,right));
      for(size_t i=0;i<6;i++) {
        assert(std::isfinite(out.positions[i]));
        assert(std::abs(out.positions[i]-previous.positions[i])<=limits.velocity[i]*.0005+1e-8);
        assert(std::abs(out.velocities[i])<=limits.velocity[i]+1e-6);
        assert(std::abs(out.accelerations[i])<=limits.acceleration[i]+.01);
        if(k==1) {
          const double expected=commanded[i]+velocities[example][i]*t+.5*accelerations[example][i]*t*t;
          assert(std::abs(out.positions[i]-expected)<1e-7);
        }
      }
      previous=out;
    }
    std::cout<<"Recorded stop "<<example<<": no takeover jump, installed-controller interpolation passed, "
      <<"duration="<<brake.duration()<<" generation_us="<<generation_us<<" allocations="<<allocations<<"\n";
  }
  Brake::Vector zero{},bad{};bad[0]=.21;
  assert(!brake.calculate(bad,zero,zero,zero,limits,.6,.35,.2));
  assert(brake.rejection().reason == Brake::Failure::tracking_error);
  assert(brake.rejection().joint == 0);
  assert(brake.rejection().value == .21 && brake.rejection().limit == .2);
  assert(!brake.calculate(zero,velocities[0],accelerations[0],zero,limits,.01,.35,.2));
  assert(brake.rejection().reason == Brake::Failure::duration_limit);
  assert(brake.rejection().value == brake.duration());
  assert(brake.rejection().value > brake.rejection().limit);
  assert(!brake.calculate(zero,velocities[0],accelerations[0],zero,limits,.6,.001,.2));
  assert(brake.rejection().reason == Brake::Failure::travel_limit);
  assert(brake.rejection().joint >= 0 && brake.rejection().sample >= 0);
  bad[0]=NAN;
  assert(!brake.calculate(bad,zero,zero,zero,limits,.6,.35,.2));
  assert(brake.rejection().reason == Brake::Failure::invalid_state);
  assert(brake.duration() == 0.0);  // No stale duration from a previous attempt.
  assert(brake.calculate(zero,zero,zero,zero,limits,.6,.35,.2));
  assert(brake.rejection().reason == Brake::Failure::none);
  assert(brake.rejection().joint == -1 && brake.rejection().sample == -1);
  assert(!brake.calculate(zero,zero,zero,zero,limits,.7,.35,.2));
  assert(brake.rejection().reason == Brake::Failure::invalid_configuration);
  auto bounded = limits;
  bounded.upper[0] = 0.0;
  assert(!brake.calculate(zero,zero,zero,zero,bounded,.6,.35,.2));
  assert(brake.rejection().reason == Brake::Failure::upper_position_limit);
  assert(brake.rejection().joint == 0 && brake.rejection().sample == 0);
  bounded = limits;
  bounded.velocity[1] = 0.0;
  assert(!brake.calculate(zero,zero,zero,zero,bounded,.6,.35,.2));
  assert(brake.rejection().reason == Brake::Failure::invalid_limits);
  assert(brake.rejection().joint == 1);
  std::cout<<"Tracking, duration, travel, nonfinite rejection and stationary hold passed\n";
}
