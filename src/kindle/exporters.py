import re
from pathlib import Path
from typing import Any, Dict, List

from src.kindle.models import ProcessedHighlight


class MarkdownExporter:
    """Exporter for Kindle clippings to Markdown format."""

    def __init__(self, highlights: List[ProcessedHighlight], output_path: Path):
        """Initialize the exporter with highlights and output path."""
        self.highlights = highlights
        self.output_path = output_path

    def export(self) -> None:
        """Export highlights to a markdown file with hierarchical categories."""
        category_tree = self._build_category_tree()

        with open(self.output_path, "w", encoding="utf-8") as f:
            self._write_category_to_markdown(category_tree, f)

    def _normalize_category(self, category: str) -> str:
        """Normalize category name to handle case and spacing issues."""
        # Convert to lowercase for case-insensitive comparison
        normalized = category.lower()

        # Fix spacing issues (e.g., "Я- мужчина" vs "Я - мужчина")
        normalized = re.sub(r"\s*-\s*", "-", normalized)

        # Return the normalized key for comparison, but we'll use title case for display
        return normalized

    def _format_category_display(self, category: str) -> str:
        """Format category name for display in markdown."""
        # Fix spacing issues first
        category = re.sub(r"\s*-\s*", " - ", category)

        # Split into words
        words = category.split()
        formatted_words = []

        for word in words:
            # Check if the word is an abbreviation (all uppercase with length > 1)
            if word.isupper() and len(word) > 1:
                # Keep abbreviations as they are
                formatted_words.append(word)
            else:
                # Apply title case to regular words
                formatted_words.append(word.capitalize())

        # Join words back together
        return " ".join(formatted_words)

    def _build_category_tree(self) -> Dict[str, Any]:
        """Build a hierarchical category tree from highlights."""
        category_tree = {}
        normalized_to_display = {}  # Maps normalized keys to display names

        # First pass: collect all category names and their normalized versions
        for highlight in self.highlights:
            for category_hierarchy in highlight.categories:
                for cat in category_hierarchy:
                    normalized = self._normalize_category(cat)
                    # Keep the first occurrence of a category as the display name
                    if normalized not in normalized_to_display:
                        normalized_to_display[normalized] = self._format_category_display(cat)

        # Second pass: build the tree using normalized keys
        for highlight in self.highlights:
            for category_hierarchy in highlight.categories:
                normalized_hierarchy = [self._normalize_category(cat) for cat in category_hierarchy]

                # Build the tree structure
                current_level = category_tree
                for normalized_cat in normalized_hierarchy:
                    if normalized_cat not in current_level:
                        display_name = normalized_to_display[normalized_cat]
                        current_level[normalized_cat] = {
                            "display_name": display_name,
                            "notes": [],
                            "subcategories": {},
                        }
                    current_level = current_level[normalized_cat]["subcategories"]

                # Add the note to the deepest category
                parent_level = category_tree
                for i, normalized_cat in enumerate(normalized_hierarchy):
                    if i == len(normalized_hierarchy) - 1:
                        parent_level[normalized_cat]["notes"].append(
                            {
                                "highlight_text": highlight.highlight_text,
                                "note_text": highlight.note_text,
                            }
                        )
                    else:
                        parent_level = parent_level[normalized_cat]["subcategories"]

        return category_tree

    def _write_category_to_markdown(self, category_tree: Dict, file, level: int = 1) -> None:
        """Recursively write categories and notes to markdown file."""
        for normalized_cat, content in category_tree.items():
            display_name = content["display_name"]
            file.write(f"{'#' * level} {display_name}\n\n")

            # Write notes for this category
            for note in content["notes"]:
                file.write(f"* {note['highlight_text']}\n")
                if note["note_text"]:
                    file.write(f"\n  **Note**: *{note['note_text']}*\n\n")
                else:
                    file.write("\n")  # Add a newline after each highlight without a note

            # Add an extra newline after all notes in a category
            if content["notes"]:
                file.write("\n")

            # Write subcategories
            self._write_category_to_markdown(content["subcategories"], file, level + 1)


class BulletExporter:
    """Exporter for Kindle clippings to bullet point format."""

    def __init__(self, highlights: List[ProcessedHighlight], output_path: Path):
        """Initialize the exporter with highlights and output path."""
        self.highlights = highlights
        self.output_path = output_path

    def export(self) -> None:
        """Export highlights to a bullet point format file."""
        formatted_lines = []
        current_book_title = ""

        for highlight in self.highlights:
            if highlight.book_name != current_book_title:
                formatted_lines.append(f"=========== {highlight.book_name} ===========\n")
                current_book_title = highlight.book_name

            formatted_lines.append(f"* {highlight.highlight_text}")
            if highlight.note_text:
                formatted_lines.append(f"  - Note: {highlight.note_text}\n")
            else:
                formatted_lines.append("")

        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(formatted_lines))


class DefaultExporter:
    """Exporter for Kindle clippings to default Kindle format."""

    DELIMITER = "==========\n"

    def __init__(self, raw_clippings: List[str], output_path: Path):
        """Initialize the exporter with raw clippings and output path."""
        self.raw_clippings = raw_clippings
        self.output_path = output_path

    def export(self) -> None:
        """Export clippings to the default Kindle format."""
        with open(self.output_path, "w", encoding="utf-8") as f:
            for clipping in self.raw_clippings:
                formatted_clipping = f"{clipping}"
                if not clipping.strip().endswith(self.DELIMITER.strip()):
                    formatted_clipping += self.DELIMITER
                f.write(formatted_clipping)
