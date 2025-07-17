import os
import tempfile
import yaml
import subprocess
import sys
import pytest

def make_yaml_config(tmp_path, config_dict):
    config_path = tmp_path / "test_config.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config_dict, f)
    return str(config_path)

def run_cli_with_config(config_path, extra_args=None):
    cmd = [sys.executable, "-m", "fs_copy_tool.main", "one-shot", "--job-dir", "testjob", "--job-name", "testjob"]
    if extra_args:
        cmd += extra_args
    cmd = cmd[:1] + ["-c", config_path] + cmd[1:]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result


def test_invalid_yaml(tmp_path):
    config_path = tmp_path / "bad.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(": this is not valid yaml ::::\n")
    cmd = [sys.executable, "-m", "fs_copy_tool.main", "-c", str(config_path), "one-shot", "--job-dir", "job", "--job-name", "job"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode != 0
    assert "yaml" in result.stderr.lower() or "error" in result.stderr.lower()
