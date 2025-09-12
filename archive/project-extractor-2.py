#!/usr/bin/env python3
"""
NestJS Project Code Extractor

This script traverses a NestJS project directory and extracts all relevant
source code files into a single text file for easy documentation or analysis.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

class NestJSCodeExtractor:
    def __init__(self, project_path=".", output_file="project_code.txt"):
        self.project_path = Path(project_path).resolve()
        self.output_file = output_file
        
        # File extensions to include
        self.include_extensions = {
            '.ts', '.js', '.tsx', '.jsx',           # TypeScript/JavaScript files
            '.json',                                # Configuration files
            '.env', '.env.example',                 # Environment files
            '.yml', '.yaml',                        # YAML configuration
            '.md',                                  # Documentation
            '.hbs', '.html',                        # Template files
            '.css', '.scss', '.sass',               # Style files
            '.sql',                                 # SQL files
            '.graphql', '.gql'                      # GraphQL files
        }
        
        # Directories to exclude
        self.exclude_dirs = {
            'node_modules', 'dist', 'build', '.git', 
            '.vscode', '.idea', 'coverage', '.nyc_output',
            'logs', 'tmp', 'temp', '__pycache__'
        }
        
        # Files to exclude
        self.exclude_files = {
            'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
            '.gitignore', '.eslintrc.js', '.prettierrc',
            'tsconfig.json', 'nest-cli.json'  # These can be included if needed
        }

    def should_include_file(self, file_path):
        """Determine if a file should be included in the extraction."""
        file_path = Path(file_path)
        
        # Check file extension
        if file_path.suffix.lower() not in self.include_extensions and file_path.name not in self.include_extensions:
            return False
            
        # Check if file is in exclude list
        if file_path.name in self.exclude_files:
            return False
            
        return True

    def should_include_directory(self, dir_path):
        """Determine if a directory should be traversed."""
        dir_name = Path(dir_path).name
        return dir_name not in self.exclude_dirs

    def get_relative_path(self, file_path):
        """Get relative path from project root."""
        try:
            return file_path.relative_to(self.project_path)
        except ValueError:
            return file_path

    def extract_file_content(self, file_path):
        """Extract content from a file, handling different encodings."""
        encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
                return f"[Error reading file: {e}]"
        
        print(f"Warning: Could not decode {file_path} with any encoding")
        return "[Could not decode file content]"

    def traverse_project(self):
        """Traverse the project directory and collect all relevant files."""
        files_data = []
        
        for root, dirs, files in os.walk(self.project_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if self.should_include_directory(Path(root) / d)]
            
            for file in files:
                file_path = Path(root) / file
                
                if self.should_include_file(file_path):
                    relative_path = self.get_relative_path(file_path)
                    content = self.extract_file_content(file_path)
                    
                    files_data.append({
                        'path': str(relative_path).replace('\\', '/'),  # Use forward slashes
                        'content': content,
                        'size': file_path.stat().st_size if file_path.exists() else 0
                    })
        
        # Sort files by path for consistent output
        files_data.sort(key=lambda x: x['path'])
        return files_data

    def generate_output(self, files_data):
        """Generate the output text file."""
        total_files = len(files_data)
        total_size = sum(file['size'] for file in files_data)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"NestJS Project Code Extraction\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Project Path: {self.project_path}\n")
            f.write(f"Total Files: {total_files}\n")
            f.write(f"Total Size: {total_size:,} bytes\n")
            f.write("=" * 80 + "\n\n")
            
            # Write file contents
            for i, file_data in enumerate(files_data, 1):
                f.write(f"this is my {file_data['path']} :\n\n")
                f.write("```\n")
                f.write(file_data['content'])
                f.write("\n```\n\n")
                
                # Add separator between files (except for the last one)
                if i < total_files:
                    f.write("\n")

    def extract(self):
        """Main extraction process."""
        if not self.project_path.exists():
            print(f"Error: Project path '{self.project_path}' does not exist.")
            return False
            
        print(f"Extracting code from: {self.project_path}")
        print(f"Output file: {self.output_file}")
        
        try:
            files_data = self.traverse_project()
            
            if not files_data:
                print("No relevant files found in the project directory.")
                return False
                
            self.generate_output(files_data)
            print(f"Successfully extracted {len(files_data)} files to '{self.output_file}'")
            
            # Print summary
            print("\nFile Summary:")
            for file_data in files_data[:10]:  # Show first 10 files
                print(f"  - {file_data['path']}")
            
            if len(files_data) > 10:
                print(f"  ... and {len(files_data) - 10} more files")
                
            return True
            
        except Exception as e:
            print(f"Error during extraction: {e}")
            return False

def main():
    """Main function to run the extractor."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract NestJS project code to a text file")
    parser.add_argument("project_path", nargs="?", default=".", 
                       help="Path to the NestJS project directory (default: current directory)")
    parser.add_argument("-o", "--output", default="project_code.txt",
                       help="Output file name (default: project_code.txt)")
    parser.add_argument("--include-config", action="store_true",
                       help="Include configuration files like tsconfig.json, package.json")
    
    args = parser.parse_args()
    
    extractor = NestJSCodeExtractor(args.project_path, args.output)
    
    # Include config files if requested
    if args.include_config:
        extractor.exclude_files -= {'tsconfig.json', 'nest-cli.json', 'package.json'}
    
    success = extractor.extract()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()