#include <controller_interface/controller_interface.hpp>
#include <pluginlib/class_loader.hpp>
#include <hardware_interface/loaned_command_interface.hpp>
#include <hardware_interface/loaned_state_interface.hpp>
#include <rclcpp/rclcpp.hpp>
#include <trajectory_msgs/msg/joint_trajectory.hpp>
#include <lifecycle_msgs/msg/state.hpp>
#include <cassert>
#include <iostream>
#include <thread>

int main(int argc,char **argv) {
 rclcpp::init(argc,argv);
 pluginlib::ClassLoader<controller_interface::ControllerInterface> loader("controller_interface","controller_interface::ControllerInterface");
 auto controller=loader.createSharedInstance("zeroerr/CommandCollisionTrajectoryController");
 std::string urdf="<robot name='offline'><link name='base'/>";
 std::vector<std::string> names;
 for(int i=0;i<6;i++) {
  auto name="Joint_"+std::to_string(i+1); names.push_back(name);
  const auto parent=i==0?"base":"link"+std::to_string(i);
  const auto child="link"+std::to_string(i+1);
  urdf+="<link name='"+child+"'/><joint name='"+name+"' type='revolute'><parent link='"+parent+"'/><child link='"+child+"'/><axis xyz='0 0 1'/><limit lower='-10' upper='10' velocity='3' effort='100'/></joint>";
 }
 urdf+="</robot>";
 rclcpp::NodeOptions options;
 options.parameter_overrides({rclcpp::Parameter("joints",names),
  rclcpp::Parameter("command_interfaces",std::vector<std::string>{"position"}),
  rclcpp::Parameter("state_interfaces",std::vector<std::string>{"position","velocity"}),
  rclcpp::Parameter("allow_nonzero_velocity_at_trajectory_end",true),
  rclcpp::Parameter("state_publish_rate",0.0)});
 assert(controller->init("offline_collision_controller",urdf,2000,"/stop_fix_test",options)==controller_interface::return_type::OK);
 assert(controller->configure().id()==lifecycle_msgs::msg::State::PRIMARY_STATE_INACTIVE);
 std::array<double,6> q{},v{},command{};
 std::vector<std::unique_ptr<hardware_interface::CommandInterface>> cmd;
 std::vector<std::unique_ptr<hardware_interface::StateInterface>> state;
 std::vector<hardware_interface::LoanedCommandInterface> lc;
 std::vector<hardware_interface::LoanedStateInterface> ls;
 for(int i=0;i<6;i++) {
  cmd.push_back(std::make_unique<hardware_interface::CommandInterface>(names[i],"position",&command[i]));
  lc.emplace_back(*cmd.back());
  state.push_back(std::make_unique<hardware_interface::StateInterface>(names[i],"position",&q[i]));ls.emplace_back(*state.back());
  state.push_back(std::make_unique<hardware_interface::StateInterface>(names[i],"velocity",&v[i]));ls.emplace_back(*state.back());
 }
 controller->assign_interfaces(std::move(lc),std::move(ls));
 assert(controller->get_node()->activate().id()==lifecycle_msgs::msg::State::PRIMARY_STATE_ACTIVE);
 auto test_node=std::make_shared<rclcpp::Node>("offline_collision_test","/stop_fix_test");
 auto publisher=test_node->create_publisher<trajectory_msgs::msg::JointTrajectory>("/stop_fix_test/offline_collision_controller/joint_trajectory",10);
 rclcpp::executors::SingleThreadedExecutor executor;executor.add_node(controller->get_node()->get_node_base_interface());executor.add_node(test_node);
 for(int i=0;i<30;i++){executor.spin_some();std::this_thread::sleep_for(std::chrono::milliseconds(10));}
 double epoch=100.;
 auto tick=[&](){epoch+=.0005;return controller->update(rclcpp::Time(static_cast<int64_t>(epoch*1e9),RCL_ROS_TIME),rclcpp::Duration::from_seconds(.0005));};
 assert(tick()==controller_interface::return_type::OK);
 trajectory_msgs::msg::JointTrajectory normal;normal.joint_names=names;
 trajectory_msgs::msg::JointTrajectoryPoint start,end;
 start.positions=std::vector<double>(6,0.0);start.velocities=std::vector<double>(6,.3);start.accelerations=std::vector<double>(6,0.0);
 end=start;end.positions=std::vector<double>(6,.3);end.velocities=std::vector<double>(6,0.0);end.time_from_start=rclcpp::Duration::from_seconds(1.);
 normal.points={start,end};publisher->publish(normal);
 for(int i=0;i<30;i++){executor.spin_some();std::this_thread::sleep_for(std::chrono::milliseconds(2));}
 for(int k=0;k<100;k++){assert(tick()==controller_interface::return_type::OK);for(int i=0;i<6;i++){q[i]=command[i]-.01;v[i]=.3;}}
 const auto previous=command;
 trajectory_msgs::msg::JointTrajectory stop;stop.joint_names=names;stop.header.frame_id="zeroerr_command_brake_v1";
 start.positions.assign(q.begin(),q.end());start.velocities.assign(6,.3);start.accelerations.assign(6,0.);
 end=start;end.time_from_start=rclcpp::Duration::from_seconds(.3);end.velocities.assign(6,0.);end.accelerations.assign(6,0.);
 for(auto & x:end.positions)x+=.045;
 stop.points={start,end};publisher->publish(stop);
 for(int i=0;i<30;i++){executor.spin_some();std::this_thread::sleep_for(std::chrono::milliseconds(2));}
 auto takeover_start=std::chrono::steady_clock::now();
 assert(tick()==controller_interface::return_type::OK);
 std::cout<<"Full takeover update_us="<<std::chrono::duration<double,std::micro>(std::chrono::steady_clock::now()-takeover_start).count()<<"\n";
 for(int i=0;i<6;i++) {
  std::cout<<names[i]<<" previous_command="<<previous[i]<<" measured="<<q[i]<<" next_command="<<command[i]<<" step="<<command[i]-previous[i]<<"\n";
  assert(command[i]>previous[i]); // ordinary measured-origin takeover steps backwards by ~.01 rad
  assert(std::abs(command[i]-previous[i])<.001);
 }
 for(int k=0;k<1200;k++){for(int i=0;i<6;i++){q[i]=command[i];v[i]=0.;}assert(tick()==controller_interface::return_type::OK);}
 executor.spin_some();
 // A second marked request uses the other preallocated buffer. A measured
 // preview claiming motion must not override the controller's stationary command.
 const auto stopped=command;
 publisher->publish(stop);
 for(int i=0;i<30;i++){executor.spin_some();std::this_thread::sleep_for(std::chrono::milliseconds(2));}
 assert(tick()==controller_interface::return_type::OK);
 for(int i=0;i<6;i++) {assert(std::abs(command[i]-stopped[i])<1e-8);}
 // Reject a request outside the configured tracking budget without forwarding
 // its stale measured-origin curve to the standard controller.
 for(int i=0;i<6;i++){q[i]=command[i]-1.;}
 publisher->publish(stop);
 for(int i=0;i<30;i++){executor.spin_some();std::this_thread::sleep_for(std::chrono::milliseconds(2));}
 const auto before_refusal=command;
 assert(tick()==controller_interface::return_type::ERROR);
 assert(command==before_refusal);
 executor.spin_some();
 std::cout<<"Repeated collision, stationary command and excessive tracking-error refusal passed\n";
 controller->get_node()->deactivate();controller->release_interfaces();
 executor.remove_node(controller->get_node()->get_node_base_interface());executor.remove_node(test_node);
 controller.reset();rclcpp::shutdown();
 std::cout<<"Live plugin, synthetic hardware, ordinary path and marked collision takeover passed\n";
}
