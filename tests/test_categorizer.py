import pytest
import tempfile
from pathlib import Path
from organizer.categorizer import FileCategorizer

def test_file_categorization():
    rules = {
        'Documents': ['pdf', 'txt'],
        'Images': ['jpg', 'png'],
        'Others': []
    }
    
    categorizer = FileCategorizer(rules)
    
    assert categorizer.categorize_file(Path('test.pdf')) == 'Documents'
    assert categorizer.categorize_file(Path('test.jpg')) == 'Images'
    assert categorizer.categorize_file(Path('test.unknown')) == 'Others'

def test_file_hashing():
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create test files
        file1 = Path(tmp_dir) / "test1.txt"
        file2 = Path(tmp_dir) / "test2.txt"
        
        file1.write_text("Hello World")
        file2.write_text("Hello World")
        
        categorizer = FileCategorizer({})
        
        hash1 = categorizer.get_file_hash(file1)
        hash2 = categorizer.get_file_hash(file2)
        
        assert hash1 == hash2
        assert categorizer.is_duplicate(file1, file2)

def test_duplicate_detection():
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create identical files
        file1 = Path(tmp_dir) / "test1.txt"
        file2 = Path(tmp_dir) / "test2.txt"
        file3 = Path(tmp_dir) / "different.txt"
        
        file1.write_text("Same content")
        file2.write_text("Same content")
        file3.write_text("Different content")
        
        categorizer = FileCategorizer({})
        
        assert categorizer.is_duplicate(file1, file2)
        assert not categorizer.is_duplicate(file1, file3)
        
        duplicates = categorizer.find_duplicates_in_directory(Path(tmp_dir))
        assert len(duplicates) == 1
        assert len(duplicates[0]) == 2