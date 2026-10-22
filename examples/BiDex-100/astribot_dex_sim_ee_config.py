from gr00t.configs.data.embodiment_configs import register_modality_config
from gr00t.data.embodiment_tags import EmbodimentTag
from gr00t.data.types import (
    ActionConfig,
    ActionFormat,
    ActionRepresentation,
    ActionType,
    ModalityConfig,
)


# BiDex-100 astribot (astribot_s1_fixed_sharpa) sim data, EE control, 58D.
# State/action layout (58D): abs_end_effector[14] + dex_joint_position[44]
#   - abs_end_effector: [right_xyz(3)+right_quat_wxyz(4), left_xyz(3)+left_quat_wxyz(4)]
#   - dex_joint_position: right-hand(22) + left-hand(22) Sharpa joints
# ABSOLUTE ee (NO delta): the 14D abs_end_effector is pos+quat; quaternions cannot be
# element-wise delta-subtracted, so ee stays absolute and the env.step ee mode consumes
# the absolute abs_end_effector directly. NON_EEF/ABSOLUTE/DEFAULT = opaque passthrough
# (abs_end_effector is not a standard 9D EEF, so opaque-joint is the safe choice).
# 3 color cameras: head_color, left_wrist_color, right_wrist_color.
astribot_dex_sim_ee_config = {
    "video": ModalityConfig(
        delta_indices=[0],
        modality_keys=["head_color", "left_wrist_color", "right_wrist_color"],
    ),
    "state": ModalityConfig(
        delta_indices=[0],
        modality_keys=["abs_end_effector", "dex_joint_position"],
    ),
    "action": ModalityConfig(
        delta_indices=list(range(0, 16)),
        modality_keys=["abs_end_effector", "dex_joint_position"],
        action_configs=[
            ActionConfig(
                rep=ActionRepresentation.RELATIVE,
                type=ActionType.EEF_XYZ_QUAT_XYZW,
                format=ActionFormat.DEFAULT,
            ),
            ActionConfig(
                rep=ActionRepresentation.ABSOLUTE,
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

register_modality_config(
    astribot_dex_sim_ee_config, embodiment_tag=EmbodimentTag.ASTRIBOT_DEX_SIM_EE
)
