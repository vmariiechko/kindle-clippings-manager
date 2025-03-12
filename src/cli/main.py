import argparse
import re
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class KindleClippingsProcessor:
    HIGHLIGHT_IDENTIFIER = "Your Highlight"
    NOTE_IDENTIFIER = "Your Note"
    LOCATION_IDENTIFIER = "Location"
    DELIMITER = "==========\n"

    # Category mapping for shortcuts
    GROUP_MAPPING = {
        "Б": "Білки",
        "Ж": "Жири",
        "В": "Вуглеводи",
        "К": "Клітчатка",
        "М": "Мікроелементи та вітаміни",
        "А": "водА",
        "P": "Protein",
        "F": "Fat",
        "C": "Carbohydrates",
        "N": "Notes and Thoughts",
        "FIB": "Fiber",
        "MIC": "Micronutrients and Vitamins",
        "W": "Water",
    }

    def __init__(self, file_path: Path):
        """Initialize the processor with a file path."""
        self.file_path = file_path
        self.book_highlights: Dict[str, Set[Tuple[int, int]]] = {}
        # Store processed clippings with additional metadata
        self.processed_clippings = []

    def read_clippings(self) -> List[str]:
        """Read and parse clippings from the file."""

        with open(self.file_path, "r", encoding="utf-8") as file:
            content = file.read().split(self.DELIMITER)
            return [entry for entry in content if entry.strip()]

    def extract_book_title_and_range(self, clipping: str) -> Tuple[str, Tuple[int, int]]:
        """Extract the book title and highlight range from a clipping."""

        lines = clipping.split("\n")
        book_title = lines[0]
        location_line = next(line for line in lines if self.LOCATION_IDENTIFIER in line)
        location = location_line.split(self.LOCATION_IDENTIFIER)[1].split("|")[0].strip()

        if "-" in location:
            start, end = map(int, location.split("-"))
        else:
            start = end = int(location)

        return book_title, (start, end)

    def is_overlap(self, first_range: Tuple[int, int], second_range: Tuple[int, int]) -> bool:
        """
        Determines whether two ranges overlap. This includes cases of exact overlap, partial
        overlap, and full encapsulation, but excludes adjacent ranges where one ends exactly
        where the other begins.
        """

        first_start, first_end = first_range
        second_start, second_end = second_range

        if first_start == second_start and first_end == second_end:  # Check for exact overlap
            return True

        return (first_start < second_start < first_end or first_start < second_end < first_end) or (
            second_start < first_start < second_end or second_start < first_end < second_end
        )

    def remove_duplicates(self, clippings: List[str]) -> List[str]:
        """Remove duplicate highlights from the list of clippings."""

        unique_clippings = []

        for clipping in reversed(clippings):
            if self.HIGHLIGHT_IDENTIFIER not in clipping:
                unique_clippings.append(clipping)
                continue

            book_title, highlight_range = self.extract_book_title_and_range(clipping.strip())
            if book_title not in self.book_highlights:
                self.book_highlights[book_title] = set()

            if any(
                self.is_overlap(highlight_range, existing_range)
                for existing_range in self.book_highlights[book_title]
            ):
                continue

            self.book_highlights[book_title].add(highlight_range)
            unique_clippings.append(clipping)

        return list(reversed(unique_clippings))

    def save_cleaned_clippings(self, output_path: Path, formatted_clippings: List[str]) -> None:
        """Save the formatted clippings to a file."""

        with open(output_path, "w", encoding="utf-8") as file:
            for clipping in formatted_clippings:
                file.write(clipping)
                if not clipping.strip().endswith(self.DELIMITER.strip()):
                    file.write("\n")

    def filter_clippings_by_book(self, clippings: List[str], book_title: str) -> List[str]:
        """Filter clippings for a specific book using exact title match."""
        filtered_clippings = []
        for clipping in clippings:
            lines = clipping.split("\n")
            if lines and lines[0] == book_title:
                filtered_clippings.append(clipping)
        return filtered_clippings

    def list_books(self, clippings: List[str]) -> List[str]:
        """List all unique book titles from the clippings."""

        titles = set()
        for clipping in clippings:
            if self.HIGHLIGHT_IDENTIFIER in clipping:
                book_title = clipping.split("\n")[0]
                titles.add(book_title)
        return sorted(titles)

    def apply_formatting(self, clippings: List[str], format_style: str) -> List[str]:
        """Apply specified formatting style to the clippings."""

        if format_style == "bullet":
            return self._format_with_bullets(clippings)
        return self._format_default(clippings)

    def _format_default(self, clippings: List[str]) -> List[str]:
        """Format clippings in the default Kindle format."""

        formatted_clippings = []
        for clipping in clippings:
            formatted_clipping = f"{clipping}"
            if not clipping.strip().endswith(self.DELIMITER.strip()):
                formatted_clipping += self.DELIMITER
            formatted_clippings.append(formatted_clipping)
        return formatted_clippings

    def _format_with_bullets(self, clippings: List[str]) -> List[str]:
        """Format clippings with bullet points, excluding metadata."""

        formatted_clippings = []
        current_book_title = ""

        for clipping in clippings:
            if self.HIGHLIGHT_IDENTIFIER in clipping:
                lines = clipping.split("\n")
                book_title = lines[0]
                highlight_text = "".join(lines[3:])

                if book_title != current_book_title:
                    formatted_clippings.append(f"=========== {book_title} ===========\n")
                    current_book_title = book_title

                formatted_clippings.append("* " + highlight_text)
            else:
                # Ignore non-highlight clippings
                pass

        return formatted_clippings

    def extract_categories(self, note: str) -> List[List[str]]:
        """Extracts categories from notes, handling both predefined and custom categories."""
        if not isinstance(note, str):
            return [["No Category"]]

        matches = re.findall(r"\(([^)]+)\)", note)
        if not matches:
            return [["No Category"]]

        categories = []
        for group_codes in matches:
            for code in group_codes.split(","):
                hierarchy = []
                for sub in code.split(">"):
                    category = self.GROUP_MAPPING.get(sub.strip(), sub.strip())
                    hierarchy.append(category)
                categories.append(hierarchy)

        return categories

    def strip_categories_from_note(self, note: str) -> str:
        """Cleans category markers from note text."""
        if not isinstance(note, str):
            return ""
        return re.sub(r"\([^)]+\)\s*", "", note)

    def process_clippings(self, selected_book: str = None) -> List[Dict[str, Any]]:
        """Process clippings and extract all necessary information."""
        clippings = self.read_clippings()

        # Filter by selected book if specified
        if selected_book:
            # Make sure we're filtering correctly by exact book title
            clippings = [clip for clip in clippings if selected_book == clip.split("\n")[0]]

        cleaned_clippings = self.remove_duplicates(clippings)

        # First pass: collect all highlights and notes
        highlights = []
        notes = []

        for clipping in cleaned_clippings:
            lines = clipping.split("\n")
            book_title = lines[0]
            metadata_line = lines[1]
            content = "\n".join(lines[3:]).strip()

            # Extract location
            location_text = metadata_line.split(self.LOCATION_IDENTIFIER)[1].split("|")[0].strip()
            location = self.parse_location(location_text)

            if self.HIGHLIGHT_IDENTIFIER in metadata_line:
                highlights.append(
                    {
                        "book_name": book_title,
                        "location": location,
                        "location_text": location_text,
                        "highlight_text": content,
                        "note_text": "",
                        "categories": [["No Category"]],
                    }
                )
            elif self.NOTE_IDENTIFIER in metadata_line:
                notes.append(
                    {
                        "book_name": book_title,
                        "location": location,
                        "location_text": location_text,
                        "note_text": content,
                    }
                )

        # Second pass: match notes to highlights
        for note in notes:
            note_loc = note["location"]
            matched = False

            # Find the best matching highlight for this note
            for highlight in highlights:
                highlight_start, highlight_end = highlight["location"]

                # Case 1: Note is at the end of highlight or one position before
                if note_loc[0] == highlight_end or note_loc[0] == highlight_end - 1:
                    highlight["note_text"] = note["note_text"]
                    highlight["categories"] = self.extract_categories(note["note_text"])
                    highlight["note_text"] = self.strip_categories_from_note(note["note_text"])
                    matched = True
                    break

                # Case 2: Note is within the highlight range
                elif highlight_start <= note_loc[0] <= highlight_end:
                    highlight["note_text"] = note["note_text"]
                    highlight["categories"] = self.extract_categories(note["note_text"])
                    highlight["note_text"] = self.strip_categories_from_note(note["note_text"])
                    matched = True
                    break

                # Case 3: Single-point highlight matches note location
                elif highlight_start == highlight_end and note_loc[0] == highlight_start:
                    highlight["note_text"] = note["note_text"]
                    highlight["categories"] = self.extract_categories(note["note_text"])
                    highlight["note_text"] = self.strip_categories_from_note(note["note_text"])
                    matched = True
                    break

            # If no matching highlight found, create a "virtual" highlight for this note
            if not matched:
                highlights.append(
                    {
                        "book_name": note["book_name"],
                        "location": note["location"],
                        "location_text": note["location_text"],
                        "highlight_text": "[No highlight text]",
                        "note_text": self.strip_categories_from_note(note["note_text"]),
                        "categories": self.extract_categories(note["note_text"]),
                    }
                )

        self.processed_clippings = highlights
        return highlights

    @staticmethod
    def parse_location(location: str) -> Tuple[int, int]:
        """Parse location string into a tuple of start and end positions."""
        if "-" in location:
            start, end = map(int, location.split("-"))
        else:
            start = end = int(location)
        return (start, end)

    def export_to_markdown(self, output_path: Path) -> None:
        """Export processed clippings to a markdown file with hierarchical categories."""
        if not self.processed_clippings:
            self.process_clippings()

        # Build category tree
        category_tree = {}

        for clipping in self.processed_clippings:
            for category_hierarchy in clipping["categories"]:
                current_level = category_tree
                for cat in category_hierarchy:
                    if cat not in current_level:
                        current_level[cat] = {"notes": [], "subcategories": {}}
                    current_level = current_level[cat]["subcategories"]

                # Add the note to the deepest category
                parent_level = category_tree
                for i, cat in enumerate(category_hierarchy):
                    if i == len(category_hierarchy) - 1:
                        parent_level[cat]["notes"].append(
                            {
                                "highlight_text": clipping["highlight_text"],
                                "note_text": clipping["note_text"],
                            }
                        )
                    else:
                        parent_level = parent_level[cat]["subcategories"]

        # Write to markdown file
        with open(output_path, "w", encoding="utf-8") as f:
            self._write_category_to_markdown(category_tree, f)

    def _write_category_to_markdown(self, category_tree: Dict, file, level: int = 1) -> None:
        """Recursively write categories and notes to markdown file."""
        for category, content in category_tree.items():
            file.write(f"{'#' * level} {category}\n\n")

            # Write notes for this category
            for note in content["notes"]:
                file.write(f"* {note['highlight_text']}\n")
                if note["note_text"]:
                    file.write(f"\n  **Note**: *{note['note_text']}*\n\n")

            # Write subcategories
            self._write_category_to_markdown(content["subcategories"], file, level + 1)


def main():
    """Run the main function to process Kindle clippings."""

    default_input_file = "My Clippings.txt"
    default_output_file = "Cleaned Clippings.txt"
    default_markdown_file = "Categorized Notes.md"

    parser = argparse.ArgumentParser(description="Clean up Kindle clippings.")
    parser.add_argument(
        "-i",
        "--input_file",
        type=str,
        default=default_input_file,
        help=f"Path to the input 'My Clippings.txt' file (default: {default_input_file}).",
    )
    parser.add_argument(
        "-o",
        "--output_file",
        type=str,
        default=default_output_file,
        help=f"Path to the output cleaned clippings file (default: {default_output_file}).",
    )
    parser.add_argument(
        "-m",
        "--markdown_file",
        type=str,
        default=default_markdown_file,
        help=f"Path to the output markdown file (default: {default_markdown_file}).",
    )
    parser.add_argument(
        "-f",
        "--format_style",
        type=str,
        choices=["bullet", "default", "markdown"],
        default="default",
        help=(
            "Formatting style for the clippings ('bullet' for bullet points, 'default' for standard"
            " format, 'markdown' for categorized markdown)."
        ),
    )

    args = parser.parse_args()

    try:
        input_path = Path(args.input_file).resolve(strict=True)
        output_path = Path(args.output_file).resolve()
        markdown_path = Path(args.markdown_file).resolve()

        processor = KindleClippingsProcessor(input_path)
        clippings = processor.read_clippings()

        # Interactive book selection
        selected_book = None
        book_titles = processor.list_books(clippings)
        if book_titles:
            print("Available books:")
            for i, title in enumerate(book_titles, 1):
                print(f"{i}. {title}")
            selection = input(
                "Enter the number of the book to filter by (or press Enter to process all): "
            )
            if selection.isdigit() and 0 < int(selection) <= len(book_titles):
                selected_book = book_titles[int(selection) - 1]
                print(f"Selected book for processing: {selected_book}")
            else:
                print("Processing all clippings.")
        else:
            print("No book titles found in clippings.")

        if args.format_style == "markdown":
            # Process and export to markdown with categories
            processor.process_clippings(selected_book)
            processor.export_to_markdown(markdown_path)
            print(f"Categorized markdown exported to: {markdown_path}")
        else:
            # For other formats, use the existing flow
            if selected_book:
                clippings = processor.filter_clippings_by_book(clippings, selected_book)
            cleaned_clippings = processor.remove_duplicates(clippings)
            formatted_clippings = processor.apply_formatting(cleaned_clippings, args.format_style)
            processor.save_cleaned_clippings(output_path, formatted_clippings)
            print(f"Cleaned clippings saved to: {output_path}")

    except FileNotFoundError:
        print(f"Error: The file '{args.input_file}' does not exist. Please check the file path.")
    except Exception:
        print(
            f"An unexpected error occurred:\n{traceback.format_exc()}\nPlease check the inputs and"
            " try again."
        )


if __name__ == "__main__":
    main()
