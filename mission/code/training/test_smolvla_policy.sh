#!/bin/bash
# Script pour tester les modèles SmolVLA sur le robot

# Configuration par défaut
POLICY_PATH="${1:-Gowshigan/smolvla_mission2_15k}"
TASK="${2:-Sort Yellow to Green Box}"
N_ACTION_STEPS="${3:-50}"
EPISODE_TIME="${4:-60}"
NUM_EPISODES="${5:-2}"




# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   SmolVLA Policy Test${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Policy:${NC} $POLICY_PATH"
echo -e "${YELLOW}Task:${NC} $TASK"
echo -e "${YELLOW}N Action Steps:${NC} $N_ACTION_STEPS"
echo -e "${YELLOW}Episode Time:${NC} ${EPISODE_TIME}s"
echo -e "${YELLOW}Num Episodes:${NC} $NUM_EPISODES"
echo ""

# Nettoyer le dossier d'évaluation
rm -rf eval_smolvla_test

# Lancer le test
lerobot-record \
  --robot.type=so101_follower \
  --robot.port=/dev/ttyACM0 \
  --robot.id=my_awesome_follower_arm \
  --robot.calibration_dir=/home/team8/.cache/huggingface/lerobot/calibration/robots/so101_follower \
  --robot.cameras="{front: {type: opencv, index_or_path: 2, width: 320, height: 240, fps: 15}, wrist: {type: opencv, index_or_path: 4, width: 320, height: 240, fps: 15}}" \
  --teleop.type=so101_leader \
  --teleop.port=/dev/ttyACM1 \
  --teleop.id=my_awesome_leader_arm \
  --teleop.calibration_dir=/home/team8/.cache/huggingface/lerobot/calibration/teleoperators/so101_leader \
  --policy.path="$POLICY_PATH" \
  --policy.device=cuda \
  --policy.n_action_steps="$N_ACTION_STEPS" \
  --display_data=true \
  --dataset.repo_id=Gowshigan/eval_smolvla_test \
  --dataset.root=./eval_smolvla_test \
  --dataset.episode_time_s="$EPISODE_TIME" \
  --dataset.num_episodes="$NUM_EPISODES" \
  --dataset.reset_time_s=10 \
  --dataset.single_task="$TASK" \
  --dataset.push_to_hub=false
