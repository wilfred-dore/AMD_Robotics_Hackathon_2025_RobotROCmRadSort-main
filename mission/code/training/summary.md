# 🏆 Mission 2: Nuclear Waste Sorting with SmolVLA

## Team 8 - AMD Hackathon Submission

---

## 🎯 Objective

Sort simulated radioactive waste (3 different colored highlighters: **Pink**, **Yellow**, **Green**) into corresponding boxes using a **SO-101** robot controlled by a **SmolVLA** (Vision-Language-Action) model.

**Why SmolVLA?**
- Understands natural language instructions ("Pick the pink nuclear rod")
- Fully leverages **AMD MI300X** computing power
- State-of-the-art in VLA robotics

---

## 📊 Collected Dataset

| Parameter | Value |
|-----------|-------|
| **Repo ID** | `Gowshigan/mission2-nuclear-sorting-combined` |
| **Total Episodes** | 60 |
| **Episodes per color** | 20 (Yellow, Pink, Green) |
| **FPS** | 30 |
| **Resolution** | 640x480 |
| **Robot** | SO-101 Follower |
| **Teleoperation** | SO-101 Leader |

### Defined Tasks:
1. `Sort Yellow to Green Box`
2. `Sort Pink to Yellow Box`
3. `Sort Green to Pink Box`

### Camera Configuration:
- **Front Camera** (index 2): Global workspace view
- **Wrist Camera** (index 4): Gripper view for precision

---

## 🤖 Models Trained on AMD MI300X

| Model | Steps | Batch Size | Final Loss | Status | HuggingFace Hub |
|-------|-------|------------|------------|--------|-----------------|
| SmolVLA 15k | 15,000 | 8 | ~0.02 | ✅ Done | `Gowshigan/smolvla_mission2_15k` |
| SmolVLA 20k | 20,000 | 4 | ~0.015 | ✅ Done | `Gowshigan/smolvla_mission2_20k` |
| SmolVLA 50k | 50,000 | 4 | - | 🔄 In Progress | - |
| SmolVLA 200k | 200,000 | 32 | - | 🔄 In Progress | - |

### Training Hyperparameters:
```yaml
policy.type: smolvla
optimizer.lr: 0.0001
scheduler.warmup_steps: 1000
scheduler.decay_steps: 30000
dataset.image_transforms.enable: true
wandb.project: mission2-smolvla
save_freq: 10000  # Checkpoint every 10k steps
```

---

## 🔧 Issues Resolved

### 1. `ValueError: Task cannot be None` on MI300X

**Cause:** Incorrect `tasks.parquet` format when loading dataset.

**Solution:**
```bash
sed -i 's/self.meta.tasks.iloc\[task_idx\].name/self.meta.tasks.iloc[task_idx]["task"]/' /workspace/lerobot/src/lerobot/datasets/lerobot_dataset.py
```

### 2. `FileExistsError: Output directory already exists`

**Solution:** Delete folder before restarting or use `--resume=true`
```bash
rm -rf outputs/train/smolvla_*
```

### 3. Cameras freezing during inference

**Causes:** USB bandwidth saturated with 2 cameras

**Applied Solutions:**
```bash
# Increase USB buffer
echo 1000 | sudo tee /sys/module/usbcore/parameters/usbfs_memory_mb

# Disable autofocus (reduces lag)
v4l2-ctl -d /dev/video2 --set-ctrl=focus_automatic_continuous=0
v4l2-ctl -d /dev/video4 --set-ctrl=focus_automatic_continuous=0
```

### 4. Feature Mismatch with `smolvla_base`

**Problem:** Pre-trained model expected 3 cameras, our dataset has 2.

**Solution:** Train from scratch with `--policy.type=smolvla` instead of fine-tuning from `--policy.path=lerobot/smolvla_base`

---

## 📁 Created Scripts

### 1. `test_smolvla_policy.sh` - Inference Testing
```bash
#!/bin/bash
# Usage: ./test_smolvla_policy.sh [policy] [task] [n_action_steps] [episode_time] [num_episodes]

# Examples:
./test_smolvla_policy.sh  # Default: 15k model
./test_smolvla_policy.sh Gowshigan/smolvla_mission2_20k "Sort Pink to Yellow Box"
./test_smolvla_policy.sh Gowshigan/smolvla_mission2_15k "Sort Yellow to Green Box" 10 60 3
```

### 2. MI300X Training Command
```python
# Jupyter Notebook on MI300X
!rm -rf outputs/train/smolvla_200k
!sed -i 's/self.meta.tasks.iloc\[task_idx\].name/self.meta.tasks.iloc[task_idx]["task"]/' /workspace/lerobot/src/lerobot/datasets/lerobot_dataset.py

!lerobot-train \
  --policy.type=smolvla \
  --dataset.repo_id=Gowshigan/mission2-nuclear-sorting-combined \
  --batch_size=32 \
  --steps=200000 \
  --save_freq=10000 \
  --output_dir=outputs/train/smolvla_200k \
  --job_name=smolvla_200k \
  --policy.device=cuda \
  --dataset.image_transforms.enable=true \
  --wandb.enable=true \
  --wandb.project=mission2-smolvla
```

### 3. `collect_curriculum_data.py` - Additional Data Collection
Script for collecting simple movements (curriculum learning).

---

## 📈 W&B Tracking

- **Project:** `mission2-smolvla`
- **URL:** https://wandb.ai/gowshigan-upec/mission2-smolvla

---

## 🚀 Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     SmolVLA Pipeline                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐     ┌──────────┐     ┌──────────────────────┐│
│  │ Front    │────▶│          │     │                      ││
│  │ Camera   │     │  SmolVLA │────▶│  Action (6 DOF)      ││
│  └──────────┘     │  Model   │     │  - shoulder_pan      ││
│                   │          │     │  - shoulder_lift     ││
│  ┌──────────┐     │ (VLM +   │     │  - elbow_flex        ││
│  │ Wrist    │────▶│ Diffusion│     │  - wrist_flex        ││
│  │ Camera   │     │  Expert) │     │  - wrist_roll        ││
│  └──────────┘     │          │     │  - gripper           ││
│                   └──────────┘     └──────────────────────┘│
│  ┌──────────┐           ▲                                  │
│  │ Task     │───────────┘                                  │
│  │ Prompt   │  "Sort Yellow to Green Box"                  │
│  └──────────┘                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎬 Test Results

### Observations:
- **15k model:** Robot moves and shows basic task understanding
- **20k model:** Smoother movements, but precision needs improvement
- **n_action_steps=50:** Action chunk predicted, may cause delay if environment changes
- **n_action_steps=10:** More reactive to changes

### Possible Improvements:
1. More data (>100 episodes)
2. More steps (200k+)
3. More aggressive data augmentation
4. Curriculum learning (simple → complex movements)

---

## 📦 Project Files

```
lerobot/
├── MISSION2_HACKATHON_SUMMARY.md     # This document
├── test_smolvla_policy.sh            # Test script
├── train_smolvla_optimized.sh        # Multi-config training
├── collect_curriculum_data.py        # Curriculum collection
├── sweep_smolvla.yaml               # W&B sweep config
└── src/lerobot/scripts/
    ├── merge_mission2_data.py        # Dataset merging
    ├── detect_stabilos.py            # Color detection
    └── test_color_isolation.py       # Color isolation testing
```

---

## 🏁 Conclusion

**What we accomplished:**
- ✅ Collected 60 episodes of sorting data
- ✅ Trained multiple SmolVLA models (15k, 20k, 50k, 200k in progress)
- ✅ Tested on physical SO-101 robot
- ✅ Resolved all dataset/model compatibility bugs
- ✅ Created reusable scripts

**Lessons learned:**
- SmolVLA requires significant data and training steps for complex tasks
- Camera quality directly impacts performance
- Fine-tuning from `smolvla_base` requires matching camera count

**Next steps:**
1. Complete 200k training
2. Test intermediate checkpoints (50k, 100k, 150k)
3. Final demo on robot

---

## 👥 Team

**Team 8**
- Robot: SO-101 
- Cloud GPU: AMD MI300X
- Framework: LeRobot + SmolVLA
- Hackathon: AMD Hackathon 2025

---


