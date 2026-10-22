"""Single-arm (29D) Articulated_Object modality config. Reuses the franka dual-arm
group dict (modality_keys identical); the 29D slice comes from the per-task
modality.camera_ee_left/_right.json variant. Registered under a DEDICATED tag so GR00T
gives it its own action adapter (adapted to 29D), not the 58D franka_dex_sim_camera_ee one."""

from franka_dex_sim_camera_ee_config import franka_dex_sim_camera_ee_config
from gr00t.configs.data.embodiment_configs import register_modality_config
from gr00t.data.embodiment_tags import EmbodimentTag


register_modality_config(
    franka_dex_sim_camera_ee_config,
    embodiment_tag=EmbodimentTag.FRANKA_DEX_SIM_SINGLE_ARM_CAMERA_EE,
)
