from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

from src.kindle.models import KindleClipping, ProcessedHighlight
from src.kindle.parsers import KindleClippingsParser
from src.utils.text_utils import CategoryExtractor


class KindleClippingsProcessor:
    """Processor for Kindle clippings."""

    def __init__(self, file_path: Path):
        """Initialize the processor with a file path."""
        self.file_path = file_path
        self.parser = KindleClippingsParser(file_path)
        self.book_highlights: Dict[str, Set[Tuple[int, int]]] = {}
        self.processed_clippings: List[ProcessedHighlight] = []

    def read_clippings(self) -> List[KindleClipping]:
        """Read and parse clippings from the file."""
        raw_clippings = self.parser.read_clippings()
        return self.parser.parse_clippings(raw_clippings)

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

    def remove_duplicates(self, clippings: List[KindleClipping]) -> List[KindleClipping]:
        """Remove duplicate highlights from the list of clippings."""
        self.book_highlights = {}  # Reset book highlights
        unique_clippings = []

        # Sort by date, newest first (if date is available)
        sorted_clippings = sorted(
            clippings, key=lambda c: c.added_date if c.added_date else datetime.min, reverse=True
        )

        for clipping in sorted_clippings:
            if not clipping.is_highlight:
                unique_clippings.append(clipping)
                continue

            book_title = clipping.book_title
            highlight_range = clipping.location

            if book_title not in self.book_highlights:
                self.book_highlights[book_title] = set()

            if any(
                self.is_overlap(highlight_range, existing_range)
                for existing_range in self.book_highlights[book_title]
            ):
                continue

            self.book_highlights[book_title].add(highlight_range)
            unique_clippings.append(clipping)

        # Sort back by location
        return sorted(unique_clippings, key=lambda c: c.location[0])

    def process_clippings(self, selected_book: str = None) -> List[ProcessedHighlight]:
        """Process clippings and extract all necessary information."""
        clippings = self.read_clippings()

        # Filter by selected book if specified
        if selected_book:
            clippings = self.parser.filter_by_book(clippings, selected_book)

        cleaned_clippings = self.remove_duplicates(clippings)

        # First pass: collect all highlights and notes
        highlights = []
        notes = []

        for clipping in cleaned_clippings:
            if clipping.is_highlight:
                highlights.append(
                    ProcessedHighlight(
                        book_name=clipping.book_title,
                        location=clipping.location,
                        location_text=clipping.location_text,
                        highlight_text=clipping.content,
                    )
                )
            elif clipping.is_note:
                notes.append(
                    {
                        "book_name": clipping.book_title,
                        "location": clipping.location,
                        "location_text": clipping.location_text,
                        "note_text": clipping.content,
                    }
                )

        # Second pass: match notes to highlights
        for note in notes:
            note_loc = note["location"]
            matched = False

            # Find the best matching highlight for this note
            for highlight in highlights:
                highlight_start, highlight_end = highlight.location

                # Case 1: Note is at the end of highlight or one position before
                if note_loc[0] == highlight_end or note_loc[0] == highlight_end - 1:
                    highlight.note_text = note["note_text"]
                    highlight.categories = CategoryExtractor.extract_categories(note["note_text"])
                    highlight.note_text = CategoryExtractor.strip_categories_from_note(
                        note["note_text"]
                    )
                    matched = True
                    break

                # Case 2: Note is within the highlight range
                elif highlight_start <= note_loc[0] <= highlight_end:
                    highlight.note_text = note["note_text"]
                    highlight.categories = CategoryExtractor.extract_categories(note["note_text"])
                    highlight.note_text = CategoryExtractor.strip_categories_from_note(
                        note["note_text"]
                    )
                    matched = True
                    break

                # Case 3: Single-point highlight matches note location
                elif highlight_start == highlight_end and note_loc[0] == highlight_start:
                    highlight.note_text = note["note_text"]
                    highlight.categories = CategoryExtractor.extract_categories(note["note_text"])
                    highlight.note_text = CategoryExtractor.strip_categories_from_note(
                        note["note_text"]
                    )
                    matched = True
                    break

            # If no matching highlight found, create a "virtual" highlight for this note
            if not matched:
                highlights.append(
                    ProcessedHighlight(
                        book_name=note["book_name"],
                        location=note["location"],
                        location_text=note["location_text"],
                        highlight_text="[No highlight text]",
                        note_text=CategoryExtractor.strip_categories_from_note(note["note_text"]),
                        categories=CategoryExtractor.extract_categories(note["note_text"]),
                    )
                )

        self.processed_clippings = highlights
        return highlights

    def list_books(self) -> List[str]:
        """List all unique book titles from the clippings."""
        clippings = self.read_clippings()
        return self.parser.list_books(clippings)
