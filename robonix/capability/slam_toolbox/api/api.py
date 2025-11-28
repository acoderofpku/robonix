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
from robonix.manager.eaios_decorators import eaios

def get_default_config(robot_type):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    config_dir = os.path.join(project_root, "config")

    if robot_type == "wheeltec":
        return os.path.join(config_dir, "mapper_params_online_sync.yaml")
    return os.path.join(config_dir, "sync.param.yml")

_slam_proc = None

@eaios.api
def start_slam_toolbox(robot_type="wheeltec", config_file=None, use_sim_time=False):
    """
    启动 slam_toolbox 节点  
    若系统中已有 slam_toolbox 运行，则先杀死旧进程再启动新的
    返回: dict(success: bool, message: str)
    """
    global _slam_proc

    # --------------------------
    # 检查系统中是否已有 slam_toolbox 正在运行
    # --------------------------
    print("Starting Slam_toolbox")
    try:
        existing_pids = subprocess.check_output(
            ["pgrep", "-f", "sync_slam_toolbox_node"],
            text=True
        ).strip().split("\n")

        if existing_pids and existing_pids[0] != "":
            print(f"[INFO] Existing slam_toolbox PIDs: {existing_pids}")
            for pid in existing_pids:
                try:
                    os.killpg(os.getpgid(int(pid)), signal.SIGTERM)
                except:
                    os.kill(int(pid), signal.SIGTERM)
            time.sleep(1)
            print("[INFO] Old slam_toolbox process killed.")
    except subprocess.CalledProcessError:
        # pgrep 返回非 0 表示没有找到，不属于错误
        pass
    except Exception as e:
        return {"success": False, "message": f"Failed to check existing slam_toolbox: {e}"}

    # --------------------------
    # 再检查脚本内部是否有已记录的子进程
    # --------------------------
    if _slam_proc is not None and _slam_proc.poll() is None:
        try:
            os.killpg(os.getpgid(_slam_proc.pid), signal.SIGTERM)
            _slam_proc.wait(timeout=5)
            _slam_proc = None
        except Exception as e:
            return {"success": False, "message": f"Failed to kill previous internal slam_toolbox: {e}"}

    # --------------------------
    # 开始启动新的 slam_toolbox
    # --------------------------
    try:
        if config_file is None:
            config_file = get_default_config(robot_type)

        if not os.path.exists(config_file):
            return {"success": False, "message": f"Config file not found: {config_file}"}

        odom_topic = "odom_combined" if robot_type == "wheeltec" else "odom"

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
            preexec_fn=os.setsid
        )

        return {"success": True, "message": "slam_toolbox started successfully"}

    except Exception as e:
        return {"success": False, "message": f"Failed to start slam_toolbox: {e}"}

@eaios.api
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