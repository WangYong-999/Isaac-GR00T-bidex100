from gr00t.configs.data.embodiment_configs import register_modality_config
from gr00t.data.embodiment_tags import EmbodimentTag
from gr00t.data.types import (
    ActionConfig,
    ActionFormat,
    ActionRepresentation,
    ActionType,
    ModalityConfig,
)


# BiDex-100 franka (dual_fr3v2_sharpa) sim data, CAMERA-EE control, 58D.
# State/action layout (58D): abs_end_effector_camera[14] + dex_joint_position[44]
#   - abs_end_effector_camera: link8 EE in the head-cam optical frame (right+left),
#     produced by examples/franka_build_arena_fk.py.
#   - dex_joint_position: right-hand(22) + left-hand(22) Sharpa joints.
# ABSOLUTE (NO delta), NON_EEF opaque passthrough. 3 color cameras.
franka_dex_sim_camera_ee_config = {
    "video": ModalityConfig(
        delta_indices=[0],
        modality_keys=["head_color", "left_wrist_color", "right_wrist_color"],
    ),
    "state": ModalityConfig(
        delta_indices=[0],
        modality_keys=["abs_end_effector_camera", "dex_joint_position"],
    ),
    "action": ModalityConfig(
        delta_indices=list(range(0, 16)),
        modality_keys=["abs_end_effector_camera", "dex_joint_position"],
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
    franka_dex_sim_camera_ee_config, embodiment_tag=EmbodimentTag.FRANKA_DEX_SIM_CAMERA_EE
)
