from robonix.manager.eaios_decorators import eaios

import time


@eaios.api
def skl_build_2D_map(
    robot_type: str = "wheeltec",
    mapping_method: str = "slam_toolbox",
    config_file: str = None,
    map_name: str = "default_map",
    save_dir: str = "./maps",
    mapping_time: int = 120,
    duration_sec: float = 1.0
) -> dict:
    """
    主入口：完整执行一次建图流程。
    Skill 层只调用 Cap,不关心底层算法。

    Args:
        robot_type: 机器人类型，目前通过参数传递
        mapping_method: slam_toolbox / cartographer / gmapping
        config_file: 配置文件路径（可选）
        map_name: 保存地图名
        save_dir: 保存目录
        mapping_time: 建图时长（秒），可被自动化流程替代

    Returns:
        dict: 完整建图结果
    """

    # 启动建图算法
    start_res = start_slam_toolbox(robot_type, config_file, False)
    if not start_res.get("success", False):
        return {
            "success": False,
            "stage": "start_mapping",
            "message": start_res.get("message")
        }

    # 可根据需要从返回中获取节点
    # mapping_node = start_res.get("node")

    # Skill 层可以做导航、机器人移动逻辑（此处使用等待策略）
    """
    start_time = time.time()
    while time.time() - start_time <= mapping_time :
        pose = get_pos()
        if pose is None:
            print("[Mapping]SLAM not ready, waiting for TF map->base_link ...")
        else:
            print("[Mapping]Current pose:", pose)
        time.sleep(duration_sec)
    """
    time.sleep(mapping_time)
    # 停止建图
    stop_res = stop_slam_toolbox()
    if not stop_res.get("success", False):
        return {
            "success": False,
            "stage": "stop_mapping",
            "message": stop_res.get("message"),
            "map_path":None
        }
    print("[SLAM] Mapping finished, saving map...") 
    
    # 保存地图
    save_res = save_map(save_dir, map_name)
    if not save_res.get("success", False):
        return {
            "success": False,
            "stage": "save_map",
            "message": save_res.get("message"),
            "map_path":None
        }

    # 5. 完成
    return {
        "success": True,
        "message": "2D mapping completed successfully",
        "mapping_method": mapping_method,
        "map_path": save_dir+map_name
    }
