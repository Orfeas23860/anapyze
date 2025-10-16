"""
Anapyze Configuration Management System

This module provides flexible configuration for neuroimaging tools and data paths.
Supports environment variables, config files, and programmatic overrides.
"""

import os
import platform
import sys
from pathlib import Path
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass, field
import warnings


@dataclass
class AnapyzeConfig:
    """
    Central configuration class for anapyze package.
    
    Provides flexible configuration for:
    - Container runtime (Docker/Podman with CAT12 container)
    - Data directories and templates
    - Processing parameters
    - Platform-specific settings
    
    Configuration priority (highest to lowest):
    1. Programmatic overrides (direct assignment)
    2. Environment variables
    3. Config file settings
    4. Default values
    """
    
    # === Container Runtime Configuration ===
    use_container: bool = field(default_factory=lambda: _get_env_bool('ANAPYZE_USE_CONTAINER', True))
    container_runtime: str = field(default_factory=lambda: _get_env_or_default('ANAPYZE_CONTAINER_RUNTIME', 'podman'))
    cat12_docker_image: str = field(default_factory=lambda: _get_env_or_default('CAT12_DOCKER_IMAGE', 'jhuguetn/cat12:latest'))
    
    # === Legacy MATLAB Support (for backward compatibility) ===
    matlab_cmd: str = field(default_factory=lambda: _get_default_matlab_path())
    spm_path: Optional[str] = field(default_factory=lambda: _get_env_or_none('SPM_PATH'))
    cat12_path: Optional[str] = field(default_factory=lambda: _get_env_or_none('CAT12_PATH'))
    freesurfer_home: Optional[str] = field(default_factory=lambda: _get_env_or_none('FREESURFER_HOME'))
    
    # === Data Directories ===
    data_dir: Path = field(default_factory=lambda: Path.cwd() / 'data')
    output_dir: Path = field(default_factory=lambda: Path.cwd() / 'outputs')
    temp_dir: Path = field(default_factory=lambda: Path.cwd() / 'temp')
    
    # === Package Resources ===
    resources_dir: Path = field(default_factory=lambda: _get_package_resources_dir())
    atlas_dir: Path = field(default_factory=lambda: _get_package_resources_dir() / 'atlas')
    templates_dir: Path = field(default_factory=lambda: _get_package_resources_dir() / 'templates')
    masks_dir: Path = field(default_factory=lambda: _get_package_resources_dir() / 'mask')
    
    # === Processing Parameters ===
    n_cores: int = field(default_factory=lambda: int(os.getenv('ANAPYZE_N_CORES', os.cpu_count() or 1)))
    memory_limit_gb: float = field(default_factory=lambda: float(os.getenv('ANAPYZE_MEMORY_LIMIT', 8.0)))
    
    # === Logging ===
    log_level: str = field(default_factory=lambda: os.getenv('ANAPYZE_LOG_LEVEL', 'INFO'))
    log_file: Optional[Path] = field(default_factory=lambda: _get_log_file_path())
    
    # === Validation ===
    validate_inputs: bool = field(default_factory=lambda: os.getenv('ANAPYZE_VALIDATE_INPUTS', 'True').lower() == 'true')
    strict_mode: bool = field(default_factory=lambda: os.getenv('ANAPYZE_STRICT_MODE', 'False').lower() == 'true')
    
    def __post_init__(self):
        """Validate and normalize configuration after initialization."""
        self._normalize_paths()
        self._validate_configuration()
    
    def _normalize_paths(self):
        """Convert string paths to Path objects and expand user/env variables."""
        # Convert string paths to Path objects
        path_fields = ['data_dir', 'output_dir', 'temp_dir', 'resources_dir', 
                      'atlas_dir', 'templates_dir', 'masks_dir']
        
        for field_name in path_fields:
            value = getattr(self, field_name)
            if isinstance(value, str):
                value = Path(value)
            
            # Expand user directory and environment variables
            if value:
                value = Path(os.path.expanduser(os.path.expandvars(str(value))))
                setattr(self, field_name, value.resolve())
        
        # Handle optional log file
        if self.log_file and isinstance(self.log_file, str):
            self.log_file = Path(os.path.expanduser(os.path.expandvars(self.log_file))).resolve()
    
    def _validate_configuration(self):
        """Validate configuration settings and warn about issues."""
        if self.strict_mode:
            self._strict_validation()
        else:
            self._lenient_validation()
    
    def _strict_validation(self):
        """Strict validation - raises errors for missing tools."""
        if self.use_container:
            # Validate container runtime
            if not self._check_container_runtime():
                raise RuntimeError(f"Container runtime '{self.container_runtime}' not available")
            
            # Validate container image availability
            if not self._check_container_image():
                warnings.warn(f"CAT12 container image '{self.cat12_docker_image}' may not be available. "
                            "Run 'podman pull {self.cat12_docker_image}' to download.", UserWarning)
        else:
            # Legacy MATLAB validation
            if not self.matlab_cmd or not Path(self.matlab_cmd).exists():
                raise FileNotFoundError(f"MATLAB not found at: {self.matlab_cmd}")
            
            if self.spm_path and not Path(self.spm_path).exists():
                raise FileNotFoundError(f"SPM not found at: {self.spm_path}")
    
    def _lenient_validation(self):
        """Lenient validation - only warns about missing tools."""
        if self.use_container:
            if not self._check_container_runtime():
                warnings.warn(f"Container runtime '{self.container_runtime}' not available. "
                            "Container-based functions will not work.", UserWarning)
        else:
            # Legacy MATLAB validation
            if not self.matlab_cmd or not Path(self.matlab_cmd).exists():
                warnings.warn(f"MATLAB not found at: {self.matlab_cmd}. "
                            "MATLAB-dependent functions will not work.", UserWarning)
            
            if self.spm_path and not Path(self.spm_path).exists():
                warnings.warn(f"SPM not found at: {self.spm_path}. "
                            "SPM-dependent functions may not work.", UserWarning)
    
    def create_directories(self):
        """Create necessary directories if they don't exist."""
        dirs_to_create = [self.data_dir, self.output_dir, self.temp_dir]
        
        for directory in dirs_to_create:
            if directory:
                directory.mkdir(parents=True, exist_ok=True)
    
    def get_atlas_path(self, atlas_name: str) -> Path:
        """Get path to specific atlas file."""
        atlas_path = self.atlas_dir / atlas_name
        if not atlas_path.exists():
            raise FileNotFoundError(f"Atlas not found: {atlas_path}")
        return atlas_path
    
    def get_template_path(self, template_name: str) -> Path:
        """Get path to specific template file."""
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        return template_path
    
    def get_mask_path(self, mask_name: str) -> Path:
        """Get path to specific mask file."""
        mask_path = self.masks_dir / mask_name
        if not mask_path.exists():
            raise FileNotFoundError(f"Mask not found: {mask_path}")
        return mask_path
    
    def _check_container_runtime(self) -> bool:
        """Check if the specified container runtime is available."""
        import subprocess
        try:
            result = subprocess.run([self.container_runtime, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def _check_container_image(self) -> bool:
        """Check if the CAT12 container image is available locally."""
        import subprocess
        try:
            result = subprocess.run([self.container_runtime, 'images', '-q', self.cat12_docker_image], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0 and result.stdout.strip() != ''
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    def get_container_command(self, mfile_path: str, input_files: list = None) -> list:
        """
        Generate container command for running CAT12/SPM scripts.
        
        Based on https://github.com/jhuguetn/cat12-docker documentation.
        
        Parameters
        ----------
        mfile_path : str
            Path to the MATLAB batch script (.m file)
        input_files : list, optional
            List of input files to process
            
        Returns
        -------
        list
            Command list ready for subprocess.run()
        """
        if not self.use_container:
            raise RuntimeError("Container mode not enabled")
        
        # Base command
        cmd = [
            self.container_runtime, 'run', '--rm',
            '-v', f"{Path.cwd()}:/data"
        ]
        
        # Add input files if provided
        if input_files:
            for file_path in input_files:
                file_dir = Path(file_path).parent
                if file_dir != Path.cwd():
                    cmd.extend(['-v', f"{file_dir}:/data/{file_dir.name}"])
        
        # Add the CAT12 image and batch script
        cmd.extend([
            self.cat12_docker_image,
            '-b', f"/data/{Path(mfile_path).name}"
        ])
        
        # Add input files to command
        if input_files:
            for file_path in input_files:
                cmd.append(f"/data/{Path(file_path).name}")
        
        return cmd
    
    @classmethod
    def from_env(cls) -> 'AnapyzeConfig':
        """Create configuration primarily from environment variables."""
        return cls()  # Default factory functions already read from env
    
    @classmethod
    def for_student(cls, data_dir: Union[str, Path] = None) -> 'AnapyzeConfig':
        """
        Create student-friendly configuration with sensible defaults.
        
        Parameters
        ----------
        data_dir : str or Path, optional
            Directory where student will store their data.
            Defaults to './student_data'
        """
        if data_dir is None:
            data_dir = Path.cwd() / 'student_data'
        
        config = cls()
        config.data_dir = Path(data_dir)
        config.output_dir = config.data_dir / 'results'
        config.temp_dir = config.data_dir / 'temp'
        config.strict_mode = False  # Be lenient for students
        config.validate_inputs = True  # But validate inputs
        
        return config
    
    def __repr__(self):
        """Provide informative string representation."""
        return (
            f"AnapyzeConfig(\n"
            f"  use_container={self.use_container}\n"
            f"  container_runtime='{self.container_runtime}'\n"
            f"  cat12_image='{self.cat12_docker_image}'\n"
            f"  matlab_cmd='{self.matlab_cmd}'\n"
            f"  data_dir='{self.data_dir}'\n"
            f"  resources_dir='{self.resources_dir}'\n"
            f"  n_cores={self.n_cores}\n"
            f"  log_level='{self.log_level}'\n"
            f")"
        )


# === Helper Functions ===

def _get_default_matlab_path() -> str:
    """Auto-detect MATLAB installation path based on platform."""
    matlab_cmd = os.getenv('MATLAB_CMD')
    if matlab_cmd:
        return matlab_cmd
    
    system = platform.system().lower()
    
    if system == 'darwin':  # macOS
        common_paths = [
            '/Applications/MATLAB_R2024b.app/bin/matlab',
            '/Applications/MATLAB_R2024a.app/bin/matlab',
            '/Applications/MATLAB_R2023b.app/bin/matlab',
            '/usr/local/bin/matlab'
        ]
    elif system == 'linux':
        common_paths = [
            '/usr/local/MATLAB/R2024b/bin/matlab',
            '/usr/local/MATLAB/R2024a/bin/matlab', 
            '/usr/local/MATLAB/R2023b/bin/matlab',
            '/opt/MATLAB/R2024b/bin/matlab',
            '/usr/bin/matlab'
        ]
    elif system == 'windows':
        # Windows paths would go here
        common_paths = [
            'C:\\Program Files\\MATLAB\\R2024b\\bin\\matlab.exe',
            'C:\\Program Files\\MATLAB\\R2024a\\bin\\matlab.exe'
        ]
    else:
        common_paths = ['matlab']  # Hope it's in PATH
    
    # Check which path exists
    for path in common_paths:
        if Path(path).exists():
            return path
    
    # Fall back to hoping matlab is in PATH
    return 'matlab'


def _get_env_or_none(env_var: str) -> Optional[str]:
    """Get environment variable or return None."""
    value = os.getenv(env_var)
    return value if value else None


def _get_env_or_default(env_var: str, default: str) -> str:
    """Get environment variable or return default value."""
    return os.getenv(env_var, default)


def _get_env_bool(env_var: str, default: bool) -> bool:
    """Get environment variable as boolean or return default value."""
    value = os.getenv(env_var)
    if value is None:
        return default
    return value.lower() in ('true', '1', 'yes', 'on')


def _get_package_resources_dir() -> Path:
    """Get the path to the package resources directory."""
    # Try to find the resources directory relative to this file
    config_file = Path(__file__)
    
    # Go up from src/anapyze/config.py to find resources/
    possible_resources = [
        config_file.parent.parent.parent / 'resources',  # From src/anapyze/
        config_file.parent.parent.parent.parent / 'resources',  # From installed package
    ]
    
    for resources_path in possible_resources:
        if resources_path.exists():
            return resources_path.resolve()
    
    # Fall back to current directory + resources
    return Path.cwd() / 'resources'


def _get_log_file_path() -> Optional[Path]:
    """Get default log file path if requested."""
    log_file = os.getenv('ANAPYZE_LOG_FILE')
    if log_file:
        return Path(log_file)
    return None


# === Global Configuration Instance ===

# Global configuration instance - can be modified by users
config = AnapyzeConfig()


def get_config() -> AnapyzeConfig:
    """Get the global configuration instance."""
    return config


def set_config(new_config: AnapyzeConfig):
    """Set a new global configuration instance."""
    global config
    config = new_config


def reset_config():
    """Reset configuration to defaults."""
    global config
    config = AnapyzeConfig()
