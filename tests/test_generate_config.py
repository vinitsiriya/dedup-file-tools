import io
import os
import tempfile
import builtins
import pytest
from dedup_file_tools_fs_copy.main import main

def test_generate_config_interactive(monkeypatch):
    # Simulate user input for all prompts
    user_inputs = [
        'test-job-dir',    # job_dir
        'test-job',        # job_name
        'src1,src2',       # src
        'dst1,dst2',       # dst
        '8',              # threads
        'DEBUG',          # log_level
        'y',              # confirm write
        'test-config.yaml' # output file
    ]
    input_iter = iter(user_inputs)
    monkeypatch.setattr('builtins.input', lambda _: next(input_iter))
    # Capture stdout
    buf = io.StringIO()
    monkeypatch.setattr('sys.stdout', buf)
    # Run the command
    main(['generate-config'])
    output = buf.getvalue()
    # Check that the config file was written
    assert os.path.exists('test-config.yaml')
    with open('test-config.yaml') as f:
        content = f.read()
        assert 'job_dir: test-job-dir' in content
        assert 'job_name: test-job' in content
        assert 'src:' in content
        assert 'dst:' in content
        assert 'threads: 8' in content
        assert 'log_level: DEBUG' in content
    os.remove('test-config.yaml')
    # Check output contains summary and confirmation
    assert 'Config summary:' in output
    assert 'Config written to test-config.yaml' in output
