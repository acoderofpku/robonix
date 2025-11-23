#!/bin/bash
echo "installing slam_toolbox..."
echo "installing slam_toolbox via git"

# Install slam_toolbox
echo "cloning slam_toolbox..."
git clone https://github.com/SteveMacenski/slam_toolbox.git src/slam_toolbox -b humble
echo "slam_toolbox installation complete."

# build via colcon
echo "building slam_toolbox..."
rosdep install -q -y -r --from-paths src/slam_toolbox/src --ignore-src
colcon build --symlink-install
echo "slam_toolbox build complete."