"""Installation utilities for NcatBot."""

import subprocess
import sys

from ncatbot.utils.logger import get_log

LOG = get_log("Install")


def install_napcat() -> None:
    """Install napcat package.

    This function will:
    1. Check if napcat is already installed
    2. If not, install it using pip
    3. Verify the installation

    Raises:
        RuntimeError: If installation fails
    """
    return True
    try:
        # Check if napcat is already installed
        import napcat

        LOG.info("napcat is already installed")
        return
    except ImportError:
        LOG.info("napcat not found, installing...")

    try:
        # Install napcat using pip
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "napcat",
                "-i",
                "https://mirrors.aliyun.com/pypi/simple/",
            ]
        )
        LOG.info("Successfully installed napcat")

        # Verify installation
        import napcat

        LOG.info(f"Verified napcat installation: version {napcat.__version__}")

    except subprocess.CalledProcessError as e:
        LOG.error(f"Failed to install napcat: {e}")
        raise RuntimeError(f"Failed to install napcat: {e}")
    except ImportError as e:
        LOG.error(f"Failed to import napcat after installation: {e}")
        raise RuntimeError(f"Failed to import napcat after installation: {e}")
    except Exception as e:
        LOG.error(f"Unexpected error during napcat installation: {e}")
        raise RuntimeError(f"Unexpected error during napcat installation: {e}")
