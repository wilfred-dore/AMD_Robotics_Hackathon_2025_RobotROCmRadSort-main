# 🏆 Mission 2: Nuclear Waste Sorting with SmolVLA

## Team 8 - AMD Hackathon Submission

---

## 🎯 Objectif

Trier des déchets radioactifs simulés (3 stabilos de couleurs différentes: **Rose**, **Jaune**, **Vert**) dans les boîtes correspondantes en utilisant un robot **SO-101** contrôlé par un modèle **SmolVLA** (Vision-Language-Action).

**Pourquoi SmolVLA?**
- Comprend les instructions en langage naturel ("Pick the pink nuclear rod")
- Utilise pleinement la puissance du **AMD MI300X**
- État de l'art en robotique VLA

---

## 📊 Dataset Collecté

| Paramètre | Valeur |
|-----------|--------|
| **Repo ID** | `Gowshigan/mission2-nuclear-sorting-combined` |
| **Épisodes totaux** | 60 |
| **Épisodes par couleur** | 20 (Yellow, Pink, Green) |
| **FPS** | 30 |
| **Résolution** | 640x480 |
| **Robot** | SO-101 Follower |
| **Téléopération** | SO-101 Leader |

### Tâches définies:
1. `Sort Yellow to Green Box`
2. `Sort Pink to Yellow Box`
3. `Sort Green to Pink Box`

### Configuration caméras:
- **Front Camera** (index 2): Vue globale de l'espace de travail
- **Wrist Camera** (index 4): Vue du gripper pour précision

---

## 🤖 Modèles Entraînés sur AMD MI300X

| Modèle | Steps | Batch Size | Loss Finale | Status | HuggingFace Hub |
|--------|-------|------------|-------------|--------|-----------------|
| SmolVLA 15k | 15,000 | 8 | ~0.02 | ✅ Terminé | `Gowshigan/smolvla_mission2_15k` |
| SmolVLA 20k | 20,000 | 4 | ~0.015 | ✅ Terminé | `Gowshigan/smolvla_mission2_20k` |
| SmolVLA 50k | 50,000 | 4 | - | 🔄 En cours | - |
| SmolVLA 200k | 200,000 | 32 | - | 🔄 En cours | - |

### Hyperparamètres d'entraînement:
```yaml
policy.type: smolvla
optimizer.lr: 0.0001
scheduler.warmup_steps: 1000
scheduler.decay_steps: 30000
dataset.image_transforms.enable: true
wandb.project: mission2-smolvla
save_freq: 10000  # Checkpoint tous les 10k steps
```

---

## � Problèmes Résolus

### 1. Bug `ValueError: Task cannot be None` sur MI300X

**Cause:** Format incorrect de `tasks.parquet` lors du chargement du dataset.

**Solution:**
```bash
sed -i 's/self.meta.tasks.iloc\[task_idx\].name/self.meta.tasks.iloc[task_idx]["task"]/' /workspace/lerobot/src/lerobot/datasets/lerobot_dataset.py
```

### 2. `FileExistsError: Output directory already exists`

**Solution:** Supprimer le dossier avant relancer ou utiliser `--resume=true`
```bash
rm -rf outputs/train/smolvla_*
```

### 3. Caméras qui freezent pendant l'inférence

**Causes:** Bande passante USB saturée avec 2 caméras

**Solutions appliquées:**
```bash
# Augmenter le buffer USB
echo 1000 | sudo tee /sys/module/usbcore/parameters/usbfs_memory_mb

# Désactiver l'autofocus (réduit le lag)
v4l2-ctl -d /dev/video2 --set-ctrl=focus_automatic_continuous=0
v4l2-ctl -d /dev/video4 --set-ctrl=focus_automatic_continuous=0
```

### 4. Feature Mismatch avec `smolvla_base`

**Problème:** Le modèle pré-entraîné attendait 3 caméras, notre dataset en a 2.

**Solution:** Entraîner from scratch avec `--policy.type=smolvla` au lieu de fine-tuner depuis `--policy.path=lerobot/smolvla_base`

---

## 📁 Scripts Créés

### 1. `test_smolvla_policy.sh` - Test d'inférence
```bash
#!/bin/bash
# Usage: ./test_smolvla_policy.sh [policy] [task] [n_action_steps] [episode_time] [num_episodes]

# Exemples:
./test_smolvla_policy.sh  # Défaut: 15k model
./test_smolvla_policy.sh Gowshigan/smolvla_mission2_20k "Sort Pink to Yellow Box"
./test_smolvla_policy.sh Gowshigan/smolvla_mission2_15k "Sort Yellow to Green Box" 10 60 3
```

### 2. Commande Training MI300X
```python
# Jupyter Notebook sur MI300X
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

### 3. `collect_curriculum_data.py` - Collection de données additionnelles
Script pour collecter des mouvements simples (curriculum learning).

---

## � Suivi W&B

- **Project:** `mission2-smolvla`
- **URL:** https://wandb.ai/gowshigan-upec/mission2-smolvla

---

## 🚀 Architecture Technique

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

## 🎬 Résultats des Tests

### Observations:
- **15k model:** Le robot bouge et montre une compréhension basique de la tâche
- **20k model:** Mouvements plus fluides, mais précision à améliorer
- **n_action_steps=50:** Chunk d'actions prédit, peut causer du retard si environnement change
- **n_action_steps=10:** Plus réactif aux changements

### Améliorations possibles:
1. Plus de données (>100 épisodes)
2. Plus de steps (200k+)
3. Data augmentation plus agressive
4. Curriculum learning (mouvements simples → complexes)

---

## 📦 Fichiers du Projet

```
lerobot/
├── MISSION2_HACKATHON_SUMMARY.md     # Ce document
├── test_smolvla_policy.sh            # Script de test
├── train_smolvla_optimized.sh        # Training multi-config
├── collect_curriculum_data.py        # Collection curriculum
├── sweep_smolvla.yaml               # W&B sweep config
└── src/lerobot/scripts/
    ├── merge_mission2_data.py        # Merge des datasets
    ├── detect_stabilos.py            # Détection couleurs
    └── test_color_isolation.py       # Test isolation couleurs
```

---

## 🏁 Conclusion

**Ce que nous avons accompli:**
- ✅ Collecté 60 épisodes de données de tri
- ✅ Entraîné plusieurs modèles SmolVLA (15k, 20k, 50k, 200k en cours)
- ✅ Testé sur le robot physique SO-101
- ✅ Résolu tous les bugs de compatibilité dataset/modèle
- ✅ Créé des scripts réutilisables

**Leçons apprises:**
- SmolVLA nécessite beaucoup de données et de steps pour les tâches complexes
- La qualité des caméras impacte directement les performances
- Le fine-tuning depuis `smolvla_base` nécessite le même nombre de caméras

**Prochaines étapes:**
1. Terminer le training 200k
2. Tester les checkpoints intermédiaires (50k, 100k, 150k)
3. Démo finale sur le robot

---

## 👥 Équipe

**Team 8**
- Robot: SO-101 (6-DOF)
- GPU Cloud: AMD MI300X
- Framework: LeRobot + SmolVLA
- Hackathon: XHEC AI & Robotics

---

*Document généré le 14 Décembre 2025*
