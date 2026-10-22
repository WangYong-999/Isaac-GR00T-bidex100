"""Modality config for MIXED-ALL GR00T training (UNIFIED single embodiment, 58D dual).
franka and astribot share the identical 58D joint schema, so ALL tasks (both robots)
train under the ONE EmbodimentTag.DEX_SIM_JOINT embodiment -> one norm stats entry.
Loaded by gr00t.experiment.launch_finetune.load_modality_config (adds this dir to sys.path)."""
