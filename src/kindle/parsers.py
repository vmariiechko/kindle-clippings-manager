import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from src.kindle.models import KindleClipping


class KindleClippingsParser:
    """Parser for Kindle clippings file."""

    HIGHLIGHT_IDENTIFIER = "Your Highlight"
    NOTE_IDENTIFIER = "Your Note"
    BOOKMARK_IDENTIFIER = "Your Bookmark"
    LOCATION_IDENTIFIER = "Location"
    PAGE_IDENTIFIER = "page"
    DELIMITER = "==========\n"
    DATE_PATTERN = r"Added on (.*?)$"

    def __init__(self, file_path: Path):
        """Initialize the parser with a file path."""
        self.file_path = file_path

    def read_clippings(self) -> List[str]:
        """Read and parse raw clippings from the file."""
        with open(self.file_path, "r", encoding="utf-8") as file:
            content = file.read().split(self.DELIMITER)
            return [entry for entry in content if entry.strip()]

    def parse_clippings(self, raw_clippings: List[str] = None) -> List[KindleClipping]:
        """Parse raw clippings into structured KindleClipping objects."""
        if raw_clippings is None:
            raw_clippings = self.read_clippings()

        parsed_clippings = []

        for raw_clipping in raw_clippings:
            if not raw_clipping.strip():
                continue

            lines = raw_clipping.split("\n")
            if len(lines) < 3:
                continue  # Skip malformed clippings

            book_title = lines[0].strip()
            metadata_line = lines[1].strip()
            content = "\n".join(lines[3:]).strip()

            # Extract location
            location_text = ""
            if self.LOCATION_IDENTIFIER in metadata_line:
                location_parts = metadata_line.split(self.LOCATION_IDENTIFIER)
                if len(location_parts) > 1:
                    location_text = location_parts[1].split("|")[0].strip()

            # Extract page
            page = None
            if self.PAGE_IDENTIFIER in metadata_line:
                page_match = re.search(rf"{self.PAGE_IDENTIFIER} (\d+)", metadata_line)
                if page_match:
                    page = page_match.group(1)

            # Extract date
            added_date = None
            date_match = re.search(self.DATE_PATTERN, metadata_line)
            if date_match:
                date_str = date_match.group(1)
                try:
                    # Format: Monday, February 3, 2025 8:09:12 AM
                    added_date = datetime.strptime(date_str, "%A, %B %d, %Y %I:%M:%S %p")
                except ValueError:
                    pass  # Ignore date parsing errors

            # Determine clipping type
            is_highlight = self.HIGHLIGHT_IDENTIFIER in metadata_line
            is_note = self.NOTE_IDENTIFIER in metadata_line

            # Skip bookmarks and other types we don't care about
            if not (is_highlight or is_note):
                continue

            # Parse location
            location = self.parse_location(location_text)

            clipping = KindleClipping(
                book_title=book_title,
                content=content,
                location=location,
                location_text=location_text,
                added_date=added_date,
                is_highlight=is_highlight,
                is_note=is_note,
                page=page,
            )

            parsed_clippings.append(clipping)

        return parsed_clippings

    @staticmethod
    def parse_location(location: str) -> Tuple[int, int]:
        """Parse location string into a tuple of start and end positions."""
        if not location:
            return (0, 0)

        if "-" in location:
            start, end = map(int, location.split("-"))
        else:
            start = end = int(location)
        return (start, end)

    def filter_by_book(
        self, clippings: List[KindleClipping], book_title: str
    ) -> List[KindleClipping]:
        """Filter clippings for a specific book using exact title match."""
        return [clip for clip in clippings if clip.book_title == book_title]

    def list_books(self, clippings: List[KindleClipping]) -> List[str]:
        """List all unique book titles from the clippings."""
        titles = {clip.book_title for clip in clippings}
        return sorted(titles)
