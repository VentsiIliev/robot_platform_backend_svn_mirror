cmake_minimum_required(VERSION 3.22)
project(zeroerr)

find_package(ament_cmake REQUIRED)
find_package(ament_index_cpp REQUIRED)
find_package(control_msgs REQUIRED)
find_package(controller_interface REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(moveit_msgs REQUIRED)
find_package(moveit_servo REQUIRED)
find_package(kdl_parser REQUIRED)
find_package(nlohmann_json REQUIRED)
find_package(pluginlib REQUIRED)
find_package(rclcpp REQUIRED)
find_package(realtime_tools REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)
find_package(trajectory_msgs REQUIRED)

add_executable(zeroerr_servo_node src/zeroerr_servo_node.cpp)
ament_target_dependencies(zeroerr_servo_node
  control_msgs
  geometry_msgs
  moveit_msgs
  moveit_servo
  rclcpp
  std_msgs
  std_srvs
  trajectory_msgs
)

add_library(zeroerr_realtime_collision_controller SHARED
  collision_detection/runtime/src/realtime_collision_controller.cpp
)
target_include_directories(zeroerr_realtime_collision_controller PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/collision_detection/runtime/include>
  $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(zeroerr_realtime_collision_controller
  ament_index_cpp
  control_msgs
  controller_interface
  kdl_parser
  pluginlib
  rclcpp
  realtime_tools
  sensor_msgs
  std_msgs
)
target_link_libraries(zeroerr_realtime_collision_controller nlohmann_json::nlohmann_json)
pluginlib_export_plugin_description_file(
  controller_interface collision_detection/runtime/zeroerr_controllers.xml)

install(TARGETS zeroerr_servo_node
  DESTINATION lib/${PROJECT_NAME}
)
install(TARGETS zeroerr_realtime_collision_controller
  EXPORT export_zeroerr_realtime_collision_controller
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
  RUNTIME DESTINATION lib
)
install(DIRECTORY collision_detection/runtime/include/ DESTINATION include)

ament_export_targets(export_zeroerr_realtime_collision_controller HAS_LIBRARY_TARGET)
ament_export_dependencies(ament_index_cpp controller_interface kdl_parser pluginlib realtime_tools)

install(PROGRAMS
  scripts/zeroerr_state_publisher.py
  scripts/zeroerr_error_monitor.py
  scripts/zeroerr_drive_diagnostics.py
  scripts/zeroerr_runtime.py
  scripts/disk_pose_tuner.py
  scripts/mounting_surface_pose_tuner.py
  collision_detection/diagnostics/zeroerr_collision_status_gui.py
  collision_detection/calibration/data_collection/zeroerr_collision_calibration_runner.py
  collision_detection/calibration/data_collection/zeroerr_calibration_coverage_plot.py
  collision_detection/calibration/data_collection/zeroerr_peak_recorder.py
  collision_detection/calibration/modeling/zeroerr_dynamic_threshold_fit.py
  collision_detection/calibration/modeling/zeroerr_residual_model_fit.py
  collision_detection/calibration/modeling/zeroerr_motion_model_fit.py
  collision_detection/calibration/modeling/zeroerr_collision_model_audit.py
  collision_detection/calibration/modeling/zeroerr_peak_threshold_calibrate.py
  collision_detection/runtime/legacy/zeroerr_collision_monitor.py
  DESTINATION lib/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/EtherCatStart.sh
  scripts/PollEthercat.sh
  scripts/WaitForSlavesOp.sh
  scripts/wait_for_ros.py
  scripts/StartMoveIt.sh
  DESTINATION share/${PROJECT_NAME}/scripts
)


install(DIRECTORY launch DESTINATION share/${PROJECT_NAME}
  PATTERN "setup_assistant.launch" EXCLUDE)
install(DIRECTORY config DESTINATION share/${PROJECT_NAME})
install(FILES
  collision_detection/config/collision_monitor_config.json
  collision_detection/diagnostics/collision_observer_plotjuggler.xml
  DESTINATION share/${PROJECT_NAME}/config
)
install(DIRECTORY meshes DESTINATION share/${PROJECT_NAME})
install(FILES .setup_assistant DESTINATION share/${PROJECT_NAME})

ament_package()
