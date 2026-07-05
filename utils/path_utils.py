"""Shared path helpers for the housing affordability dashboard."""
import importlib.util
import sys
from pathlib import Path
from typing import Optional, Tuple


def get_project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


def get_data_dir() -> Path:
    """Return the shared data directory."""
    return get_project_root() / "data"


def get_housets_csv_path() -> Path:
    """Return the canonical ZIP-level HouseTS export."""
    return get_data_dir() / "housets_zip_level.csv"


def get_metro_aggregates_path() -> Path:
    """Return the pre-aggregated metro map dataset."""
    return get_data_dir() / "metro_map_aggregates.csv"


def get_geo_dir() -> Path:
    """Return the directory containing shapefiles and geojson."""
    return get_data_dir() / "geo"


def get_metro_boundaries_dir() -> Path:
    """Return the directory of per-metro ZIP boundary GeoJSON files."""
    return get_geo_dir() / "metro_zip_boundaries"


def get_module_path(module_name: str, subdirectory: Optional[str] = None) -> Tuple[Path, Path]:
    """Return a feature module directory and the project root."""
    project_root = get_project_root()
    if subdirectory:
        module_path = project_root / module_name / subdirectory
    else:
        module_path = project_root / module_name
    return module_path, project_root


def add_to_path(path: Path, remove_others: Optional[list] = None) -> None:
    """Add a path to sys.path and optionally remove conflicting paths."""
    path_str = str(path)

    if remove_others:
        for other_path in remove_others:
            other_path_str = str(other_path)
            if other_path_str in sys.path:
                sys.path.remove(other_path_str)

    if path_str not in sys.path:
        sys.path.insert(0, path_str)
    elif sys.path[0] != path_str:
        sys.path.remove(path_str)
        sys.path.insert(0, path_str)


def import_from_path(module_name: str, file_path: Path):
    """Import a module from a specific file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {module_name} from {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def clear_module_cache(module_names: list) -> None:
    """Clear specified modules from sys.modules cache."""
    for module_name in module_names:
        if module_name in sys.modules:
            del sys.modules[module_name]
        for key in list(sys.modules.keys()):
            if key.startswith(f"{module_name}."):
                del sys.modules[key]
