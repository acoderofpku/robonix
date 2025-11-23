import os
import subprocess
import time

def save_map(save_dir="./maps", map_name="map"):
    """
    通过 map_saver_cli 保存当前 SLAM 地图
    """

    save_dir = os.path.abspath(save_dir)
    os.makedirs(save_dir, exist_ok=True)

    # 完整路径（map_saver_cli 不加扩展名）
    save_path = os.path.join(save_dir, map_name)

    cmd = [
        "ros2", "run", "nav2_map_server", "map_saver_cli",
        "-f", save_path
    ]

    try:
        print("[save_map] Running:", " ".join(cmd))
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)

        if result.returncode != 0:
            return {
                "success": False,
                "message": f"map_saver_cli failed: {result.stderr}"
            }

        # 成功
        yaml_path = save_path + ".yaml"
        if os.path.exists(yaml_path):
            return {
                "success": True,
                "message": f"Map saved to {yaml_path}",
                "path": yaml_path
            }

        return {
            "success": False,
            "message": "Unknown error: map file not generated"
        }

    except Exception as e:
        return {"success": False, "message": str(e)}
