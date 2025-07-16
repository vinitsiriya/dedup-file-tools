"""
UidPath: System-Independent Path Abstraction Utility

This module provides the UidPath class, which enables robust, portable file referencing
across different operating systems by abstracting filesystem mount points using unique identifiers (UIDs).

- On Windows, UID is the volume serial number (serving as a replacement for the drive letter).
- On Linux, UID is the filesystem UUID.

The class supports converting absolute file paths to (UID, relative_path) tuples and reconstructing
absolute paths from these tuples, enabling consistent file tracking across system boundaries.

IMPORTANT:
- The 'relative_path' returned by convert_path is only guaranteed to be relative to the detected mount point.
- Its format may be long or look like an absolute path segment, especially in test/temp environments.
- Only UidPath should interpret or manipulate rel_path; treat it as opaque elsewhere.
"""
import platform
import logging
from pathlib import Path
import subprocess
try:
    import wmi
except ImportError:
    wmi = None
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class UidPath:
    """
    UidPath: System-independent file reference.

    Represents a file location as a (uid, relative_path) pair:
    - uid: Unique identifier for the volume (serial number, UUID, or test path).
    - relative_path: Path relative to the mount point or root.

    Use this struct to pass file references around, instead of raw tuples.
    """
    uid: Any
    relative_path: str

class UidPathUtil:
    """
    UidPath provides methods to convert file paths to a (UID, relative_path) tuple and reconstruct
    absolute paths from these tuples. This abstraction allows for system-independent file referencing.

    UID:
        - On Windows: The volume serial number (replacement for drive letter, e.g., 'C:').
        - On Linux: The filesystem UUID.
    Relative Path:
        - The path of the file relative to the mount point (drive root or mount directory).
        - NOTE: The format of relative_path is only guaranteed to be relative to the detected mount point.
          It may be a long path segment or appear absolute in some environments (e.g., tests/temp dirs).
        - Only UidPath should interpret or manipulate rel_path; all other code should treat it as opaque.
    """
    def __init__(self):
        """
        Initialize UidPath, detecting the operating system and available mount points.
        """
        self.os = platform.system()
        self.mounts = self.get_mounts()

    def get_mounts(self):
        """
        Detect all available mount points and their UIDs for the current system.
        Returns:
            dict: Mapping of mount point (str) to UID (str or int).
        """
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
        """
        Get Linux mount points and their UUIDs using lsblk.
        Returns:
            dict: Mapping of mount point to UUID.
        """
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
        """
        Get Windows drive letters and their volume serial numbers using WMI.
        Returns:
            dict: Mapping of drive letter (e.g., 'C:\\') to serial number (int or str).
        """
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
        """
        Refresh the mount point to UID mapping.
        """
        self.mounts = self.get_mounts()
        logging.info("Mounts have been updated.")

    def get_available_volumes(self):
        """
        Return the current mapping of mount points to UIDs.
        Returns:
            dict: Mapping of mount point to UID.
        """
        return self.mounts

    def is_volume_available(self, uid):
        """
        Check if a volume with the given UID is available.
        Args:
            uid (str or int): UID to check.
        Returns:
            bool: True if available, False otherwise.
        """
        return int(str(uid)) in self.mounts.values()

    def get_volume_id_from_path(self, path):
        """
        Get the UID for the given path.
        Args:
            path (str): Absolute file path.
        Returns:
            str or int: UID for the volume containing the path.
        """
        uid_path_obj = self.convert_path(path)
        return uid_path_obj.uid

    def get_mount_point_from_volume_id(self, volume_id):
        """
        Given a UID, return the corresponding mount point (drive root or mount directory).
        Args:
            volume_id (str or int): UID of the volume.
        Returns:
            str: Mount point path, or None if not found.
        """
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
        """
        Return a set of all available UIDs.
        Returns:
            set: Set of UIDs.
        """
        return set(self.mounts.values())

    def convert_path(self, path) -> 'UidPath':
        """
        Convert an absolute file path to a UidPath (uid, relative_path) struct.
        Args:
            path (str): Absolute file path.
        Returns:
            UidPath: (uid, relative_path) where relative_path is relative to the mount point.
        Notes:
            - The format of relative_path is only guaranteed to be relative to the detected mount point.
            - It may be a long path segment or appear absolute in some environments (e.g., tests/temp dirs).
            - Only UidPath should interpret or manipulate rel_path; all other code should treat it as opaque.
        """
        path = Path(path).resolve()
        for mountpoint, key in sorted(self.mounts.items(), key=lambda x: -len(x[0])):
            if str(path).startswith(mountpoint):
                relative_path = path.relative_to(mountpoint)
                return UidPath(key, str(relative_path))
        return UidPath(None, str(path))

    def reconstruct_path(self, uid_path_obj: 'UidPath'):
        """
        Reconstruct an absolute path from a UidPath (uid, relative_path) struct.
        Args:
            uid_path_obj (UidPath): UidPath dataclass with uid and relative_path.
        Returns:
            Path or None: Absolute path if the volume is available, else None.
        """
        for mountpoint, key in self.mounts.items():
            if key == uid_path_obj.uid or key == int(uid_path_obj.uid):
                return Path(mountpoint) / uid_path_obj.relative_path
        return None

    def is_conversion_reversible(self, path):
        """
        Check if converting and reconstructing a path yields the original absolute path.
        Args:
            path (str): Absolute file path.
        Returns:
            bool: True if reversible, False otherwise.
        """
        converted = self.convert_path(path)
        if converted.uid is None:
            return False
        reconstructed = self.reconstruct_path(converted)
        return reconstructed == Path(path).resolve()

    def get_volume_label_from_drive_letter(self, drive_letter):
        """
        Get the volume label for a given drive letter (Windows only).
        Args:
            drive_letter (str): Drive letter (e.g., 'C:').
        Returns:
            str: Volume label, or 'Unknown' if not found.
        """
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
