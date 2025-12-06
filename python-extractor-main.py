#!/usr/bin/env python3
"""
Project Code Extractor for Python Projects

This script traverses Python project directories and extracts all relevant
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
        
        # File extensions to include
        self.include_extensions = {
            '.py', '.pyw',                          # Python files
            '.pyi',                                 # Python stub files
            '.txt',                                 # Requirements and text files
            '.toml',                                # pyproject.toml, poetry configs
            '.cfg', '.ini',                         # Configuration files
            '.yaml', '.yml',                        # YAML configuration
            '.json',                                # JSON config files
            '.env', '.env.local', '.env.example',   # Environment files
            '.sql',                                 # SQL files
            '.sh',                                  # Shell scripts
            '.md',                                  # Documentation
        }
        
        # Specific filenames to include (without extensions)
        self.include_files = {
            'requirements.txt', 'requirements-dev.txt', 'requirements-test.txt',
            'setup.py', 'setup.cfg', 'pyproject.toml', 'poetry.lock',
            'Pipfile', 'Pipfile.lock', 'tox.ini', 'pytest.ini',
            'Makefile', 'Dockerfile', '.dockerignore',
            'manifest.in', 'MANIFEST.in',
        }
        
        # Base directories to exclude
        self.base_exclude_dirs = {
            '__pycache__', '.git', '.vscode', '.idea', '.pytest_cache',
            'venv', 'env', '.env', 'virtualenv', '.venv',
            'node_modules', 'coverage', '.coverage', 'htmlcov',
            '.tox', '.mypy_cache', '.ruff_cache', 'dist', 'build',
            '*.egg-info', '.eggs', 'logs', 'tmp', 'temp',
            '.ipynb_checkpoints', 'test', 'tests', '__pypackages__',
        }
        
        # Configure based on project type
        self.configure_for_project_type()

    def detect_project_type(self):
        """Detect Python project type (Django, Flask, FastAPI, or generic)."""
        print(f"🔍 Analyzing project at: {self.project_path}")
        
        # Check for Django
        if (self.project_path / 'manage.py').exists():
            # Verify it's actually Django by checking content
            try:
                with open(self.project_path / 'manage.py', 'r') as f:
                    content = f.read()
                    if 'django' in content.lower():
                        print("✅ Detected: Django project")
                        return "django"
            except:
                pass
        
        # Check requirements.txt or pyproject.toml for framework detection
        frameworks = {
            'django': ['django'],
            'flask': ['flask'],
            'fastapi': ['fastapi'],
        }
        
        detected = self.check_dependencies(frameworks)
        if detected:
            print(f"✅ Detected: {detected.capitalize()} project")
            return detected
        
        # Check for common Python project indicators
        python_indicators = [
            'setup.py', 'pyproject.toml', 'requirements.txt', 
            'Pipfile', 'poetry.lock'
        ]
        
        if any((self.project_path / f).exists() for f in python_indicators):
            print("✅ Detected: Python project")
            return "python"
        
        # Check if there are any .py files
        py_files = list(self.project_path.rglob('*.py'))
        if py_files:
            print("✅ Detected: Python project (found .py files)")
            return "python"
        
        print("ℹ️  Generic project detected")
        return "generic"

    def check_dependencies(self, frameworks):
        """Check requirements files for framework dependencies."""
        # Check requirements.txt
        req_file = self.project_path / 'requirements.txt'
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    content = f.read().lower()
                    for name, keywords in frameworks.items():
                        if any(kw in content for kw in keywords):
                            return name
            except:
                pass
        
        # Check pyproject.toml
        pyproject = self.project_path / 'pyproject.toml'
        if pyproject.exists():
            try:
                with open(pyproject, 'r') as f:
                    content = f.read().lower()
                    for name, keywords in frameworks.items():
                        if any(kw in content for kw in keywords):
                            return name
            except:
                pass
        
        # Check setup.py
        setup_py = self.project_path / 'setup.py'
        if setup_py.exists():
            try:
                with open(setup_py, 'r') as f:
                    content = f.read().lower()
                    for name, keywords in frameworks.items():
                        if any(kw in content for kw in keywords):
                            return name
            except:
                pass
        
        return None

    def configure_for_project_type(self):
        """Configure extraction rules based on project type."""
        if self.project_type == "django":
            self.exclude_dirs = self.base_exclude_dirs | {
                'staticfiles', 'static', 'media', 'migrations'
            }
            self.exclude_files = {
                '*.pyc', '*.pyo', '*.pyd', '.gitignore',
                'db.sqlite3', '*.sqlite', '*.db',
            }
        elif self.project_type == "flask":
            self.exclude_dirs = self.base_exclude_dirs | {
                'static', 'instance'
            }
            self.exclude_files = {
                '*.pyc', '*.pyo', '*.pyd', '.gitignore',
                '*.db', '*.sqlite'
            }
        elif self.project_type == "fastapi":
            self.exclude_dirs = self.base_exclude_dirs
            self.exclude_files = {
                '*.pyc', '*.pyo', '*.pyd', '.gitignore',
            }
        else:  # python or generic
            self.exclude_dirs = self.base_exclude_dirs
            self.exclude_files = {
                '*.pyc', '*.pyo', '*.pyd', '.gitignore',
            }

    def should_include_file(self, file_path):
        """Check if file should be included."""
        file_path = Path(file_path)
        
        # Exclude test files
        if file_path.name.startswith('test_') or file_path.name.endswith('_test.py'):
            return False
        
        # Check if it's in the specific include files
        if file_path.name.lower() in self.include_files:
            return True
        
        # Check extension
        if file_path.suffix.lower() not in self.include_extensions:
            return False
            
        # Check if excluded
        if file_path.name in self.exclude_files:
            return False
        
        # Exclude compiled Python files
        if file_path.suffix in {'.pyc', '.pyo', '.pyd'}:
            return False
            
        return True

    def should_include_directory(self, dir_path):
        """Check if directory should be traversed."""
        dir_name = Path(dir_path).name
        
        # Check exact matches
        if dir_name in self.exclude_dirs:
            return False
        
        # Check pattern matches (e.g., *.egg-info)
        for pattern in self.exclude_dirs:
            if '*' in pattern:
                pattern_without_star = pattern.replace('*', '')
                if pattern.startswith('*') and dir_name.endswith(pattern_without_star):
                    return False
                if pattern.endswith('*') and dir_name.startswith(pattern_without_star):
                    return False
        
        return True

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
        
        for root, dirs, files in os.walk(self.project_path):
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
        
        # Sort to group folders and subfolders together
        def sort_key(file_data):
            path = file_data['path']
            path_parts = path.split('/')
            
            if len(path_parts) == 1:  # Root files
                return (0, '', path)
            else:  # Files in subdirectories
                main_dir = path_parts[0]
                if len(path_parts) == 2:
                    return (1, main_dir, path)
                else:
                    sub_dir = path_parts[1]
                    return (2, f"{main_dir}/{sub_dir}", path)
        
        files_data.sort(key=sort_key)
        return files_data

    def generate_output_file(self, files_data):
        """Generate the output text file."""
        total_files = len(files_data)
        total_size = sum(file['size'] for file in files_data)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            # Header
            project_name = {
                'django': 'Django',
                'flask': 'Flask',
                'fastapi': 'FastAPI',
                'python': 'Python',
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
            ext = Path(file_data['path']).suffix.lower() or 'no extension'
            file_types[ext] = file_types.get(ext, 0) + 1
        
        print("📈 Files by Type:")
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {ext:12} {count:3d} files")
        
        print(f"\n📁 Files by Directory:")
        
        # Build hierarchical directory structure
        dir_tree = {}
        
        for file_data in files_data:
            path_parts = Path(file_data['path']).parts
            
            if len(path_parts) == 1:
                # Root files
                if 'root' not in dir_tree:
                    dir_tree['root'] = {'files': [], 'subdirs': {}}
                dir_tree['root']['files'].append(file_data['path'])
            else:
                # Navigate/create the directory tree
                current_level = dir_tree
                full_path = []
                
                for i, part in enumerate(path_parts[:-1]):
                    full_path.append(part)
                    path_key = '/'.join(full_path)
                    
                    if path_key not in current_level:
                        current_level[path_key] = {'files': [], 'subdirs': {}}
                    
                    if i < len(path_parts) - 2:
                        current_level = current_level[path_key]['subdirs']
                    else:
                        current_level[path_key]['files'].append(path_parts[-1])
        
        # Print the hierarchical structure
        def print_directory(dir_dict, indent=2):
            sorted_dirs = sorted(dir_dict.items(), key=lambda x: (x[0] != 'root', x[0]))
            
            for dir_path, dir_info in sorted_dirs:
                if dir_path == 'root':
                    print(f"{' ' * indent}📂 root/")
                else:
                    dir_parts = dir_path.split('/')
                    current_indent = indent + (len(dir_parts) - 1) * 3
                    print(f"{' ' * current_indent}📂 {dir_parts[-1]}/")
                
                # Print files in this directory
                file_indent = indent + len(dir_path.split('/')) * 3 + 2
                for filename in sorted(dir_info['files']):
                    print(f"{' ' * file_indent}└─ {filename}")
                
                # Print subdirectories recursively
                if dir_info['subdirs']:
                    print_directory(dir_info['subdirs'], indent + 3)
        
        print_directory(dir_tree)
        
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
            
            # Show ALL files (no truncation)
            print(f"\n📋 All files:")
            for file_data in files_data:
                print(f"   • {file_data['path']}")
            
            # Show detailed extraction summary with proper directory grouping
            self.print_extraction_summary(files_data)
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract Python project code to text file"
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