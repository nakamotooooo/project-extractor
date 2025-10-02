#!/usr/bin/env python3
"""
Project Code Extractor for Laravel Applications

This script traverses a Laravel project directory and extracts all relevant
source code files into a single text file for documentation or analysis.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

class ProjectCodeExtractor:
    def __init__(self, project_path=".", output_file="project-code.txt"):
        self.project_path = Path(project_path).resolve()
        
        # Detect project type
        self.project_type = self.detect_project_type()
        
        self.output_file = self.project_type + "-" + output_file 
        
        # File extensions to include for Laravel
        self.include_extensions = {
            '.php',                                 # PHP files (Models, Controllers, etc.)
            '.blade.php',                           # Blade templates
            '.js', '.ts', '.vue',                   # JavaScript/TypeScript/Vue files
            '.json',                                # Configuration files (composer.json, etc.)
            '.env', '.env.example',                 # Environment files
            '.yml', '.yaml',                        # YAML configuration (e.g., for GitHub Actions)
            '.md',                                  # Documentation
            '.html',                                # HTML files
            '.css', '.scss', '.sass', '.less',      # Style files
            '.sql',                                 # SQL files
            '.sh',                                  # Shell scripts
        }
        
        # Base directories to exclude
        self.base_exclude_dirs = {
            'node_modules', '.git', '.vscode', '.idea',
            'coverage', 'logs', 'tmp', 'temp', 'vendor',
            '.github',
        }
        
        # Configure based on project type
        self.configure_for_project_type()

    def detect_project_type(self):
        """Detect if this is a Laravel project."""
        print(f"🔍 Analyzing project at: {self.project_path}")
        
        artisan_path = self.project_path / 'artisan'
        composer_json_path = self.project_path / 'composer.json'

        if artisan_path.exists() and composer_json_path.exists():
            try:
                with open(composer_json_path, 'r', encoding='utf-8') as f:
                    composer_data = json.load(f)
                
                dependencies = composer_data.get('require', {})
                if 'laravel/framework' in dependencies:
                    print("✅ Detected: Laravel project")
                    return "laravel"
            except Exception as e:
                print(f"⚠️  Could not read composer.json: {e}")

        print("ℹ️  Generic project detected (or not a Laravel project)")
        return "generic"

    def configure_for_project_type(self):
        """Configure extraction rules based on project type."""
        if self.project_type == "laravel":
            self.exclude_dirs = self.base_exclude_dirs | {
                'storage', 'public/build', 'public/hot', 'bootstrap/cache'
            }
            self.exclude_files = {
                'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', '.gitignore',
                'composer.lock', '.env.testing'
            }
        else:  # generic
            self.exclude_dirs = self.base_exclude_dirs | {'dist', 'build'}
            self.exclude_files = {
                'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
                '.gitignore'
            }

    def should_include_file(self, file_path):
        """Check if file should be included."""
        file_path = Path(file_path)
        
        # Custom exclusion for specific test files if needed, but keeping Feature/Unit tests
        # if '.test.php' in file_path.name or '.spec.php' in file_path.name:
        #     return False
        
        # Check extension
        # Handle double extensions like .blade.php
        file_suffix = ''.join(file_path.suffixes).lower()
        if file_suffix not in self.include_extensions and file_path.suffix.lower() not in self.include_extensions:
             return False
            
        # Check if excluded
        if file_path.name in self.exclude_files:
            return False
            
        return True

    def should_include_directory(self, dir_path):
        """Check if directory should be traversed."""
        dir_path_str = str(dir_path.relative_to(self.project_path)).replace('\\', '/')
        dir_name = Path(dir_path).name

        # Exclude specific subdirectories like storage/framework, storage/logs
        if dir_path_str.startswith('storage/framework') or \
           dir_path_str.startswith('storage/logs') or \
           dir_path_str.startswith('storage/app'):
            return False

        return dir_name not in self.exclude_dirs

    def read_file_content(self, file_path):
        """Read file content with encoding fallback."""
        encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception as e:
                return f"[Error reading file: {e}]"
        
        return "[Could not decode file content]"

    def collect_files(self):
        """Collect all relevant files from the project."""
        files_data = []
        
        for root, dirs, files in os.walk(self.project_path, topdown=True):
            # Filter directories
            dirs[:] = [d for d in dirs if self.should_include_directory(Path(root) / d)]
            
            for file in files:
                file_path = Path(root) / file
                
                if self.should_include_file(file_path):
                    try:
                        relative_path = file_path.relative_to(self.project_path)
                        content = self.read_file_content(file_path)
                        
                        files_data.append({
                            'path': str(relative_path).replace('\\', '/'),
                            'content': content,
                            'size': file_path.stat().st_size
                        })
                    except Exception as e:
                        print(f"⚠️  Skipping {file_path}: {e}")
        
        # Custom sorting for Laravel projects
        def sort_key(file_data):
            path = file_data['path']
            path_parts = path.split('/')
            
            # Define order of top-level directories
            order = {
                'routes': 1,
                'app': 2,
                'database': 3,
                'resources': 4,
                'config': 5,
                'tests': 6,
                'public': 7,
            }

            if len(path_parts) == 1:  # Root files
                return (0, path)
            
            main_dir = path_parts[0]
            dir_order = order.get(main_dir, 99) # Other directories last
            
            return (dir_order, path)
        
        files_data.sort(key=sort_key)
        return files_data

    def generate_output_file(self, files_data):
        """Generate the output text file."""
        total_files = len(files_data)
        total_size = sum(file['size'] for file in files_data)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            # Header
            project_name = {
                'laravel': 'Laravel',
                'generic': 'Project'
            }.get(self.project_type, 'Project')
            
            f.write(f"{project_name} Code Extraction\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Project: {self.project_path}\n")
            f.write(f"Files: {total_files} ({total_size:,} bytes)\n")
            f.write("=" * 80 + "\n\n")
            
            # File contents
            for file_data in files_data:
                f.write(f"### {file_data['path']} :\n\n")
                f.write("```\n")
                f.write(file_data['content'])
                if not file_data['content'].endswith('\n'):
                    f.write('\n')
                f.write("```\n\n\n")

    def print_extraction_summary(self, files_data):
        """Print detailed extraction summary to console."""
        total_size = sum(file['size'] for file in files_data)
        
        print("\n" + "=" * 60)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 60)
        
        # Count files by extension
        file_types = {}
        for file_data in files_data:
            ext = ''.join(Path(file_data['path']).suffixes).lower() or 'no extension'
            file_types[ext] = file_types.get(ext, 0) + 1
        
        print("📈 Files by Type:")
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {ext:15} {count:3d} files")
        
        print(f"\n📁 Files by Directory:")
        
        # Directory tree for summary
        dir_tree = {}
        for file_data in files_data:
            path_parts = Path(file_data['path']).parts
            current_level = dir_tree
            for part in path_parts[:-1]:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
            
            filename = path_parts[-1]
            if '__files__' not in current_level:
                current_level['__files__'] = []
            current_level['__files__'].append(filename)

        def print_directory(dir_dict, indent=0):
            # Prioritize certain directories for printing order
            priority_dirs = ['routes', 'app', 'database', 'resources', 'config', 'tests', 'public']
            
            sorted_dirs = sorted(
                dir_dict.keys(),
                key=lambda x: (priority_dirs.index(x) if x in priority_dirs else 99, x)
            )

            for key in sorted_dirs:
                if key == '__files__':
                    continue
                print(f"{' ' * indent}📂 {key}/")
                
                if '__files__' in dir_dict[key]:
                    for filename in sorted(dir_dict[key]['__files__']):
                        print(f"{' ' * (indent + 4)}└─ {filename}")
                
                print_directory(dir_dict[key], indent + 2)

        # Print root files first
        if '__files__' in dir_tree:
            print("📂 root/")
            for filename in sorted(dir_tree['__files__']):
                print(f"    └─ {filename}")
        
        print_directory({k: v for k, v in dir_tree.items() if k != '__files__'})
        
        # Total size with human readable format
        size_kb = total_size / 1024
        size_mb = size_kb / 1024
        
        if size_mb >= 1:
            size_display = f"({size_mb:.1f} MB)"
        else:
            size_display = f"({size_kb:.1f} KB)"
            
        print(f"\n💾 Total Size: {total_size:,} bytes {size_display}")
        print("=" * 60)

    def extract(self):
        """Main extraction process."""
        if not self.project_path.exists():
            print(f"❌ Error: Path '{self.project_path}' does not exist")
            return False
        
        print(f"📁 Extracting from: {self.project_path}")
        print(f"📄 Output file: {self.output_file}")
        
        try:
            files_data = self.collect_files()
            
            if not files_data:
                print("❌ No files found to extract")
                return False
            
            self.generate_output_file(files_data)
            
            print(f"✅ Successfully extracted {len(files_data)} files")
            
            self.print_extraction_summary(files_data)
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract Laravel project code to a single text file"
    )
    parser.add_argument(
        "project_path", 
        nargs="?", 
        default=".", 
        help="Project directory path (default: current directory)"
    )
    parser.add_argument(
        "-o", "--output", 
        default="project-code.txt",
        help="Output file name (default: project-code.txt)"
    )
    
    args = parser.parse_args()
    
    extractor = ProjectCodeExtractor(args.project_path, args.output)
    success = extractor.extract()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()