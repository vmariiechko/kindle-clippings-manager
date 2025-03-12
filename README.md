# Kindle Clippings Manager

A powerful tool to organize, deduplicate, and export your Kindle highlights and notes.

![Kindle Clippings Manager](https://img.shields.io/badge/Kindle-Clippings%20Manager-orange)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 📚 Overview

Kindle Clippings Manager helps you take control of your Kindle highlights and notes by:

- Parsing the "My Clippings.txt" file directly from your Kindle
- Removing duplicate highlights
- Matching notes to their corresponding highlights
- Organizing content by categories extracted from your notes
- Exporting to various formats (markdown, bullet points, or original format)

## ✨ Features

- **Direct Parsing**: Works directly with the "My Clippings.txt" file from your Kindle
- **Smart Deduplication**: Intelligently removes duplicate highlights while keeping the most recent versions
- **Note Matching**: Automatically matches notes to their corresponding highlights
- **Category Extraction**: Extracts categories from your notes using a simple syntax: `(Category>Subcategory) Your note text`
- **Multiple Export Formats**:
  - **Markdown**: Hierarchical organization by categories
  - **Bullet Points**: Simple bullet-point format organized by book
  - **Default**: Original Kindle format with duplicates removed

## 🚀 Installation

### Using Poetry (recommended)

```bash
# Clone the repository
git clone https://github.com/vmariiechko/kindle-clippings-manager
cd kindle-clippings-manager

# Install dependencies with Poetry
poetry install

# Activate the virtual environment
poetry shell
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/vmariiechko/kindle-clippings-manager
cd kindle-clippings-manager

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Usage

### Basic Usage

1. Connect your Kindle to your computer
2. Copy the "My Clippings.txt" file from your Kindle to the project directory
3. Run the CLI tool:

```bash
# Using Poetry
poetry run kindle-clippings -f markdown

# Or directly with Python
python src/cli/main.py -f markdown
```

4. Select a book from the interactive menu (or press Enter to process all books)
5. Find your organized notes in the output file (default: "Categorized Notes.md")

## 📝 Note Categorization

You can categorize your notes by adding category markers at the beginning of your notes on your Kindle:

- **Simple category**: `(Category) Your note text`
- **Hierarchical categories**: `(MainCategory>Subcategory) Your note text`
- **Multiple categories**: `(Category1) (Category2) Your note text`
- **Using shortcuts**: `(P) Your note about protein` (will be expanded to "Protein")


You can customize these shortcuts by editing the `GROUP_MAPPING` dictionary in `src/utils/text_utils.py`.

## 📊 Example Output

### Markdown Format

```markdown
# Category1

* This is a highlighted text from your Kindle.

  **Note**: *This is my note about the highlight.*

## Subcategory

* Another highlighted text that belongs to a subcategory.

  **Note**: *My thoughts on this particular highlight.*

# Category2

* A highlight in a different category.
```

### Bullet Format

```
=========== Book Title (Author) ===========

* This is a highlighted text from your Kindle.
  - Note: This is my note about the highlight.

* Another highlighted text.
```

## 🧪 Running Tests

```bash
# Using Poetry
poetry run pytest
```


## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Made with ❤️ for Kindle readers who love to highlight and take notes
