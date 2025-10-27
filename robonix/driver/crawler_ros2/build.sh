#!/bin/bash
# Build script for crawler_ros2

set -e

echo "Building crawler_ros2 packages..."
source /opt/ros/humble/setup.bash
colcon build --symlink-install

echo "crawler_ros2 build completed successfully!"
echo "To use the built packages, run: source install/setup.bash"