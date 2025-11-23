import os
import subprocess
from launch_ros.actions import Node as LaunchNode
from ament_index_python.packages import get_package_share_directory


def start_gmapping(config_file: str = None):
    """
    返回一个可启动 gmapping 的 ROS2 Node 实例。
    不启动 wheeltec 的 robot/lidar。
    只启动 slam_gmapping 节点。
    """

    # gmapping 默认没有配置文件，但 wheeltec 提供了一些默认参数
    # 如果有你自己的配置文件，也可以传入
    parameters = []
    if config_file is not None:
        parameters.append(config_file)

    node = LaunchNode(
        package='slam_gmapping',
        executable='slam_gmapping',
        name='gmapping',
        output='screen',
        parameters=parameters
    )

    return node


def stop_gmapping():
    """
    停止 gmapping。
    由于 gmapping 不是 lifecycle 节点，只能通过 kill 方式停止。
    """

    try:
        #使用 pkill
        subprocess.run(["pkill", "-f", "slam_gmapping"], check=False)

        return {
            "success": True,
            "message": "gmapping stopped (via pkill)"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Exception when stopping gmapping: {str(e)}"
        }