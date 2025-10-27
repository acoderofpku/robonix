import subprocess
import os
import time
import psutil
from robonix.manager.eaios_decorators import eaios

MAPPING_LAUNCH_MAP = {
    "gmapping":  "slam_gmapping/slam_gmapping.launch.py",
    "cartographer": "wheeltec_cartographer/cartographer.launch.py",
    "slam_toolbox": "wheeltec_slam_toolbox/online_sync.launch.py"
}

@eaios.api
def start_mapping(mapping_method: str = "gmapping", config_file: str = None) -> dict:
    """
    启动指定建图算法的ROS2建图进程。
    Args:
        mapping_method: 建图算法，可选 ["gmapping", "cartographer", "slam_toolbox"]
        config_file: 配置文件，可选
    Returns:
        { "success": bool, "message": str }
    """
    try :
        if mapping_method not in  MAPPING_LAUNCH_MAP:
            return{
                "success":False,
                "message":f"Unkonwn mapping method: {mapping_method}"
            }
        launch_path = MAPPING_LAUNCH_MAP[mapping_method]
        cmd = [
            "ros2", "launch",
            *launch_path.split("/") 
        ]

        if config_file:
            cmd += ["--ros-args", "-p", f"config_file:={config_file}"]
        
        log_file = f"/tmp/{mapping_method}_mapping.log"

        with open(log_file, "w") as f:
            proc = subprocess.Popen(cmd, stdout=f, stderr=f)

        time.sleep(3)

        # 检查进程是否仍在运行
        if proc.poll() is not None:
            with open(log_file, "r") as f:
                error_output = f.read()[-500:] 
            return {"success": False, "message": f"Launch failed:{error_output}"}

        # 检查是否在 ps 进程列表中
        p = psutil.Process(proc.pid)
        children = p.children(recursive=True)
        if not children:
            return {"success": False, "message": "No child processes found — launch may have failed"}

        return {
            "success": True,
            "message": f"Started mapping using {mapping_method}",
            "launch_file": launch_path,
            "config_file": config_file,
        }

    except Exception as e:
        return {"success": False, "message": str(e)}
    
@eaios.api
def stop_mapping() -> dict:
    """
    停止所有建图相关节点。
    """
    try:
        for node in ["slam_gmapping", "cartographer_node", "slam_toolbox_node"]:
            subprocess.run(["pkill", "-f", node], check=False)
        return {"success": True, "message": "Stopped all mapping nodes"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    
@eaios.api
def save_map(map_name: str = "default_map", save_dir: str = "./maps") -> dict:
    """
    保存当前地图结果到指定（可相对）路径。

    Args:
        map_name: 地图文件名（不带后缀）
        save_dir: 保存目录，可为相对路径或绝对路径
    Returns:
        {
            "success": bool,
            "path": str,
            "message": str,
            "log_file": str
        }
    """
    try:
        # 确保保存目录存在
        os.makedirs(save_dir, exist_ok=True)

        # 构建地图路径
        map_path = os.path.join(save_dir, map_name)
        log_file = f"/tmp/save_map_{map_name}.log"

        # 构建命令
        cmd = ["ros2", "run", "nav2_map_server", "map_saver_cli", "-f", map_path]

        # 执行命令并捕获输出
        with open(log_file, "w") as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, text=True)

        # 检查返回码
        if result.returncode != 0:
            with open(log_file, "r") as f:
                log_tail = f.readlines()[-10:] 
            return {
                "success": False,
                "path": "",
                "message": "Map saver command failed:\n" + "".join(log_tail),
                "log_file": log_file
            }

        # 稍微等一下文件写入
        time.sleep(2)

        yaml_path = f"{map_path}.yaml"
        pgm_path = f"{map_path}.pgm"

        # 检查文件是否生成
        if not os.path.exists(yaml_path) or not os.path.exists(pgm_path):
            return {
                "success": False,
                "path": "",
                "message": "Map save failed: expected output files not found",
                "log_file": log_file
            }

        return {
            "success": True,
            "path": yaml_path,
            "message": f"Map saved successfully: {yaml_path}",
            "log_file": log_file
        }

    except Exception as e:
        return {
            "success": False,
            "path": "",
            "message": str(e),
            "log_file": ""
        }