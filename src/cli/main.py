import argparse
from pathlib import Path
from typing import Dict, List


def read_clippings(file_name: str) -> List[str]:
    with open(file_name, "r", encoding="utf-8") as f:
        content = f.read().split("==========\n")
        return [entry.strip() for entry in content if entry.strip() != ""]


def extract_location(clipping: str) -> (int, int):
    location_line = [line for line in clipping.split("\n") if "Location" in line][0]
    location = location_line.split("Location")[1].split("|")[0].strip()
    if "-" in location:
        start, end = map(int, location.split("-"))
    else:
        start = end = int(location)
    return start, end


def is_overlap(first_range: (int, int), second_range: (int, int)) -> bool:
    """
    Determines whether two ranges overlap. This includes cases of exact overlap, partial
    overlap, and full encapsulation, but excludes adjacent ranges where one ends exactly
    where the other begins.

    :param first_range: A tuple containing the start and end of the first range.
    :param second_range: A tuple containing the start and end of the second range.
    :return: True if the ranges overlap, False otherwise.
    """

    first_start, first_end = first_range
    second_start, second_end = second_range

    if first_start == second_start and first_end == second_end:  # Check for exact overlap
        return True

    return (first_start < second_start < first_end or first_start < second_end < first_end) or (
        second_start < first_start < second_end or second_start < first_end < second_end
    )


def remove_duplicates(clippings: List[str]) -> List[str]:
    book_highlights: Dict[str, set] = {}
    clippings_copy = clippings[:]

    # Iterate in reverse over the copy to keep the newest clippings
    for i in range(len(clippings_copy) - 1, -1, -1):
        clipping = clippings_copy[i]
        if "Your Highlight" in clipping:
            book_title = clipping.split("\n")[0]
            start, end = extract_location(clipping)

            if book_title not in book_highlights:
                book_highlights[book_title] = set()

            # Check for exact duplicates and overlap
            is_duplicate = False
            for existing in book_highlights[book_title]:
                existing_start, existing_end = extract_location(existing)
                if clipping == existing or is_overlap((start, end), (existing_start, existing_end)):
                    is_duplicate = True
                    break

            if is_duplicate:
                clippings_copy.pop(i)  # Remove the duplicate clipping from the copy

            else:
                book_highlights[book_title].add(clipping)

    return clippings_copy


def save_cleaned_clippings(file_name: str, cleaned_clippings: List[str]) -> None:
    with open(file_name, "w", encoding="utf-8") as f:
        for clipping in cleaned_clippings:
            f.write(clipping + "\n==========\n")


def main():
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

    input_path = Path(args.input_file).resolve()
    output_path = Path(args.output_file).resolve()

    if not input_path.exists():
        print(f"Error: The file {input_path} does not exist.")
        return

    clippings = read_clippings(input_path)
    cleaned_clippings = remove_duplicates(clippings)
    save_cleaned_clippings(output_path, cleaned_clippings)
    print(f"Cleaned clippings saved to: {output_path}")


if __name__ == "__main__":
    main()
