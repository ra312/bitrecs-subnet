import subprocess
import template.utils.constants as CONST
from shlex import split
from dataclasses import dataclass
from importlib.metadata import version

    
@dataclass
class LocalMetadata:
    """Metadata associated with the local validator instance"""

    commit: str
    btversion: str
    uid: int = 0
    coldkey: str = ""
    hotkey: str = ""


    @staticmethod
    def local_metadata() -> "LocalMetadata":
        """Extract the version as current git commit hash"""
        commit_hash = ""
        try:
            result = subprocess.run(
                split("git rev-parse HEAD"),
                check=True,
                capture_output=True,
                cwd=CONST.ROOT_DIR,
            )
            commit = result.stdout.decode().strip()
            assert len(commit) == 40, f"Invalid commit hash: {commit}"
            commit_hash = commit[:8]
        except Exception as e:
            commit_hash = "unknown"

        bittensor_version = version("bittensor")
        return LocalMetadata(
            commit=commit_hash,
            btversion=bittensor_version,
        )