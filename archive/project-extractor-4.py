#!/usr/bin/env python3
"""
Project Code Extractor for NestJS and Next.js

This script traverses NestJS or Next.js project directories and extracts all relevant
source code files into a single text file for documentation or analysis.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

class ProjectCodeExtractor:
    def __init__(self, project_path=".", output_file="project_code.txt"):
        self.project_path = Path(project_path).resolve()
        self.output_file = output_file
        
        # Detect project type
        self.project_type = self.detect_project_type()
        
        # File extensions to include
        self.include_extensions = {
            '.ts', '.js', '.tsx', '.jsx',           # TypeScript/JavaScript files
            '.json',                                # Configuration files
            '.env', '.env.local', '.env.example',   # Environment files
            '.yml', '.yaml',                        # YAML configuration
            #'.md', '.mdx',                          # Documentation
            '.hbs', '.html',                        # Template files
            #'.css', '.scss', '.sass', '.less',      # Style files
            '.module.css', '.module.scss',          # CSS modules
            '.sql',                                 # SQL files
            '.graphql', '.gql',                     # GraphQL files
            '.prisma',                              # Prisma schema
        }
        
        # Base directories to exclude
        self.base_exclude_dirs = {
            'node_modules', '.git', '.vscode', '.idea',
            'coverage', '.nyc_output', 'logs', 'tmp', 'temp' , 'public'
        }
        
        # Configure based on project type
        self.configure_for_project_type()

    def detect_project_type(self):
        """Detect if this is a Next.js, NestJS, or generic project."""
        print(f"🔍 Analyzing project at: {self.project_path}")
        
        # Check package.json
        package_json_path = self.project_path / 'package.json'
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    
                dependencies = {
                    **package_data.get('dependencies', {}),
                    **package_data.get('devDependencies', {})
                }
                
                if 'next' in dependencies:
                    print("✅ Detected: Next.js project")
                    return "nextjs"
                elif '@nestjs/core' in dependencies:
                    print("✅ Detected: NestJS project")
                    return "nestjs"
            except Exception as e:
                print(f"⚠️  Could not read package.json: {e}")
        
        # Check for config files
        if any((self.project_path / f).exists() for f in ['next.config.js', 'next.config.ts', 'next.config.mjs']):
            print("✅ Detected: Next.js project (found config)")
            return "nextjs"
            
        if (self.project_path / 'nest-cli.json').exists():
            print("✅ Detected: NestJS project (found nest-cli.json)")
            return "nestjs"
        
        print("ℹ️  Generic project detected")
        return "generic"

    def configure_for_project_type(self):
        """Configure extraction rules based on project type."""
        if self.project_type == "nextjs":
            self.exclude_dirs = self.base_exclude_dirs | {
                '.next', 'out', 'build', 'dist', '.vercel', '.netlify'
            }
            self.exclude_files = {
                'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
                'next-env.d.ts', '.gitignore' , 'README.md'
            }
        elif self.project_type == "nestjs":
            self.exclude_dirs = self.base_exclude_dirs | {
                'dist', 'build'
            }
            self.exclude_files = {
                'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
                '.gitignore' , 'README.md'
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
        
        # Check extension
        if file_path.suffix.lower() not in self.include_extensions and file_path.name not in self.include_extensions:
            return False
            
        # Check if excluded
        if file_path.name in self.exclude_files:
            return False
            
        return True

    def should_include_directory(self, dir_path):
        """Check if directory should be traversed."""
        dir_name = Path(dir_path).name
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
        
        # Sort by path
        files_data.sort(key=lambda x: x['path'])
        return files_data

    def generate_output_file(self, files_data):
        """Generate the output text file."""
        total_files = len(files_data)
        total_size = sum(file['size'] for file in files_data)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            # Header
            project_name = {
                'nextjs': 'Next.js',
                'nestjs': 'NestJS', 
                'generic': 'Project'
            }.get(self.project_type, 'Project')
            
            f.write(f"{project_name} Code Extraction\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Project: {self.project_path}\n")
            f.write(f"Files: {total_files} ({total_size:,} bytes)\n")
            f.write("=" * 80 + "\n\n")
            
            # File contents
            for file_data in files_data:
                f.write(f"this is my {file_data['path']} :\n\n")
                f.write("```\n")
                f.write(file_data['content'])
                if not file_data['content'].endswith('\n'):
                    f.write('\n')
                f.write("```\n\n\n")

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
            print(f"📊 Total size: {sum(f['size'] for f in files_data):,} bytes")
            
            # Show sample files
            print(f"📋 Sample files:")
            for file_data in files_data[:5]:
                print(f"   • {file_data['path']}")
            if len(files_data) > 5:
                print(f"   ... and {len(files_data) - 5} more files")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract NestJS/Next.js project code to text file"
    )
    parser.add_argument(
        "project_path", 
        nargs="?", 
        default=".", 
        help="Project directory path (default: current directory)"
    )
    parser.add_argument(
        "-o", "--output", 
        default="project_code.txt",
        help="Output file name (default: project_code.txt)"
    )
    
    args = parser.parse_args()
    
    extractor = ProjectCodeExtractor(args.project_path, args.output)
    success = extractor.extract()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()