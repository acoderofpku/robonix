source /opt/ros/humble/setup.bash
source install/setup.sh 
ros2 launch turn_on_wheeltec_robot turn_on_wheeltec_robot.launch.py
ros2 launch wheeltec_joy wheeltec_joy.launch.py