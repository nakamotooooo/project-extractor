# Project Code Extractor

A Python tool that extracts and consolidates source code from NestJS, Next.js, or generic JavaScript/TypeScript projects into a single, organized text file for documentation, analysis, or AI assistance.

## Features

- 🔍 **Auto-Detection**: Automatically detects project type (Next.js, NestJS, or generic)
- 📁 **Smart Filtering**: Intelligently excludes build artifacts, dependencies, and test files
- 📊 **Detailed Summary**: Provides comprehensive extraction statistics and directory structure
- 🎯 **Configurable**: Customizable file extensions and exclusion patterns
- 🌐 **Multi-Encoding Support**: Handles various file encodings gracefully
- 📝 **Organized Output**: Groups files by directory with clear formatting

## Supported File Types

The extractor includes the following file types by default:

- **Code**: `.ts`, `.tsx`, `.js`, `.jsx`
- **Configuration**: `.json`, `.env`, `.env.local`, `.env.example`
- **Templates**: `.hbs`, `.html`
- **Database**: `.sql`, `.prisma`
- **GraphQL**: `.graphql`, `.gql`

## Installation

1. Clone this repository:
```bash
git clone https://github.com/nakamotooooo/project-extractor.git
cd project-extractor
```

2. Ensure Python 3.6+ is installed:
```bash
python --version
```

3. Make the script executable (Linux/Mac):
```bash
chmod +x extractor.py
```

## Usage

### Basic Usage

Extract code from the current directory:
```bash
python extractor.py
```

### Specify Project Path

Extract from a specific project directory:
```bash
python extractor.py /path/to/your/project
```

### Custom Output File

Specify a custom output filename:
```bash
python extractor.py -o my-output.txt
```

### Combined Options

```bash
python extractor.py /path/to/project -o custom-name.txt
```

## Output

The script generates a text file with:

1. **Header Section**: Project metadata, timestamp, file count, and total size
2. **Code Files**: All extracted files with syntax highlighting markers
3. **Console Summary**: Detailed breakdown by file type and directory structure

### Example Output Format

```
Next.js Code Extraction
Generated: 2024-01-15 14:30:00
Project: /path/to/project
Files: 42 (125,000 bytes)
================================================================================

### src/app/page.tsx :

```
// File contents here...
```


### src/components/Header.tsx :

```
// File contents here...
```
```

## Project Detection

The tool automatically detects your project type by checking:

- **Next.js**: Presence of `next` in dependencies or `next.config.js/ts/mjs`
- **NestJS**: Presence of `@nestjs/core` in dependencies or `nest-cli.json`
- **Generic**: Falls back to generic JavaScript/TypeScript project settings

## Excluded Directories

The following directories are automatically excluded:

- `node_modules`, `.git`, `.vscode`, `.idea`
- `coverage`, `.nyc_output`, `logs`, `tmp`, `temp`
- `test`, `public`
- **Next.js**: `.next`, `out`, `build`, `dist`, `.vercel`, `.netlify`
- **NestJS**: `dist`, `build`

## Excluded Files

- `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- `.gitignore`
- Test files: `*.spec.ts`
- Type definition files: `next-env.d.ts`

## Customization

To modify which files are included or excluded, edit these sections in the script:

```python
# File extensions to include
self.include_extensions = {
    '.ts', '.js', '.tsx', '.jsx',
    # Add more extensions...
}

# Directories to exclude
self.base_exclude_dirs = {
    'node_modules', '.git',
    # Add more directories...
}
```

## Use Cases

- 📚 **Documentation**: Generate complete project documentation
- 🤖 **AI Analysis**: Feed entire codebase to AI assistants like Claude or ChatGPT
- 🔍 **Code Review**: Get a comprehensive view of project structure
- 📦 **Archiving**: Create text-based snapshots of your codebase
- 🎓 **Learning**: Study project architecture and patterns

## Example Console Output

```
🔍 Analyzing project at: /home/user/my-app
✅ Detected: Next.js project
📁 Extracting from: /home/user/my-app
📄 Output file: nextjs-project-code.txt
✅ Successfully extracted 42 files

📋 All files:
   • package.json
   • next.config.js
   • src/app/layout.tsx
   • src/app/page.tsx
   ...

============================================================
📊 EXTRACTION SUMMARY
============================================================
📈 Files by Type:
  .tsx          15 files
  .ts           12 files
  .json          8 files
  .css           5 files
  .env           2 files

📁 Files by Directory:
  📂 root/
    └─ package.json
    └─ next.config.js
  📂 src/
     📂 app/
       └─ layout.tsx
       └─ page.tsx
     📂 components/
       └─ Header.tsx
       └─ Footer.tsx

💾 Total Size: 125,000 bytes (122.1 KB)
============================================================
```

## Requirements

- Python 3.6 or higher
- No external dependencies required (uses only Python standard library)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this tool in your projects.

## Troubleshooting

### Files not being extracted

Check that:
- File extensions are in the `include_extensions` set
- Parent directories are not in the exclusion list
- Files are not in the `exclude_files` set

### Encoding errors

The script automatically tries multiple encodings (UTF-8, Latin1, CP1252). If you still encounter issues, the file content will be marked as unreadable.

### Permission errors

Ensure you have read permissions for all project files and write permission in the output directory.

## Author

Created for developers who need to consolidate project code for documentation, analysis, or AI-assisted development.

## Links

- [GitHub Repository](https://github.com/nakamotooooo/project-extractor)
- [Report Issues](https://github.com/nakamotooooo/project-extractor/issues)

---

**Happy Extracting! 🚀**