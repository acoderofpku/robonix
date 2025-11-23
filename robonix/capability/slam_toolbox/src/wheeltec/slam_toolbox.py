from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os
import rclpy
from rclpy.node import Node
from lifecycle_msgs.srv import ChangeState
from lifecycle_msgs.msg import Transition
from slam_toolbox.srv import SaveMap

def start_slam_toolbox(config_file: str = None):
    """
    返回一个可启动 slam_toolbox 的 ROS2 Node 实例。
    不启动 wheeltec 的 robot/lidar,只启动 SLAM 节点。
    """

    # 默认使用 wheeltec 的配置文件
    if config_file is None:
        config_file = os.path.join(
            get_package_share_directory("wheeltec_slam_toolbox"),
            "config",
            "mapper_params_online_sync.yaml"
        )

    node = Node(
        package="slam_toolbox",
        executable="sync_slam_toolbox_node",
        name="slam_toolbox",
        output="screen",
        parameters=[config_file],
        remappings=[
            ("odom", "odom_combined")    # wheeltec 环境需要这个
        ]
    )

    return node


def stop_slam_toolbox():
    """
    使用生命周期接口让 slam_toolbox 关闭。
    需要 slam_toolbox 以生命周期节点方式启动。
    """

    rclpy.init()
    node = Node("slam_toolbox_stop_client")

    cli = node.create_client(ChangeState, "/slam_toolbox/transition")

    if not cli.wait_for_service(timeout_sec=2.0):
        return {"success": False, "message": "slam_toolbox transition service unavailable"}

    req = ChangeState.Request()
    req.transition.id = Transition.TRANSITION_DEACTIVATE  # deactivate
    future = cli.call_async(req)
    rclpy.spin_until_future_complete(node, future)

    # 再调用 shutdown
    req.transition.id = Transition.TRANSITION_SHUTDOWN
    future = cli.call_async(req)
    rclpy.spin_until_future_complete(node, future)

    node.destroy_node()
    rclpy.shutdown()

    return {"success": True, "message": "slam_toolbox stopped (via lifecycle)"}
