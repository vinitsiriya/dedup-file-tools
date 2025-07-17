from dedup_file_tools_commons.utils.fileops import copy_file, verify_file

def test_copy_file(tmp_path):
    src = tmp_path / "source.txt"
    dst = tmp_path / "dest.txt"
    content = "unit test content"
    src.write_text(content)
    src_checksum, dst_checksum = copy_file(str(src), str(dst))
    assert dst.exists(), f"Destination file {dst} does not exist"
    assert dst.read_text() == content
    assert src_checksum == dst_checksum
    assert verify_file(str(src), str(dst))
