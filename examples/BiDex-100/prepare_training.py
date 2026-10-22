"""Prepare the public BiDex-100 task datasets for GR00T co-training."""

import argparse
import os
from pathlib import Path

from write_modality_json import write_for_task


SUITES = (
    "Generalization",
    "Instruction_Following",
    "Limited_Demonstrations",
    "Long_Horizon",
    "Memory",
)


def task_paths(root):
    return [
        info.parent.parent.resolve()
        for suite in SUITES
        for info in sorted((root / suite).glob("*/meta/info.json"))
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument(
        "--print-paths", action="store_true", help="Read-only, path-separated trainer argument"
    )
    args = parser.parse_args()
    paths = task_paths(args.data_root)
    if not paths:
        parser.error(
            "No BiDex-100 task datasets found; expected <root>/<capability>/<task>/meta/info.json"
        )
    if args.print_paths:
        print(os.pathsep.join(map(str, paths)))
        return
    for task in paths:
        if not write_for_task(task, "joint"):
            parser.error(f"Dataset schema is incompatible with 58-D joint training: {task}")
    print(f"Prepared {len(paths)} task datasets for the shared BiDex-100 joint embodiment")


if __name__ == "__main__":
    main()
