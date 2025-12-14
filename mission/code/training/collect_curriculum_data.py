#!/usr/bin/env python
"""
Curriculum Learning Data Collection Script
==========================================
Collect varied simple movements before complex sorting tasks.

Mouvements à collecter:
1. Move arm up/down
2. Move arm left/right  
3. Open/close gripper
4. Pick object (simple)
5. Place object (simple)
6. Full sorting task (complex)
"""

import subprocess
import sys
from pathlib import Path

# Configuration
ROBOT_PORT = "/dev/ttyACM0"
ROBOT_TYPE = "so101_follower"
CAMERAS = "{front: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}, wrist: {type: opencv, index_or_path: 2, width: 640, height: 480, fps: 30}}"
BASE_DIR = Path.home() / "lerobot" / "curriculum_data"

# Curriculum tasks - from simple to complex
CURRICULUM_TASKS = [
    {
        "name": "move_arm_up",
        "task": "Move the robot arm upward",
        "episodes": 5,
        "time_s": 10,
    },
    {
        "name": "move_arm_down", 
        "task": "Move the robot arm downward",
        "episodes": 5,
        "time_s": 10,
    },
    {
        "name": "open_gripper",
        "task": "Open the gripper fully",
        "episodes": 5,
        "time_s": 5,
    },
    {
        "name": "close_gripper",
        "task": "Close the gripper fully",
        "episodes": 5,
        "time_s": 5,
    },
    {
        "name": "pick_object",
        "task": "Pick up an object from the table",
        "episodes": 10,
        "time_s": 15,
    },
    {
        "name": "place_object",
        "task": "Place an object on the table",
        "episodes": 10,
        "time_s": 15,
    },
    {
        "name": "sort_yellow_green",
        "task": "Pick up the yellow stabilo and place it in the green box",
        "episodes": 10,
        "time_s": 25,
    },
    {
        "name": "sort_pink_yellow",
        "task": "Pick up the pink stabilo and place it in the yellow box", 
        "episodes": 10,
        "time_s": 25,
    },
    {
        "name": "sort_green_pink",
        "task": "Pick up the green stabilo and place it in the pink box",
        "episodes": 10,
        "time_s": 25,
    },
]


def collect_task(task_config: dict) -> None:
    """Collect data for a single curriculum task."""
    name = task_config["name"]
    task = task_config["task"]
    episodes = task_config["episodes"]
    time_s = task_config["time_s"]
    
    output_dir = BASE_DIR / name
    repo_id = f"Gowshigan/curriculum_{name}"
    
    print(f"\n{'='*60}")
    print(f"📹 Collecting: {name}")
    print(f"   Task: {task}")
    print(f"   Episodes: {episodes}")
    print(f"   Time per episode: {time_s}s")
    print(f"{'='*60}\n")
    
    cmd = [
        "lerobot-record",
        f"--robot.type={ROBOT_TYPE}",
        f"--robot.port={ROBOT_PORT}",
        "--robot.id=curriculum_robot",
        f"--robot.cameras={CAMERAS}",
        f"--dataset.repo_id={repo_id}",
        f"--dataset.root={output_dir}",
        f"--dataset.episode_time_s={time_s}",
        f"--dataset.num_episodes={episodes}",
        f"--dataset.single_task={task}",
        "--dataset.push_to_hub=false",
    ]
    
    print(f"Running: {' '.join(cmd[:5])}...")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Completed: {name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {name} - {e}")
    except KeyboardInterrupt:
        print(f"\n⏸️  Interrupted: {name}")
        sys.exit(1)


def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║           CURRICULUM LEARNING DATA COLLECTION            ║
    ║                                                          ║
    ║  Collect simple → complex movements for better training  ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Create base directory
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Data will be saved to: {BASE_DIR}")
    print(f"📊 Total tasks: {len(CURRICULUM_TASKS)}")
    total_episodes = sum(t["episodes"] for t in CURRICULUM_TASKS)
    print(f"📹 Total episodes: {total_episodes}")
    
    input("\n⏎ Press Enter to start data collection...")
    
    for i, task_config in enumerate(CURRICULUM_TASKS, 1):
        print(f"\n[{i}/{len(CURRICULUM_TASKS)}] ", end="")
        collect_task(task_config)
    
    print(f"\n{'='*60}")
    print("🎉 ALL DATA COLLECTION COMPLETE!")
    print(f"📁 Data saved to: {BASE_DIR}")
    print(f"{'='*60}\n")
    
    # Print merge instructions
    print("📝 Next steps:")
    print("1. Merge all curriculum datasets:")
    print("   python merge_curriculum_data.py")
    print("2. Upload to HuggingFace:")
    print("   huggingface-cli upload Gowshigan/curriculum-combined ...")
    print("3. Train SmolVLA on curriculum data:")
    print("   lerobot-train --dataset.repo_id=Gowshigan/curriculum-combined ...")


if __name__ == "__main__":
    main()
