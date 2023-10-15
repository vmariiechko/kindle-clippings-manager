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


def remove_duplicates(clippings: List[str]) -> List[str]:
    book_highlights: Dict[str, List[str]] = {}
    processed_clippings: List[str] = []

    for clipping in clippings:
        # If it's not a highlight, append directly to the result and continue
        if "Your Highlight" not in clipping:
            processed_clippings.append(clipping)
            continue

        # Process the highlights
        book_title = clipping.split("\n")[0]
        start, end = extract_location(clipping)

        if book_title not in book_highlights:
            book_highlights[book_title] = []

        overlaps = []
        for existing in book_highlights[book_title]:
            existing_start, existing_end = extract_location(existing)
            if (
                existing_start <= start <= existing_end
                or existing_start <= end <= existing_end
                or start <= existing_start
                and end >= existing_end
            ):
                overlaps.append(existing)

        if not overlaps:
            book_highlights[book_title].append(clipping)
            processed_clippings.append(clipping)
        else:
            longest = max(overlaps, key=lambda o: extract_location(o)[1] - extract_location(o)[0])
            if end - start > extract_location(longest)[1] - extract_location(longest)[0]:
                book_highlights[book_title].remove(longest)
                processed_clippings.remove(longest)
                book_highlights[book_title].append(clipping)
                processed_clippings.append(clipping)

    return processed_clippings


def save_cleaned_clippings(file_name: str, cleaned_clippings: List[str]) -> None:
    with open(file_name, "w", encoding="utf-8") as f:
        for clipping in cleaned_clippings:
            f.write(clipping + "\n==========\n")


if __name__ == "__main__":
    clippings = read_clippings("")
    cleaned_clippings = remove_duplicates(clippings)
    save_cleaned_clippings("", cleaned_clippings)
