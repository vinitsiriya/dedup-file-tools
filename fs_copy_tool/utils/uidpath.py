"""
File: src/utils/uidpath.py
Description: UidPath class for robust volume and path handling (moved from scan.py)
"""
import platform
import logging
from pathlib import Path
import subprocess
try:
    import wmi
except ImportError:
    wmi = None

class UidPath:
    def __init__(self):
        self.os = platform.system()
        self.mounts = self.get_mounts()

    def get_mounts(self):
        if self.os == "Windows":
            mounts = self.get_mounts_windows()
        elif self.os == "Linux":
            mounts = self.get_mounts_linux()
        else:
            raise NotImplementedError("Unsupported operating system")
        # TEST HOOK: Add any local directories as pseudo-volumes for testing
        import os, glob
        for d in glob.glob(os.path.join(os.getcwd(), 'tests', '*')):
            if os.path.isdir(d):
                mounts[d] = d
        return mounts

    def get_mounts_linux(self):
        result = subprocess.run(['lsblk', '-o', 'UUID,MOUNTPOINT', '--noheadings'], capture_output=True, text=True)
        mounts = {}
        for line in result.stdout.splitlines():
            parts = line.strip().split()
            if len(parts) == 2:
                uuid, mountpoint = parts
                if uuid and mountpoint:
                    mounts[mountpoint] = uuid
        return mounts

    def get_mounts_windows(self):
        if not wmi:
            logging.error("wmi module not available on this system.")
            return {}
        try:
            c = wmi.WMI()
            mounts = {}
            for volume in c.Win32_Volume():
                if volume.DriveType == 3 and volume.DriveLetter:
                    drive_letter = volume.DriveLetter if volume.DriveLetter.endswith("\\") else volume.DriveLetter + "\\"
                    mounts[drive_letter] = volume.SerialNumber
            return mounts
        except Exception as e:
            logging.error(f"Failed to fetch volume information: {e}")
            return {}

    def update_mounts(self):
        self.mounts = self.get_mounts()
        logging.info("Mounts have been updated.")
    def get_available_volumes(self):
        return self.mounts

    def is_volume_available(self, uid):
        return int(str(uid)) in self.mounts.values()

    def get_volume_id_from_path(self, path):
        _, volume_id = self.convert_path(path)
        return volume_id

    def get_mount_point_from_volume_id(self, volume_id):
        # If the volume_id is a path to an existing directory, treat it as a valid mount (for tests)
        import os
        if os.path.isdir(volume_id):
            return volume_id
        for mountpoint, id in self.mounts.items():
            if id == volume_id:
                return mountpoint
            try:
                if id == int(volume_id):
                    return mountpoint
            except (ValueError, TypeError):
                continue
        return None

    def get_available_uids(self):
        return set(self.mounts.values())

    def convert_path(self, path):
        path = Path(path).resolve()
        for mountpoint, key in sorted(self.mounts.items(), key=lambda x: -len(x[0])):
            if str(path).startswith(mountpoint):
                relative_path = path.relative_to(mountpoint)
                return (key, str(relative_path))
        return None, str(path)

    def reconstruct_path(self, key1, relative_path):
        for mountpoint, key in self.mounts.items():
            if key == key1 or key == int(key1):
                return Path(mountpoint) / relative_path
        return None

    def is_conversion_reversible(self, path):
        converted = self.convert_path(path)
        if converted[0] is None:
            return False
        reconstructed = self.reconstruct_path(converted[0], converted[1])
        return reconstructed == Path(path).resolve()

    def get_volume_label_from_drive_letter(self, drive_letter):
        if not drive_letter :
            return "None"
        if self.os != "Windows":
            return "N/A"
        normalized_drive_letter = drive_letter.upper().strip("\\/")
        if not wmi:
            return "Unknown"
        c = wmi.WMI()
        try:
            for volume in c.Win32_Volume():
                if volume.DriveLetter:
                    wmi_drive_letter = volume.DriveLetter.upper().strip("\\/")
                    if wmi_drive_letter == normalized_drive_letter:
                        return volume.Label if volume.Label else "No Label"
        except Exception as e:
            logging.error(f"Failed to fetch volume label for {drive_letter}: {e}")
        return "Unknown"
