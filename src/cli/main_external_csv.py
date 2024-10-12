import re
from pathlib import Path

import pandas as pd


class ClippingProcessor:
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
        self.df = self.read_csv(file_path)

    @staticmethod
    def read_csv(file_path: Path) -> pd.DataFrame:
        return pd.read_csv(file_path)

    @staticmethod
    def parse_location(location: str) -> tuple[int, int]:
        return (
            tuple(map(int, location.split("-")))
            if "-" in location
            else (int(location), int(location))
        )

    @staticmethod
    def overlaps(loc1: tuple[int, int], loc2: tuple[int, int]) -> bool:
        # Handles exact overlap and range overlap
        return not (loc1[1] <= loc2[0] or loc2[1] <= loc1[0])

    def clean_date(self, df: pd.DataFrame) -> pd.DataFrame:
        df["date"] = pd.to_datetime(
            df["date"].str.split(" GMT").str[0], format="%a %b %d %Y %H:%M:%S"
        )
        return df

    def remove_duplicates(self) -> pd.DataFrame:
        """
        Removes duplicate clippings based on overlapping locations, keeping the most recent one.
        """
        self.df["location_start"], self.df["location_end"] = zip(
            *self.df["location"].apply(self.parse_location)
        )
        self.df = self.clean_date(self.df)
        latest_rows = {}

        for idx, row in self.df.iterrows():
            current_location = (row["location_start"], row["location_end"])
            if any(self.overlaps(current_location, loc) for loc in latest_rows):
                overlap_loc = next(
                    loc for loc in latest_rows if self.overlaps(current_location, loc)
                )
                if row["date"] > latest_rows[overlap_loc]["date"]:
                    del latest_rows[overlap_loc]
                    latest_rows[current_location] = row
            else:
                latest_rows[current_location] = row

        return pd.DataFrame(latest_rows.values()).drop(columns=["location_start", "location_end"])

    def categorize_notes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extracts categories and cleans the note text."""
        df["categories"] = df["note_text"].apply(self.extract_categories)
        df["note_text"] = df["note_text"].apply(self.strip_categories_from_note)
        return df

    def extract_categories(self, note: str) -> list[list[str]]:
        """Extracts categories from notes, handling both predefined and custom categories."""
        matches = re.findall(r"\(([^)]+)\)", note) if isinstance(note, str) else []
        return [
            [self.GROUP_MAPPING.get(sub.strip(), sub.strip()) for sub in code.split(">")]
            for group_codes in matches
            for code in group_codes.split(",")
        ] or [["No Category"]]

    @staticmethod
    def strip_categories_from_note(note: str) -> str:
        """Cleans category markers from note text."""
        return re.sub(r"\([^)]+\)\s*", "", note) if isinstance(note, str) else note


class MarkdownExporter:
    def __init__(self, df: pd.DataFrame, output_file: Path):
        self.df = df
        self.output_file = output_file

    def export(self):
        category_dict = self.build_category_tree()
        with self.output_file.open("w", encoding="utf-8") as f:
            self.write_categories(category_dict, f)

    def build_category_tree(self) -> dict:
        """Builds a nested dictionary structure for categories and notes."""
        category_tree = {}

        def add_to_tree(categories, highlight, note):
            current_level = category_tree
            for cat in categories:
                current_level = current_level.setdefault(cat, {"notes": []})
            current_level["notes"].append({"highlight_text": highlight, "note_text": note})

        for _, row in self.df.iterrows():
            for category_hierarchy in row["categories"]:
                add_to_tree(category_hierarchy, row["highlight_text"], row["note_text"])

        return category_tree

    def write_categories(self, category_tree: dict, f, level=1):
        """Recursively writes markdown based on the category tree."""
        for category, content in category_tree.items():
            if category != "notes":
                f.write(f"{'#' * level} {category}\n")
                for note in content.get("notes", []):
                    f.write(f'* {note["highlight_text"]}\n')
                    if note["note_text"]:
                        f.write(f'\n  **Note**: *{note["note_text"]}*\n')
                self.write_categories(content, f, level + 1)


def main():
    # Usage:
    # 1. Go to https://www.mykindletools.com/kindle-clipping-export and export CSV file
    # 2. Move downloaded files to `data/` directory, replace the path below and execute
    #    with active poetry venv: `python src/cli/main_external_csv.py`

    file_path = Path("data/happiness_clippings.csv")
    output_file = Path("data/exported_notes.md")

    processor = ClippingProcessor(file_path)
    deduped_df = processor.remove_duplicates()
    categorized_df = processor.categorize_notes(deduped_df)

    exporter = MarkdownExporter(categorized_df, output_file)
    exporter.export()


if __name__ == "__main__":
    main()
