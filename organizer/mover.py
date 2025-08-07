import shutil
import os
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime

class FileMover:
    def __init__(self, target_base_dir: Path, create_date_folders: bool = False):
        self.target_base_dir = Path(target_base_dir)
        self.create_date_folders = create_date_folders
        self.target_base_dir.mkdir(parents=True, exist_ok=True)
    
    def get_target_directory(self, category: str, file_path: Path) -> Path:
        """Determine target directory for a file"""
        target_dir = self.target_base_dir / category
        
        if self.create_date_folders:
            # Create date-based subdirectories
            try:
                modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                date_folder = modified_time.strftime("%Y/%m")
                target_dir = target_dir / date_folder
            except (OSError, ValueError):
                # Fall back to current date if file stat fails
                date_folder = datetime.now().strftime("%Y/%m")
                target_dir = target_dir / date_folder
        
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir
    
    def get_unique_filename(self, target_dir: Path, filename: str) -> str:
        """Generate unique filename if file already exists"""
        target_path = target_dir / filename
        
        if not target_path.exists():
            return filename
        
        # Extract name and extension
        stem = target_path.stem
        suffix = target_path.suffix
        counter = 1
        
        while True:
            new_filename = f"{stem}_{counter:03d}{suffix}"
            new_target_path = target_dir / new_filename
            if not new_target_path.exists():
                return new_filename
            counter += 1
    
    def move_file(self, source_path: Path, category: str) -> Tuple[bool, Optional[Path]]:
        """Move file to appropriate category directory"""
        try:
            target_dir = self.get_target_directory(category, source_path)
            unique_filename = self.get_unique_filename(target_dir, source_path.name)
            target_path = target_dir / unique_filename
            
            # Move the file
            shutil.move(str(source_path), str(target_path))
            print(f"Moved: {source_path} -> {target_path}")
            return True, target_path
            
        except (IOError, OSError, shutil.Error) as e:
            print(f"Error moving file {source_path}: {e}")
            return False, None
    
    def handle_duplicate(self, source_path: Path, existing_path: Path, 
                        strategy: str = "rename") -> Tuple[bool, Optional[Path]]:
        """Handle duplicate files based on strategy"""
        if strategy == "skip":
            print(f"Skipping duplicate: {source_path}")
            return True, existing_path
        
        elif strategy == "rename":
            # Rename and move the file
            target_dir = existing_path.parent
            unique_filename = self.get_unique_filename(target_dir, source_path.name)
            target_path = target_dir / unique_filename
            
            try:
                shutil.move(str(source_path), str(target_path))
                print(f"Renamed and moved duplicate: {source_path} -> {target_path}")
                return True, target_path
            except (IOError, OSError, shutil.Error) as e:
                print(f"Error handling duplicate {source_path}: {e}")
                return False, None
        
        elif strategy == "replace":
            # Replace existing file
            try:
                existing_path.unlink()  # Delete existing file
                shutil.move(str(source_path), str(existing_path))
                print(f"Replaced: {existing_path} with {source_path}")
                return True, existing_path
            except (IOError, OSError, shutil.Error) as e:
                print(f"Error replacing file {existing_path}: {e}")
                return False, None
        
        return False, None