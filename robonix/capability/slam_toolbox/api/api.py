import os
import time
from launch import LaunchService, LaunchDescription
from launch import LaunchService
from launch.launch_description_sources import PythonLaunchDescriptionSource
import rclpy
from rclpy.node import Node
from lifecycle_msgs.srv import ChangeState
from lifecycle_msgs.msg import Transition
import subprocess
import shlex
import signal 
from nav2_msgs.srv import SaveMap

def get_default_config(robot_type):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    config_dir = os.path.join(project_root, "config")

    if robot_type == "wheeltec":
        return os.path.join(config_dir, "mapper_params_online_sync.yaml")
    return os.path.join(config_dir, "sync.param.yml")

_slam_proc = None
def start_slam_toolbox(robot_type="wheeltec", config_file=None, use_sim_time=False):
    """
    启动 slam_toolbox 节点
    返回: dict(success: bool, message: str)
    """
    global _slam_proc

    if _slam_proc is not None and _slam_proc.poll() is None:
        return {"success": False, "message": "slam_toolbox is already running"}

    try:
        if config_file is None:
            config_file = get_default_config(robot_type)

        if not os.path.exists(config_file):
            return {"success": False, "message": f"Config file not found: {config_file}"}

        odom_topic = "odom_combined" if robot_type == "wheeltec" else "odom"

        # 构建 ros2 run 命令
        cmd = (
            f"ros2 run slam_toolbox sync_slam_toolbox_node "
            f"--ros-args "
            f"-p use_sim_time:={str(use_sim_time).lower()} "
            f"-p odom_frame:={odom_topic} "
            f"-p map_frame:=map "
            f"-p base_frame:={'base_footprint' if robot_type=='wheeltec' else 'base_link'} "
            f"-p scan_topic:={'/scan' if robot_type=='wheeltec' else '/scanner/scan'} "
            f"-p slam_toolbox.config_file:={config_file}"
        )

        _slam_proc = subprocess.Popen(
            shlex.split(cmd),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # 方便后续通过 os.killpg 停止整个进程组
        )

        return {"success": True, "message": "slam_toolbox started successfully"}

    except Exception as e:
        return {"success": False, "message": f"Failed to start slam_toolbox: {e}"}

def stop_slam_toolbox():
    """
    停止 slam_toolbox 节点
    """
    global _slam_proc
    if _slam_proc is None or _slam_proc.poll() is not None:
        return {"success": False, "message": "slam_toolbox is not running"}

    try:
        os.killpg(os.getpgid(_slam_proc.pid), signal.SIGTERM)
        _slam_proc.wait(timeout=5)
        _slam_proc = None
        return {"success": True, "message": "slam_toolbox stopped successfully"}
    except Exception as e:
        return {"success": False, "message": f"Failed to stop slam_toolbox: {e}"}