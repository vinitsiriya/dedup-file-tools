import tempfile
import os
import yaml
from dedup_file_tools_dupes_move.utils import config_loader

def test_load_yaml_config(tmp_path):
    config_data = {
        'job_dir': str(tmp_path / 'job'),
        'job_name': 'testjob',
        'src': str(tmp_path / 'src'),
        'threads': 2
    }
    config_path = tmp_path / 'config.yaml'
    with open(config_path, 'w') as f:
        yaml.dump(config_data, f)
    loaded = config_loader.load_yaml_config(str(config_path))
    assert loaded['job_dir'] == config_data['job_dir']
    assert loaded['job_name'] == config_data['job_name']
    assert loaded['src'] == config_data['src']
    assert loaded['threads'] == config_data['threads']

def test_merge_config_with_args():
    class DummyArgs:
        job_dir = None
        job_name = None
        src = None
        threads = 4
        log_level = 'WARNING'
    parser = type('Parser', (), {'_actions': [
        type('Action', (), {'dest': 'job_dir', 'default': None}),
        type('Action', (), {'dest': 'job_name', 'default': None}),
        type('Action', (), {'dest': 'src', 'default': None}),
        type('Action', (), {'dest': 'threads', 'default': 4}),
        type('Action', (), {'dest': 'log_level', 'default': 'WARNING'}),
    ]})()
    args = DummyArgs()
    config_dict = {
        'job_dir': '/tmp/job',
        'job_name': 'testjob',
        'src': '/tmp/src',
        'threads': 8,
        'log_level': 'DEBUG'
    }
    merged = config_loader.merge_config_with_args(args, config_dict, parser)
    assert merged.job_dir == '/tmp/job'
    assert merged.job_name == 'testjob'
    assert merged.src == '/tmp/src'
    assert merged.threads == 8
    assert merged.log_level == 'DEBUG'  # Should be overwritten by config if not set by user
