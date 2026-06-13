"""
Unified error handling utilities for the application.
Provides consistent error messages and handling patterns.
"""
import streamlit as st
from pathlib import Path
from typing import Optional, List


def show_file_not_found_error(file_path: Path, context: str = "") -> None:
    """
    Display a standardized file not found error message.
    
    Args:
        file_path: Path to the missing file
        context: Additional context about what the file is for
    """
    context_msg = f" ({context})" if context else ""
    st.error(f"❌ **File Not Found**: `{file_path.name}` not found at `{file_path}`{context_msg}")
    st.info(f"Please ensure the file exists in the correct location.")


def show_directory_not_found_error(dir_path: Path, required_files: Optional[List[str]] = None) -> None:
    """
    Display a standardized directory not found error message.
    
    Args:
        dir_path: Path to the missing directory
        required_files: Optional list of required file names
    """
    st.error(f"❌ **Directory Not Found**: The `{dir_path.name}` directory could not be found.")
    st.info("Please ensure all required files are present.")
    
    if required_files:
        st.markdown("**Required files:**")
        for file_name in required_files:
            st.markdown(f"- `{file_name}`")


def show_missing_files_error(missing_files: List[Path]) -> None:
    """
    Display a standardized missing files error message.
    
    Args:
        missing_files: List of missing file paths
    """
    file_names = [f.name for f in missing_files]
    st.error(f"❌ **Missing Required Files**: The following files are missing:\n- " + "\n- ".join(file_names))
    st.info("Please ensure all required files are present in the correct directories.")


def show_data_loading_error(error: Exception, file_path: Optional[Path] = None) -> None:
    """
    Display a standardized data loading error message.
    
    Args:
        error: The exception that occurred
        file_path: Optional path to the file that failed to load
    """
    file_info = f" from `{file_path}`" if file_path else ""
    st.error(f"❌ **Error loading data{file_info}**: {str(error)}")
    st.info("Please check that the file exists and is properly formatted.")


def show_empty_data_error(context: str = "") -> None:
    """
    Display a standardized empty data error message.
    
    Args:
        context: Additional context about what data is missing
    """
    context_msg = f" {context}" if context else ""
    st.error(f"⚠️ **No data available{context_msg}**")
    st.info("Please check that the data files exist and are properly formatted.")

