"""
Shared utility functions for path management across different design pages.
This module eliminates code duplication and provides consistent path handling.
"""
import sys
import os
from pathlib import Path
from typing import Optional, Tuple


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def setup_design_path(design_name: str, subdirectory: Optional[str] = None) -> Tuple[Path, Path]:
    """
    Set up the path for a design module and return both the design path and project root.
    
    Args:
        design_name: Name of the design directory (e.g., 'map_explorer', 'trend_comparison', 'affordability_finder')
        subdirectory: Optional subdirectory within the design directory
    
    Returns:
        Tuple of (design_path, project_root)
    """
    project_root = get_project_root()
    
    if subdirectory:
        design_path = project_root / design_name / subdirectory
    else:
        design_path = project_root / design_name
    
    return design_path, project_root


def add_to_path(path: Path, remove_others: Optional[list] = None) -> None:
    """
    Add a path to sys.path and optionally remove conflicting paths.
    
    Args:
        path: Path to add to sys.path
        remove_others: Optional list of paths to remove from sys.path
    """
    path_str = str(path)
    
    # Remove conflicting paths if specified
    if remove_others:
        for other_path in remove_others:
            other_path_str = str(other_path)
            if other_path_str in sys.path:
                sys.path.remove(other_path_str)
    
    # Add the new path at the beginning
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
    elif sys.path[0] != path_str:
        # Move to front if already in path
        sys.path.remove(path_str)
        sys.path.insert(0, path_str)


def import_from_path(module_name: str, file_path: Path):
    """
    Import a module from a specific file path.
    
    Args:
        module_name: Name to assign to the module
        file_path: Path to the Python file to import
    
    Returns:
        The imported module
    """
    import importlib.util
    
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {module_name} from {file_path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def clear_module_cache(module_names: list) -> None:
    """
    Clear specified modules from sys.modules cache.
    
    Args:
        module_names: List of module names to clear
    """
    for module_name in module_names:
        if module_name in sys.modules:
            del sys.modules[module_name]
        # Also remove submodules
        for key in list(sys.modules.keys()):
            if key.startswith(f"{module_name}."):
                del sys.modules[key]

