"""Chrome Extensions manifest.json parser."""

import json
import os


class ChromeExtensions:
    """Parse and query Chrome extension manifest files from a profile folder."""

    def __init__(self, profile_path: str):
        """
        Initialize with a Chrome profile folder path.

        Args:
            profile_path: Path to the Chrome profile folder
                          (e.g. ~/<user>/AppData/Local/Google/Chrome/User Data/Default)
        """
        self.extensions_path = os.path.join(profile_path, "Extensions")
        self._manifests: dict[str, dict] = {}  # cache: extension_id -> parsed manifest
        self._manifest_paths: dict[str, str] = {}  # extension_id -> manifest file path
        self._scan()

    def _scan(self) -> None:
        """Scan the Extensions folder and cache all manifest data."""
        if not os.path.isdir(self.extensions_path):
            return

        for extension_id in os.listdir(self.extensions_path):
            ext_dir = os.path.join(self.extensions_path, extension_id)
            if not os.path.isdir(ext_dir):
                continue

            # Find the latest version subfolder (by filesystem order or version sort)
            version_dirs = [
                d for d in os.listdir(ext_dir)
                if os.path.isdir(os.path.join(ext_dir, d))
            ]
            if not version_dirs:
                continue

            # Use the last version alphabetically (highest version in most cases)
            version_dirs.sort()
            version_dir = version_dirs[-1]

            manifest_path = os.path.join(ext_dir, version_dir, "manifest.json")
            if os.path.isfile(manifest_path):
                self._manifest_paths[extension_id] = manifest_path
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        self._manifests[extension_id] = json.load(f)
                except (json.JSONDecodeError, OSError):
                    self._manifests[extension_id] = {}

    def get_manifest_paths(self) -> dict[str, str]:
        """
        Return a dictionary mapping each extension ID to the full path
        of its manifest.json file.

        Returns:
            dict with extension ID as key and manifest.json path as value.
        """
        return dict(self._manifest_paths)

    def get_name(self, extension_id: str) -> str | None:
        """
        Return the name of the extension, or None if not available.

        Args:
            extension_id: The extension's folder name / ID.
        """
        manifest = self._manifests.get(extension_id)
        if manifest:
            return manifest.get("name")
        return None

    def get_description(self, extension_id: str) -> str | None:
        """
        Return the description of the extension, or None if not available.

        Args:
            extension_id: The extension's folder name / ID.
        """
        manifest = self._manifests.get(extension_id)
        if manifest:
            return manifest.get("description")
        return None

    def get_author(self, extension_id: str) -> str | dict | None:
        """
        Return the author details of the extension, or None if not available.

        The author field may be a string (e.g. "developer" key) or a dict
        (e.g. {"email": "..."}). This method checks the "author" and
        "developer" keys in the manifest.

        Args:
            extension_id: The extension's folder name / ID.
        """
        manifest = self._manifests.get(extension_id)
        if manifest:
            return manifest.get("author") or manifest.get("developer")
        return None

    def get_homepage_url(self, extension_id: str) -> str | None:
        """
        Return the homepage_url of the extension, or None if not available.

        Args:
            extension_id: The extension's folder name / ID.
        """
        manifest = self._manifests.get(extension_id)
        if manifest:
            return manifest.get("homepage_url")
        return None

    def get_version(self, extension_id: str) -> str | None:
        """
        Return the version of the extension, or None if not available.

        Args:
            extension_id: The extension's folder name / ID.
        """
        manifest = self._manifests.get(extension_id)
        if manifest:
            return manifest.get("version")
        return None

    def get_extension_count(self):
        """
        Returns the total number of extensions found.
        """

        return len(self.get_manifest_paths().keys())