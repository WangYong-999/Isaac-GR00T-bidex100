#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DATA_ROOT=""
EXTRA_ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --data-root) DATA_ROOT="${2:?--data-root requires a value}"; shift 2 ;;
    -h|--help)
      echo 'Usage: bash examples/BiDex-100/train.sh --data-root <lerobotv21> --base-model-path <checkpoint> --output-dir <directory>'
      exit 0 ;;
    *) EXTRA_ARGS+=("$1"); shift ;;
  esac
done
[[ -n "$DATA_ROOT" ]] || { echo 'Missing --data-root' >&2; exit 2; }
DATASET_PATH="$(python "$SCRIPT_DIR/prepare_training.py" --data-root "$DATA_ROOT" --print-paths)"
export NUM_GPUS="${NUM_GPUS:-8}"
export MAX_STEPS="${MAX_STEPS:-400000}"
export GLOBAL_BATCH_SIZE="${GLOBAL_BATCH_SIZE:-256}"
export USE_WANDB="${USE_WANDB:-0}"
cd "$REPO_ROOT"
exec bash examples/finetune.sh \
  --dataset-path "$DATASET_PATH" \
  --embodiment-tag BIDEX_JOINT \
  --modality-config-path "$SCRIPT_DIR/dex_sim_joint_config.py" \
  "${EXTRA_ARGS[@]}"
