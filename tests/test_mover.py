import pytest
import tempfile
from pathlib import Path
from organizer.mover import FileMover

def test_file_moving():
    with tempfile.TemporaryDirectory() as tmp_dir:
        source_dir = Path(tmp_dir) / "source"
        target_dir = Path(tmp_dir) / "target"
        
        source_dir.mkdir()
        
        # Create test file
        test_file = source_dir / "test.txt"
        test_file.write_text("Test content")
        
        mover = FileMover(target_dir)
        success, final_path = mover.move_file(test_file, "Documents")
        
        assert success
        assert final_path.exists()
        assert final_path.read_text() == "Test content"
        assert not test_file.exists()

def test_unique_filename_generation():
    with tempfile.TemporaryDirectory() as tmp_dir:
        target_dir = Path(tmp_dir)
        
        # Create existing file
        existing_file = target_dir / "test.txt"
        existing_file.write_text("existing")
        
        mover = FileMover(target_dir)
        unique_name = mover.get_unique_filename(target_dir, "test.txt")
        
        assert unique_name == "test_001.txt"