import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple


class KindleClippingsProcessor:
    HIGHLIGHT_IDENTIFIER = "Your Highlight"
    LOCATION_IDENTIFIER = "Location"
    DELIMITER = "==========\n"

    def __init__(self, file_path: Path):
        """Initialize the processor with a file path."""

        self.file_path = file_path
        self.book_highlights: Dict[str, Set[Tuple[int, int]]] = {}

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

    def save_cleaned_clippings(self, output_path: Path, cleaned_clippings: List[str]) -> None:
        """Save the cleaned clippings to a file."""

        with open(output_path, "w", encoding="utf-8") as file:
            for clipping in cleaned_clippings:
                file.write(clipping + self.DELIMITER)

    def filter_clippings_by_book(self, clippings: List[str], book_title: str) -> List[str]:
        """Filter clippings for a specific book."""

        filtered_clippings = [clipping for clipping in clippings if book_title in clipping]
        return filtered_clippings

    def list_books(self, clippings: List[str]) -> List[str]:
        """List all unique book titles from the clippings."""

        titles = set()
        for clipping in clippings:
            if self.HIGHLIGHT_IDENTIFIER in clipping:
                book_title = clipping.split("\n")[0]
                titles.add(book_title)
        return sorted(titles)


def main():
    """Run the main function to process Kindle clippings."""

    parser = argparse.ArgumentParser(description="Clean up Kindle clippings.")
    parser.add_argument("input_file", type=str, help="Path to the input 'My Clippings.txt' file.")
    parser.add_argument(
        "-o",
        "--output_file",
        type=str,
        default="Cleaned Clippings.txt",
        help=(
            "Path to the output cleaned clippings file. Defaults to 'Cleaned Clippings.txt' in the"
            " current directory."
        ),
    )

    args = parser.parse_args()

    try:
        input_path = Path(args.input_file).resolve(strict=True)
        output_path = Path(args.output_file).resolve()

        processor = KindleClippingsProcessor(input_path)
        clippings = processor.read_clippings()
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
                clippings = processor.filter_clippings_by_book(clippings, selected_book)
                print(f"Selected book for processing: {selected_book}")
            else:
                print("Processing all clippings.")
        else:
            print("No book titles found in clippings.")

        cleaned_clippings = processor.remove_duplicates(clippings)
        processor.save_cleaned_clippings(output_path, cleaned_clippings)

        print(f"Cleaned clippings saved to: {output_path}")

    except FileNotFoundError:
        print(f"Error: The file {args.input_file} does not exist.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
