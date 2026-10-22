from gr00t.configs.data.embodiment_configs import register_modality_config
from gr00t.data.embodiment_tags import EmbodimentTag
from gr00t.data.types import (
    ActionConfig,
    ActionFormat,
    ActionRepresentation,
    ActionType,
    ModalityConfig,
)


# UNIFIED BiDex-100 joint embodiment: franka (dual FR3 v2) + astribot (S1), both with the
# Sharpa dexterous hand, merged into ONE tag for joint training + inference (the two robots
# share the identical 58D schema; same cameras + column names — see franka/astribot
# configs). State/action layout (58D): arm_joint_position[14] + dex_joint_position[44]
#   - arm_joint_position: right-arm-first [right_q(7), left_q(7)]
#   - dex_joint_position: right-hand(22) + left-hand(22) Sharpa joints
# One embodiment tag -> ONE norm stats entry in the checkpoint (both robots together).
dex_sim_joint_config = {
    "video": ModalityConfig(
        delta_indices=[0],
        modality_keys=["head_color", "left_wrist_color", "right_wrist_color"],
    ),
    "state": ModalityConfig(
        delta_indices=[0],
        modality_keys=["arm_joint_position", "dex_joint_position"],
    ),
    "action": ModalityConfig(
        delta_indices=list(range(0, 16)),
        modality_keys=["arm_joint_position", "dex_joint_position"],
        action_configs=[
            ActionConfig(
                rep=ActionRepresentation.RELATIVE,
                type=ActionType.NON_EEF,
                format=ActionFormat.DEFAULT,
            ),
            ActionConfig(
                rep=ActionRepresentation.RELATIVE,
                type=ActionType.NON_EEF,
                format=ActionFormat.DEFAULT,
            ),
        ],
    ),
    "language": ModalityConfig(
        delta_indices=[0],
        modality_keys=["annotation.human.task_description"],
    ),
}

register_modality_config(dex_sim_joint_config, embodiment_tag=EmbodimentTag.DEX_SIM_JOINT)
