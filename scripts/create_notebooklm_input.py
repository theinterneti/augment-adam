import os
from pathlib import Path
import logging

# --- Configuration ---
VSCODE_EXTENSION_DIR = Path("/workspace/vscode-extension")
OUTPUT_DIR = Path("/workspace/notebooklm_input")
OUTPUT_FILENAMES = {
    "source": OUTPUT_DIR / "vscode_extension_source_code.md",
    "config_meta": OUTPUT_DIR / "vscode_extension_config_metadata.md",
    "docs_other": OUTPUT_DIR / "vscode_extension_docs_other.md",
}

# File extensions/names for categorization
SOURCE_EXTENSIONS = {".ts", ".js"}
CONFIG_FILES = {
    "package.json",
    "package-lock.json",
    ".vscodeignore",
    ".gitignore",
    "tsconfig.json",
    "launch.json",
    "tasks.json",
}
CONFIG_EXTENSIONS = {".json"} # Exclude already matched config files
LINT_CONFIG_PATTERNS = {".eslintrc", ".prettierrc"} # Check startswith
DOC_EXTENSIONS = {".md"}
DOC_FILES = {"LICENSE", "README"} # Check startswith, case-insensitive

# Files/Dirs to explicitly ignore
IGNORE_PATTERNS = {"node_modules", ".git", "__pycache__", ".DS_Store"}
IGNORE_EXTENSIONS = {".map", ".ico", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".woff", ".woff2", ".ttf", ".eot"} # Source maps and binary files

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper Functions ---

def get_category(filepath: Path) -> str | None:
    """Categorizes a file based on its name and extension."""
    if any(part in IGNORE_PATTERNS for part in filepath.parts) or \
       filepath.name in IGNORE_PATTERNS or \
       filepath.suffix.lower() in IGNORE_EXTENSIONS:
        return None # Ignore this file

    # Prioritize specific filenames
    if filepath.name in CONFIG_FILES:
        return "config_meta"
    if filepath.name.lower().startswith(tuple(df.lower() for df in DOC_FILES)):
         return "docs_other"
    if any(filepath.name.startswith(pattern) for pattern in LINT_CONFIG_PATTERNS):
        return "config_meta"

    # Categorize by extension
    ext = filepath.suffix.lower()
    if ext in SOURCE_EXTENSIONS:
        return "source"
    if ext in CONFIG_EXTENSIONS: # Already checked specific json files
        return "config_meta"
    if ext in DOC_EXTENSIONS:
        return "docs_other"

    # Default category for other text-like files (can be adjusted)
    # Add more specific checks above if needed
    try:
        # Simple check if it looks like text
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            f.read(100) # Try reading a bit
        return "docs_other" # Put remaining text files here
    except Exception:
        logging.warning(f"Could not read or categorize file: {filepath}. Skipping.")
        return None


def get_markdown_language(filepath: Path) -> str:
    """Suggests a language hint for Markdown code blocks."""
    ext = filepath.suffix.lower()
    if ext == ".ts":
        return "typescript"
    if ext == ".js":
        return "javascript"
    if ext == ".json":
        return "json"
    if ext == ".md":
        return "markdown"
    # Add more mappings if needed
    return "" # Default to no language hint

# --- Main Script ---

def main():
    """Walks the directory, categorizes files, and writes to output MD files."""
    if not VSCODE_EXTENSION_DIR.is_dir():
        logging.error(f"Error: Directory not found - {VSCODE_EXTENSION_DIR}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Clear existing output files
    for outfile in OUTPUT_FILENAMES.values():
        outfile.unlink(missing_ok=True)

    file_contents = {key: [] for key in OUTPUT_FILENAMES}
    processed_files = 0
    ignored_files = 0

    logging.info(f"Starting scan of {VSCODE_EXTENSION_DIR}...")

    for root, _, files in os.walk(VSCODE_EXTENSION_DIR):
        root_path = Path(root)
        for filename in files:
            filepath = root_path / filename
            relative_path = filepath.relative_to(VSCODE_EXTENSION_DIR)

            category = get_category(filepath)

            if category:
                try:
                    content = filepath.read_text(encoding="utf-8")
                    lang = get_markdown_language(filepath)
                    header = f"\n\n---\n\n### File: `{relative_path}`\n\n"
                    if lang:
                        formatted_content = f"{header}```{lang}\n{content}\n```\n"
                    else:
                        # For non-code files, just include content without backticks
                        # unless it's markdown itself
                        if lang == "markdown":
                             formatted_content = f"{header}```markdown\n{content}\n```\n"
                        else:
                             formatted_content = f"{header}{content}\n"

                    file_contents[category].append(formatted_content)
                    processed_files += 1
                    logging.debug(f"Processed: {relative_path} -> {category}")
                except UnicodeDecodeError:
                    logging.warning(f"Skipping file due to encoding error: {filepath}")
                    ignored_files += 1
                except Exception as e:
                    logging.warning(f"Skipping file due to error reading {filepath}: {e}")
                    ignored_files += 1
            else:
                # Check if it wasn't explicitly ignored by patterns/extensions
                if not (any(part in IGNORE_PATTERNS for part in filepath.parts) or \
                        filepath.name in IGNORE_PATTERNS or \
                        filepath.suffix.lower() in IGNORE_EXTENSIONS):
                    logging.info(f"Ignored (uncategorized/binary): {relative_path}")
                    ignored_files +=1


    logging.info(f"Scan complete. Processed {processed_files} files, ignored {ignored_files}.")

    # Write concatenated content to files
    for category, outfile in OUTPUT_FILENAMES.items():
        if file_contents[category]:
            logging.info(f"Writing {len(file_contents[category])} sections to {outfile}...")
            full_content = f"# VS Code Extension: {category.replace('_', ' ').title()}\n\n" + "".join(file_contents[category])
            try:
                outfile.write_text(full_content, encoding="utf-8")
                logging.info(f"Successfully wrote {outfile}")
            except Exception as e:
                logging.error(f"Error writing to {outfile}: {e}")
        else:
            logging.info(f"No content found for category '{category}', skipping file {outfile}.")

    logging.info("Script finished.")

if __name__ == "__main__":
    main()
