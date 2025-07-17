import yaml
import os

def interactive_config_generator():
    print("\nWelcome to the Interactive Config Generator!\n")
    config = {}
    # Example required fields (customize as needed)
    config['job_dir'] = input("Enter the path to the job directory: ").strip()
    config['job_name'] = input("Enter the job name: ").strip()
    config['src'] = input("Enter source volume root(s) (comma-separated): ").strip().split(',')
    config['dst'] = input("Enter destination volume root(s) (comma-separated): ").strip().split(',')
    threads = input("Number of threads for parallel operations [4]: ").strip()
    config['threads'] = int(threads) if threads else 4
    log_level = input("Set logging level [INFO]: ").strip()
    config['log_level'] = log_level if log_level else 'INFO'
    # Add more prompts as needed for other config fields
    print("\nConfig summary:")
    print(yaml.dump(config, sort_keys=False, default_flow_style=False))
    confirm = input("Write this config to file? [y/N]: ").strip().lower()
    if confirm == 'y':
        out_path = input("Enter output YAML file path [config.yaml]: ").strip() or 'config.yaml'
        with open(out_path, 'w') as f:
            yaml.dump(config, f, sort_keys=False, default_flow_style=False)
        print(f"Config written to {out_path}")
    else:
        print("Aborted. No file written.")
