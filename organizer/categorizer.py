import hashlib
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class FileCategorizer:
    def __init__(self, rules: Dict[str, List[str]]):
        self.rules = rules
        self._build_extension_map()
    
    def _build_extension_map(self) -> None:
        """Build reverse mapping from extension to category"""
        self.extension_to_category = {}
        for category, extensions in self.rules.items():
            for ext in extensions:
                self.extension_to_category[ext.lower()] = category
    
    def categorize_file(self, file_path: Path) -> str:
        """Determine the category of a file based on its extension"""
        extension = file_path.suffix.lower().lstrip('.')
        return self.extension_to_category.get(extension, 'Others')
    
    def get_file_hash(self, file_path: Path, chunk_size: int = 8192) -> str:
        """Calculate MD5 hash of file for duplicate detection"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (IOError, OSError) as e:
            print(f"Error reading file {file_path}: {e}")
            return ""
    
    def get_file_metadata(self, file_path: Path) -> Dict:
        """Get file metadata for comparison"""
        try:
            stat = file_path.stat()
            return {
                'size': stat.st_size,
                'modified_time': stat.st_mtime,
                'created_time': stat.st_ctime,
                'name': file_path.name,
                'extension': file_path.suffix.lower()
            }
        except (IOError, OSError) as e:
            print(f"Error getting metadata for {file_path}: {e}")
            return {}
    
    def is_duplicate(self, file1_path: Path, file2_path: Path) -> bool:
        """Check if two files are duplicates using hash and metadata"""
        # Quick check: compare file sizes first
        try:
            if file1_path.stat().st_size != file2_path.stat().st_size:
                return False
        except (IOError, OSError):
            return False
        
        # If sizes match, compare hashes
        hash1 = self.get_file_hash(file1_path)
        hash2 = self.get_file_hash(file2_path)
        
        return hash1 == hash2 and hash1 != ""
    
    def find_duplicates_in_directory(self, directory: Path) -> List[List[Path]]:
        """Find all duplicate files in a directory"""
        file_hashes = {}
        duplicates = []
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                file_hash = self.get_file_hash(file_path)
                if file_hash:
                    if file_hash in file_hashes:
                        file_hashes[file_hash].append(file_path)
                    else:
                        file_hashes[file_hash] = [file_path]
        
        # Return groups of duplicate files
        for file_list in file_hashes.values():
            if len(file_list) > 1:
                duplicates.append(file_list)
        
        return duplicates