"""Combined modality config for MIXED-ALL GR00T training (franka + astribot, 58D dual).
franka & astribot dex_sim_ee configs are identical (same dims/columns); importing
both registers BOTH embodiment tags so a multi-embodiment datasets_config (2 entries)
trains both robots in one run via a single --modality-config-path.
Loaded by gr00t.experiment.launch_finetune.load_modality_config (adds this dir to sys.path)."""
