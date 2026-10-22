#!/usr/bin/env python3
"""Write `meta/modality.json` into every BiDex-100 data_fixed task dir.

GR00T's LeRobot loader requires a meta/modality.json next to info.json that
declares how the state/action arrays split into named groups (start/end within
the source column), which video/annotation keys to use.

BiDex-100 data stores state/action as SEPARATE columns (not a single
observation.state/action), so each group gets its own `original_key`. The qc
{astribot,franka} datasets share the same column schema; we expose a 58D
`--variant`:

  --variant joint  (58D = arm_joint_position[14] + dex_joint_position[44])
  --variant ee     (58D = abs_end_effector[14]   + dex_joint_position[44])

The variant MUST match the embodiment config's state/action `modality_keys`.

Usage:
    python examples/BiDex-100/write_modality_json.py \
        --root /path/to/BiDex-100/datasets/lerobotv21 \
        --variant joint
"""

import argparse
import json
from pathlib import Path


MODALITY = {
    "state": {
        "arm_joint_position": {
            "start": 0,
            "end": 14,
            "original_key": "observation.states.arm_joint_position",
        },
        "dex_joint_position": {
            "start": 0,
            "end": 44,
            "original_key": "observation.states.dex_joint_position",
        },
        "abs_end_effector": {
            "start": 0,
            "end": 14,
            "original_key": "observation.states.abs_end_effector",
        },
        "abs_end_effector_camera": {
            "start": 0,
            "end": 14,
            "original_key": "observation.states.abs_end_effector_camera",
        },
    },
    "action": {
        "arm_joint_position": {"start": 0, "end": 14, "original_key": "actions.arm_joint_position"},
        "dex_joint_position": {"start": 0, "end": 44, "original_key": "actions.dex_joint_position"},
        "abs_end_effector": {"start": 0, "end": 14, "original_key": "actions.abs_end_effector"},
        "abs_end_effector_camera": {
            "start": 0,
            "end": 14,
            "original_key": "actions.abs_end_effector_camera",
        },
    },
    "video": {
        "head_color": {"original_key": "observation.images.head_color"},
        "left_wrist_color": {"original_key": "observation.images.left_wrist_color"},
        "right_wrist_color": {"original_key": "observation.images.right_wrist_color"},
    },
    "annotation": {
        "human.task_description": {"original_key": "task_index"},
    },
}

# 58D group sets (joint = arm+dex; ee = ee+dex; camera_ee = camera_ee+dex). The
# chosen variant must match the embodiment config's state/action `modality_keys` so
# the parquet columns, modality.json, and the modality config agree on action_dim==58.
_ARM_GROUP = {"arm_joint_position"}  # 14D arm (joint variant)
_EE_GROUP = {"abs_end_effector"}  # 14D ee, robot base frame (ee variant)
_CAMERA_EE_GROUP = {"abs_end_effector_camera"}  # 14D ee, head-cam optical frame (camera_ee)
_DEX_GROUP = {"dex_joint_position"}  # 44D dex (always present)


def build_modality(variant: str, arm: str | None = None) -> dict:
    """Return a modality dict for the given variant, optionally sliced to ONE active arm
    (29D): arm/ee group -> 7, dex -> 22. arm='left' slices [7:14]/[22:44]; 'right' [0:7]/[0:22].
    Without arm the standard 58D (arm/ee 14 + dex 44) is returned."""
    if variant == "joint":
        keep = _ARM_GROUP | _DEX_GROUP
    elif variant == "ee":
        keep = _EE_GROUP | _DEX_GROUP
    elif variant == "camera_ee":
        keep = _CAMERA_EE_GROUP | _DEX_GROUP
    else:
        raise ValueError(f"unknown variant {variant!r}; expected 'joint'|'ee'|'camera_ee'")
    modality = json.loads(json.dumps(MODALITY))  # deep copy
    for mod in ("state", "action"):
        for g in list(modality[mod].keys()):
            if g not in keep:
                del modality[mod][g]
    if arm in ("left", "right"):
        arm_start, arm_end = (0, 7) if arm == "right" else (7, 14)
        dex_start, dex_end = (0, 22) if arm == "right" else (22, 44)
        for mod in ("state", "action"):
            for g, spec in modality[mod].items():
                if g == "dex_joint_position":
                    spec["start"], spec["end"] = dex_start, dex_end
                elif g in ("arm_joint_position", "abs_end_effector", "abs_end_effector_camera"):
                    spec["start"], spec["end"] = arm_start, arm_end
    return modality


def write_for_task(task_dir: Path, variant: str, arm: str | None = None) -> bool:
    meta = task_dir / "meta"
    info_p = meta / "info.json"
    if not info_p.exists():
        print(f"  SKIP {task_dir} (no meta/info.json)")
        return False
    info = json.loads(info_p.read_text())
    feats = set(info.get("features", {}).keys())

    # Validate all original_keys exist in features; drop missing video cams.
    modality = build_modality(variant, arm)
    for mod in ("state", "action"):
        for g, spec in list(modality[mod].items()):
            if spec["original_key"] not in feats:
                print(f"  WARN {task_dir}: missing {spec['original_key']} in features")
                return False
    for cam in list(modality["video"].keys()):
        if modality["video"][cam]["original_key"] not in feats:
            print(f"  WARN {task_dir}: dropping missing cam {cam}")
            del modality["video"][cam]
    if "task_index" not in feats:
        print(f"  WARN {task_dir}: missing task_index")
        return False

    variant_name = f"{variant}_{arm}" if arm else variant
    if arm:
        # Single-arm (29D): write ONLY the variant-specific file so the default 58D
        # modality.json (joint/ee/camera_ee) is left intact for dual training.
        out_v = meta / f"modality.{variant_name}.json"
        out_v.write_text(json.dumps(modality, indent=4) + "\n")
        print(f"  wrote {out_v.name} (single-arm 29D, arm={arm})")
    else:
        out = meta / "modality.json"
        out.write_text(json.dumps(modality, indent=4) + "\n")
        out_v = meta / f"modality.{variant}.json"
        out_v.write_text(json.dumps(modality, indent=4) + "\n")
        print(f"  wrote {out} + {out_v.name} (variant={variant})")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="dir containing <suite>/<task>/ data dirs")
    ap.add_argument(
        "--variant",
        choices=["joint", "ee", "camera_ee"],
        default="joint",
        help="58D group set: joint=arm+dex, ee=abs_end_effector+dex, "
        "camera_ee=abs_end_effector_camera+dex",
    )
    ap.add_argument(
        "--arm",
        choices=["left", "right"],
        default=None,
        help="if set, write a single-arm 29D variant (arm/ee group -> 7, dex -> 22) "
        "as modality.<variant>_<arm>.json; leaves the 58D default untouched",
    )
    args = ap.parse_args()
    root = Path(args.root)
    # dexsimbench_data layout is <root>/<category>/<task>; skip init_states/ (eval-only).
    tasks = sorted(p for p in root.glob("*/*") if p.is_dir() and p.parent.name != "init_states")
    print(f"Found {len(tasks)} task dirs under {root} (variant={args.variant} arm={args.arm})")
    ok = 0
    for t in tasks:
        if write_for_task(t, args.variant, args.arm):
            ok += 1
    print(f"\nDone: {ok}/{len(tasks)} tasks (variant={args.variant} arm={args.arm})")


if __name__ == "__main__":
    main()
