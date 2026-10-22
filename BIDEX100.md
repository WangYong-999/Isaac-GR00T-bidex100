# BiDex-100 · GR00T-N1.7

[Document](https://bidex-100.github.io/BiDex-100/document.html) · [Benchmark code](https://github.com/robbyant-research/BiDex-100)


### Create the environment

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone https://github.com/WangYong-999/Isaac-GR00T-bidex100.git
cd Isaac-GR00T-bidex100
python -m pip install -U uv
uv sync --python 3.12 --all-extras
```

For an NVIDIA dGPU, use a CUDA-compatible driver and the dependency setup in
`scripts/deployment/dgpu/install_deps.sh`. Download the GR00T-N1.7 pretrained
model separately. The BiDex-100 integration keeps the upstream installation
manifests and training loop.

### Prepare data and train

The preparation utility writes the state/action/camera mapping required by
GR00T to each task's `meta/modality.json`. It uses the **LeRobot v2.1** download.
The joint embodiment is shared by both robots, giving one normalization profile
for the co-trained policy.

```bash
uv run python examples/BiDex-100/prepare_training.py \
  --data-root /absolute/path/to/BiDex-100/downloads/BiDex-100/datasets/lerobotv21

NUM_GPUS=8 MAX_STEPS=400000 GLOBAL_BATCH_SIZE=256 \
  uv run bash examples/BiDex-100/train.sh \
    --data-root /absolute/path/to/BiDex-100/downloads/BiDex-100/datasets/lerobotv21 \
    --base-model-path /absolute/path/to/GR00T-N1.7-3B \
    --output-dir /absolute/path/to/outputs/gr00t-bidex
```

`examples/BiDex-100/dex_sim_joint_config.py` defines the three RGB cameras,
58-D relative arm/hand targets and native 16-step action chunk. The persisted
`dex_sim_joint` identifier is retained for compatibility with the benchmark's
existing checkpoint loader; the integration is for BiDex-100.

### Evaluate

From the **BiDex-100** repository:

```bash
export MODEL_REPO=/absolute/path/to/Isaac-GR00T-bidex100
export MODEL_PY="$MODEL_REPO/.venv/bin/python"
export MODEL_CKPT=/absolute/path/to/outputs/gr00t-bidex/checkpoint-400000
export BIDEX_LEADERBOARD_ROOT=/absolute/path/to/evaluation-output

MID_OVERRIDE=gr00t_smoke MODEL_GPUS=0 RENDER_GPUS=0 \
  bash scripts/evaluation/run_vec_models_eval.sh gr00t smoke
```
