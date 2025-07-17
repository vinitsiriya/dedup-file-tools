import yaml
import argparse
import os

def load_yaml_config(config_path):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"YAML config file not found: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def merge_config_with_args(args, config_dict, parser):
    """
    Update the argparse.Namespace `args` with values from config_dict,
    but only for arguments that are still set to their default values.
    CLI args always take precedence.
    """
    for action in parser._actions:
        dest = action.dest
        if dest == 'help' or dest == 'config':
            continue
        if hasattr(args, dest):
            current_val = getattr(args, dest)
            # Only update if current value is None or default
            if (current_val is None or current_val == action.default) and dest in config_dict:
                setattr(args, dest, config_dict[dest])
    return args
