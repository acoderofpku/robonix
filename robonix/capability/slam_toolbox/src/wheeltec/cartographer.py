import os
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import subprocess
import time


def start_cartographer(config_file: str = None):
    """
    返回两个 cartographer Node:cartographer_node + occupancy_grid_node
    """

    if config_file is None:
        config_directory = os.path.join(
            get_package_share_directory("wheeltec_cartographer"),
            "config"
        )
        config_basename = "cartographer.lua"
    else:
        config_directory = os.path.dirname(config_file)
        config_basename = os.path.basename(config_file)

    carto = Node(
        package="cartographer_ros",
        executable="cartographer_node",
        name="cartographer",
        output="screen",
        arguments=[
            "-configuration_directory", config_directory,
            "-configuration_basename", config_basename
        ]
    )

    grid = Node(
        package="cartographer_ros",
        executable="occupancy_grid_node",
        name="cartographer_grid",
        output="screen",
        arguments=[
            "-resolution", "0.05",
            "-publish_period_sec", "0.5"
        ]
    )

    return [carto, grid]


def stop_cartographer():
    subprocess.run(["pkill", "-f", "cartographer_node"], check=False)
    subprocess.run(["pkill", "-f", "occupancy_grid_node"], check=False)
    return {"success": True}

