from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple


@dataclass
class KindleClipping:
    """Represents a single clipping from a Kindle device."""

    book_title: str
    content: str
    location: Tuple[int, int]
    location_text: str
    added_date: Optional[datetime] = None
    is_highlight: bool = False
    is_note: bool = False
    page: Optional[str] = None

    def __post_init__(self):
        """Validate the clipping after initialization."""
        if not self.is_highlight and not self.is_note:
            raise ValueError("Clipping must be either a highlight or a note")


@dataclass
class ProcessedHighlight:
    """Represents a processed highlight with optional note and categories."""

    book_name: str
    location: Tuple[int, int]
    location_text: str
    highlight_text: str
    note_text: str = ""
    categories: List[List[str]] = field(default_factory=lambda: [["No Category"]])
