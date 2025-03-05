"""
File utilities for Real Estate AI
Provides functions for reading/writing data files and caching
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from config import logger, DATA_DIR

def ensure_dir_exists(directory_path: str) -> None:
    """
    Ensure a directory exists, creating it if needed
    
    Args:
        directory_path: Path to directory
    """
    os.makedirs(directory_path, exist_ok=True)
    logger.debug(f"Ensured directory exists: {directory_path}")

def load_json_file(file_path: str, default_value: Any = None) -> Any:
    """
    Load data from a JSON file with error handling
    
    Args:
        file_path: Path to JSON file
        default_value: Value to return if file doesn't exist or has an error
        
    Returns:
        Data from JSON file or default value
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}, returning default value")
            return default_value
            
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.debug(f"Loaded JSON file: {file_path}")
        return data
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {file_path}")
        return default_value
    except Exception as e:
        logger.error(f"Error loading file {file_path}: {str(e)}")
        return default_value

def save_json_file(file_path: str, data: Any, indent: int = 2) -> bool:
    """
    Save data to a JSON file with error handling
    
    Args:
        file_path: Path to JSON file
        data: Data to save
        indent: Indentation for JSON formatting
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        dir_path = os.path.dirname(file_path)
        ensure_dir_exists(dir_path)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent)
        logger.debug(f"Saved JSON file: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving file {file_path}: {str(e)}")
        return False

def merge_json_data(original: Dict, updates: Dict) -> Dict:
    """
    Recursively merge two dictionaries
    
    Args:
        original: Original dictionary
        updates: Dictionary with updates
        
    Returns:
        Merged dictionary
    """
    # If original is not a dict or is None, return updates
    if not isinstance(original, dict) or original is None:
        return updates
        
    # If updates is not a dict or is None, return original
    if not isinstance(updates, dict) or updates is None:
        return original
        
    # Create a copy of original to avoid modifying it
    result = original.copy()
    
    # Update with values from updates
    for key, value in updates.items():
        # If both original and updates have the key and both are dictionaries, merge recursively
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_json_data(result[key], value)
        else:
            result[key] = value
            
    return result

class SimpleCache:
    """Simple cache for data to avoid repeated file I/O"""
    
    def __init__(self, max_size: int = 20):
        """
        Initialize the cache
        
        Args:
            max_size: Maximum number of items in cache
        """
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if key in self.cache:
            self.access_count[key] += 1
            return self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # If cache is full, remove least accessed item
        if len(self.cache) >= self.max_size and key not in self.cache:
            # Sort by access count and remove the least accessed
            least_accessed = sorted(self.access_count.items(), key=lambda x: x[1])[0][0]
            del self.cache[least_accessed]
            del self.access_count[least_accessed]
            
        self.cache[key] = value
        self.access_count[key] = 0
    
    def clear(self) -> None:
        """Clear the cache"""
        self.cache = {}
        self.access_count = {}