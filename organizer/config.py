import yaml
import os
from pathlib import Path
from typing import Dict, List, Optional

class ConfigManager:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            self._create_default_config()
        
        with open(self.config_path, 'r') as file:
            return yaml.safe_load(file)
    
    def _create_default_config(self) -> None:
        """Create default configuration file"""
        default_config = {
            'rules': {
                'Documents': ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt'],
                'Images': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'svg'],
                'Archives': ['zip', 'tar', 'gz', 'rar', '7z', 'bz2'],
                'Videos': ['mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv'],
                'Audio': ['mp3', 'wav', 'flac', 'aac', 'ogg'],
                'Others': []
            },
            'settings': {
                'source_dir': str(Path.home() / 'Downloads'),
                'target_dir': str(Path.home() / 'Downloads' / 'Organized'),
                'watch_mode': True,
                'handle_duplicates': True,
                'create_date_folders': False
            }
        }
        
        with open(self.config_path, 'w') as file:
            yaml.dump(default_config, file, default_flow_style=False)
    
    def get_file_rules(self) -> Dict[str, List[str]]:
        """Get file categorization rules"""
        return self.config.get('rules', {})
    
    def get_settings(self) -> Dict:
        """Get application settings"""
        return self.config.get('settings', {})
    
    def update_config(self, new_config: Dict) -> None:
        """Update configuration"""
        self.config.update(new_config)
        with open(self.config_path, 'w') as file:
            yaml.dump(self.config, file, default_flow_style=False)