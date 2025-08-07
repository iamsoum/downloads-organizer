import pytest
import tempfile
from pathlib import Path
from organizer.config import ConfigManager

def test_config_creation():
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_path = Path(tmp_dir) / "test_config.yaml"
        config_manager = ConfigManager(str(config_path))
        
        assert config_path.exists()
        rules = config_manager.get_file_rules()
        assert 'Documents' in rules
        assert 'pdf' in rules['Documents']

def test_config_loading():
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_path = Path(tmp_dir) / "test_config.yaml"
        
        # Create config and modify it
        config_manager = ConfigManager(str(config_path))
        config_manager.update_config({
            'rules': {'TestCategory': ['test']},
            'settings': {'test_setting': True}
        })
        
        # Load it again
        new_config_manager = ConfigManager(str(config_path))
        rules = new_config_manager.get_file_rules()
        settings = new_config_manager.get_settings()
        
        assert 'TestCategory' in rules
        assert settings['test_setting'] is True