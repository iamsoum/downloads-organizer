import click
from pathlib import Path
from .config import ConfigManager
from .categorizer import FileCategorizer
from .mover import FileMover
from .watcher import FileWatcher

@click.group()
def cli():
    """Downloads Organizer - Automated file organization tool"""
    pass

@cli.command()
@click.option('--source', '-s', help='Source directory to organize')
@click.option('--target', '-t', help='Target directory for organized files')
@click.option('--watch', '-w', is_flag=True, help='Enable watch mode')
@click.option('--existing', '-e', is_flag=True, help='Organize existing files')
def organize(source, target, watch, existing):
    """Organize files in the specified directory"""
    
    # Load configuration
    config_manager = ConfigManager()
    settings = config_manager.get_settings()
    rules = config_manager.get_file_rules()
    
    # Use command line args or fall back to config
    source_dir = Path(source) if source else Path(settings['source_dir'])
    target_dir = Path(target) if target else Path(settings['target_dir'])
    
    if not source_dir.exists():
        click.echo(f"Error: Source directory {source_dir} does not exist")
        return
    
    # Initialize components
    categorizer = FileCategorizer(rules)
    mover = FileMover(target_dir, settings.get('create_date_folders', False))
    
    if existing:
        # Organize existing files
        watcher = FileWatcher(source_dir, categorizer, mover, 
                            settings.get('handle_duplicates', True))
        watcher.organize_existing_files()
    
    if watch or settings.get('watch_mode', True):
        # Start watching for new files
        watcher = FileWatcher(source_dir, categorizer, mover,
                            settings.get('handle_duplicates', True))
        click.echo("Starting file watcher... Press Ctrl+C to stop")
        watcher.start_watching()
    
    if not watch and not existing:
        click.echo("Use --watch to monitor directory or --existing to organize current files")

@cli.command()
@click.argument('directory')
def find_duplicates(directory):
    """Find duplicate files in the specified directory"""
    dir_path = Path(directory)
    
    if not dir_path.exists():
        click.echo(f"Error: Directory {dir_path} does not exist")
        return
    
    config_manager = ConfigManager()
    rules = config_manager.get_file_rules()
    categorizer = FileCategorizer(rules)
    
    click.echo(f"Searching for duplicates in {dir_path}...")
    duplicates = categorizer.find_duplicates_in_directory(dir_path)
    
    if not duplicates:
        click.echo("No duplicates found!")
        return
    
    click.echo(f"\nFound {len(duplicates)} groups of duplicate files:")
    for i, duplicate_group in enumerate(duplicates, 1):
        click.echo(f"\nGroup {i}:")
        for file_path in duplicate_group:
            size = file_path.stat().st_size
            click.echo(f"  - {file_path} ({size} bytes)")

@cli.command()
def config():
    """Show current configuration"""
    config_manager = ConfigManager()
    
    click.echo("Current Configuration:")
    click.echo("\nFile Rules:")
    for category, extensions in config_manager.get_file_rules().items():
        click.echo(f"  {category}: {extensions}")
    
    click.echo("\nSettings:")
    for key, value in config_manager.get_settings().items():
        click.echo(f"  {key}: {value}")

if __name__ == '__main__':
    cli()