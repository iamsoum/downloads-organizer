import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .categorizer import FileCategorizer
from .mover import FileMover

class FileOrganizerHandler(FileSystemEventHandler):
    def __init__(self, categorizer: FileCategorizer, mover: FileMover, 
                 handle_duplicates: bool = True):
        self.categorizer = categorizer
        self.mover = mover
        self.handle_duplicates = handle_duplicates
        self.processed_files = set()
    
    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory:
            self.process_file(Path(event.src_path))
    
    def on_moved(self, event):
        """Handle file move events"""
        if not event.is_directory:
            self.process_file(Path(event.dest_path))
    
    def process_file(self, file_path: Path):
        """Process a single file"""
        # Avoid processing the same file multiple times
        if str(file_path) in self.processed_files:
            return
        
        # Wait a bit to ensure file is fully written
        time.sleep(0.5)
        
        try:
            if not file_path.exists() or not file_path.is_file():
                return
            
            # Categorize the file
            category = self.categorizer.categorize_file(file_path)
            
            # Check for duplicates if enabled
            if self.handle_duplicates:
                target_dir = self.mover.get_target_directory(category, file_path)
                
                # Look for existing files with same hash
                for existing_file in target_dir.rglob('*'):
                    if (existing_file.is_file() and 
                        existing_file.name != file_path.name and
                        self.categorizer.is_duplicate(file_path, existing_file)):
                        
                        # Handle duplicate
                        success, final_path = self.mover.handle_duplicate(
                            file_path, existing_file, "rename"
                        )
                        if success:
                            self.processed_files.add(str(file_path))
                        return
            
            # Move the file
            success, final_path = self.mover.move_file(file_path, category)
            if success:
                self.processed_files.add(str(file_path))
                
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

class FileWatcher:
    def __init__(self, source_dir: Path, categorizer: FileCategorizer, 
                 mover: FileMover, handle_duplicates: bool = True):
        self.source_dir = Path(source_dir)
        self.observer = Observer()
        self.event_handler = FileOrganizerHandler(
            categorizer, mover, handle_duplicates
        )
    
    def start_watching(self):
        """Start watching the source directory"""
        self.observer.schedule(
            self.event_handler, 
            str(self.source_dir), 
            recursive=False
        )
        self.observer.start()
        print(f"Started watching: {self.source_dir}")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_watching()
    
    def stop_watching(self):
        """Stop watching the directory"""
        self.observer.stop()
        self.observer.join()
        print("Stopped watching directory")
    
    def organize_existing_files(self):
        """Organize files that already exist in the source directory"""
        print(f"Organizing existing files in {self.source_dir}")
        
        for file_path in self.source_dir.iterdir():
            if file_path.is_file():
                self.event_handler.process_file(file_path)
        
        print("Finished organizing existing files")