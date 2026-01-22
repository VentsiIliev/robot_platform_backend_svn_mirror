#!/bin/bash
# A script to completely stop all ROS 2 background processes and relaunch your demo

echo "=============================================="
echo "   Stopping all ROS 2 background processes..."
echo "=============================================="

# Define process names to kill
ROS_PROCESSES=(
  "ros2"
  "rviz2"
  "gzserver"
  "gzclient"
  "rosmaster"
  "rosout"
  "python.*launch"
  "at-spi-bus-launcher"
)

# Function to check if a process is still running
is_running() {
  pgrep -f "$1" > /dev/null 2>&1
}

# Attempt to kill each process
for PROC in "${ROS_PROCESSES[@]}"; do
  echo "Stopping process: $PROC"
  pkill -f "$PROC" 2>/dev/null

  # Wait for it to fully terminate
  for i in {1..5}; do
    if ! is_running "$PROC"; then
      echo "✅ $PROC stopped."
      break
    fi
    echo "⏳ Waiting for $PROC to stop..."
    sleep 1
  done

  # If still running, force kill
  if is_running "$PROC"; then
    echo "⚠️  $PROC still running. Forcing kill..."
    pkill -9 -f "$PROC" 2>/dev/null
    sleep 1
    if is_running "$PROC"; then
      echo "❌ Failed to kill $PROC even with -9"
    else
      echo "✅ $PROC force-killed."
    fi
  fi
done

echo "=============================================="
echo "   Checking for zombie (defunct) ROS2 processes..."
echo "=============================================="

# Detect zombie ROS2 processes
ZOMBIES=$(ps -eo pid,ppid,stat,cmd | grep "[r]os2" | grep "Z")

if [[ -n "$ZOMBIES" ]]; then
  echo "⚠️  Found zombie ros2 processes:"
  echo "$ZOMBIES"
  echo "Attempting to kill their parent processes..."
  while read -r PID PARENT_PID STAT CMD; do
    if [[ "$STAT" == *"Z"* ]]; then
      echo "Killing parent process of zombie PID $PID (parent $PARENT_PID)"
      kill -9 "$PARENT_PID" 2>/dev/null
    fi
  done <<< "$(ps -eo pid,ppid,stat,cmd | grep "[r]os2" | grep "Z")"
  sleep 1
else
  echo "✅ No zombie ros2 processes found."
fi

echo "=============================================="
echo "   Verifying no ROS processes remain..."
echo "=============================================="

if pgrep -fa "ros2|rviz2|gzserver|gzclient|rosmaster|rosout|launch|at-spi-bus-launcher" > /dev/null; then
  echo "❌ Some ROS-related processes are still running:"
  pgrep -fa "ros2|rviz2|gzserver|gzclient|rosmaster|rosout|launch"
  echo "Please terminate them manually before continuing."
  exit 1
else
  echo "✅ All ROS-related processes have been stopped."
fi

echo "=============================================="
echo "   Building ROS 2 workspace..."
echo "=============================================="

cd ~/ros2_ws || { echo "❌ Workspace not found!"; exit 1; }

colcon build

source ./install/setup.bash

echo "=============================================="
echo "   Launching ROS 2 demo..."
echo "=============================================="
ros2 launch pl25488 demo.launch.py

