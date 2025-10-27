echo "Building crawler_mapping packages..."
source /opt/ros/humble/setup.bash
colcon build --symlink-install

echo "carwler_mapping build completed successfully!"