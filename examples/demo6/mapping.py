#!/usr/bin/env python3

import sys
import os
import argparse
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

project_root_parent = Path(
    __file__
).parent.parent.parent.parent  # robonix root
sys.path.insert(0, str(project_root_parent))

from robonix.uapi import get_runtime, set_runtime
from robonix.manager.log import logger, set_log_level

from robonix.skill import *

set_log_level("debug")


def init_skill_providers(runtime):
    """Initialize skill providers for mapping demo"""
    from robonix.uapi.runtime.provider import SkillProvider

    # dump __all__ in robonix.skill to skills list
    try:
        from robonix.skill import __all__
        skills = __all__
    except ImportError:
        logger.warning("robonix.skill module not available")
        skills = []

    local_provider = SkillProvider(
        name="local_provider",
        IP="127.0.0.1",
        skills=skills,
    )

    runtime.registry.add_provider(local_provider)
    logger.info(f"Added skill providers: {runtime.registry}")


def create_mapping_entity_builder():
    """创建建图 Entity 并绑定capabilities"""
    def builder(runtime, **kwargs):
        from robonix.uapi.graph.entity import create_root_room, create_controllable_entity

        root = create_root_room()
        runtime.set_graph(root)

        mapping = create_controllable_entity("mapping")
        root.add_child(mapping)

        mapping.bind_skill("cap_start_mapping", start_mapping)
        mapping.bind_skill("cap_stop_mapping", stop_mapping)
        mapping.bind_skill("cap_save_map", save_map)

        logger.info("Mapping entity graph initialized:")
        logger.info(f"  root: {root.get_absolute_path()}")
        logger.info(f"  mapping: {mapping.get_absolute_path()}")

    return builder

def main():
    parser = argparse.ArgumentParser(description="Mapping Test Demo")
    parser.add_argument(
        "--export-scene", 
        type=str, 
        help="Export scene info to JSON file"
        )
    args = parser.parse_args()

    runtime = get_runtime()
    runtime.register_entity_builder("mapping", create_mapping_entity_builder())
    runtime.build_entity_graph("mapping")
    set_runtime(runtime)
    runtime.print_entity_tree()

    if args.export_scene:
        runtime.export_scene_info(args.export_scene)
        logger.info(f"Scene exported to {args.export_scene}")

    action_program_path = os.path.join(
        os.path.dirname(__file__), "mapping.action")
    logger.info(f"Loading action program from: {action_program_path}")

    try:
        action_names = runtime.load_action_program(action_program_path)
        logger.info(f"Loaded actions: {action_names}")

        runtime.configure_action("test_mapping", mapping_path="/mapping")

        logger.info("Starting test_mapping action...")
        thread = runtime.start_action("test_mapping")
        result = runtime.wait_for_action("test_mapping", timeout=600.0)

        logger.info(f"Mapping test completed with result: {result}")
        logger.info(" Demo completed successfully")
        return 0

    except Exception as e:
        logger.error(f"Demo failed: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)