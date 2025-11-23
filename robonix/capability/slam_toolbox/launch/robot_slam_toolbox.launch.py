from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():

    # ===== 参数声明 =====
    declare_robot_type = DeclareLaunchArgument(
        "robot_type",
        default_value="generic",
        description="Robot type selection: wheeltec / generic"
    )

    declare_config_file = DeclareLaunchArgument(
        "config_file",
        default_value="",
        description="Full path to custom slam config yaml (overrides robot_type)"
    )
    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time",
        default_value="false",
        description="Use /clock from simulation"
    )

    robot_type = LaunchConfiguration("robot_type")
    config_file = LaunchConfiguration("config_file")
    use_sim_time = LaunchConfiguration("use_sim_time")

    # 等价于：
    # if config_file != "" → config_file
    # else if robot_type == wheeltec → wheeltec_params
    # else → generic_params

    # ===== remapping =====
    odom_remap = PythonExpression([
        "'odom_combined' if '", robot_type, "' == 'wheeltec' else 'odom'"
    ])

    slam_node = Node(
        package="slam_toolbox",
        executable="sync_slam_toolbox_node",
        name="slam_toolbox",
        output="screen",
        parameters=[config_file],
        remappings=[
            ("odom", odom_remap)
        ]
    )

    return LaunchDescription([
        declare_robot_type,
        declare_config_file,
        declare_use_sim_time,
        slam_node
    ])
