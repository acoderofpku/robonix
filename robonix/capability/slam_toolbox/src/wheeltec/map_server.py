import os
import subprocess
from launch_ros.actions import Node as LaunchNode


def start_map_saver(map_path: str):
    """
    返回一个 nav2_map_server 的 map_saver_cli Node,启动后会自动保存地图。
    map_path: 地图保存路径（不带扩展名）
    """
    node = LaunchNode(
        package='nav2_map_server',
        executable='map_saver_cli',
        name='map_saver',
        output='screen',
        arguments=['-f', map_path],
        parameters=[
            {'save_map_timeout': 20000.0},
            {'free_thresh_default': 0.196},
        ]
    )
    return node


def start_map_backup(backup_path: str):
    """
    返回一个 map_saver_cli 节点，用于备份地图。
    """
    node = LaunchNode(
        package='nav2_map_server',
        executable='map_saver_cli',
        name='map_backup',
        output='screen',
        arguments=['-f', backup_path],
        parameters=[
            {'save_map_timeout': 20000.0},
            {'free_thresh_default': 0.196},
        ]
    )
    return node


def cli_save_map(map_name="map", save_dir="."):
    """
    对 nav2_map_server 的 map_saver_cli 进行封装。
    不需要启动 Node,直接命令行方式保存地图。
    """

    os.makedirs(save_dir, exist_ok=True)
    map_path = os.path.join(save_dir, map_name)

    cmd = [
        "ros2", "run", "nav2_map_server",
        "map_saver_cli",
        "-f", map_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return {
                "success": False,
                "message": "map_saver_cli failed",
                "stderr": result.stderr,
                "stdout": result.stdout
            }

        yaml = map_path + ".yaml"
        pgm = map_path + ".pgm"

        if not os.path.exists(yaml):
            return {"success": False, "message": "Map yaml not found"}

        return {
            "success": True,
            "path": yaml,
            "message": "Map saved successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Exception: {str(e)}"
        }
