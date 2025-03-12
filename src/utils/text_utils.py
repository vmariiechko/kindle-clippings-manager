import re
from typing import List


class CategoryExtractor:
    """Utility class for extracting categories from text."""

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

    @classmethod
    def extract_categories(cls, note: str) -> List[List[str]]:
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
                    category = cls.GROUP_MAPPING.get(sub.strip(), sub.strip())
                    hierarchy.append(category)
                categories.append(hierarchy)

        return categories

    @staticmethod
    def strip_categories_from_note(note: str) -> str:
        """Cleans category markers from note text."""
        if not isinstance(note, str):
            return ""
        return re.sub(r"\([^)]+\)\s*", "", note)
