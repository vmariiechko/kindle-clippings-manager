import argparse

# Add the project root to the Python path
import os
import sys
import traceback
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.kindle.exporters import BulletExporter, DefaultExporter, MarkdownExporter

# Use absolute imports
from src.kindle.processor import KindleClippingsProcessor


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

        # Interactive book selection
        selected_book = None
        book_titles = processor.list_books()
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
            processed_highlights = processor.process_clippings(selected_book)
            exporter = MarkdownExporter(processed_highlights, markdown_path)
            exporter.export()
            print(f"Categorized markdown exported to: {markdown_path}")
        elif args.format_style == "bullet":
            # Process and export to bullet format
            processed_highlights = processor.process_clippings(selected_book)
            exporter = BulletExporter(processed_highlights, output_path)
            exporter.export()
            print(f"Bullet-formatted clippings saved to: {output_path}")
        else:
            # Default format - use raw clippings
            raw_clippings = processor.parser.read_clippings()
            if selected_book:
                raw_clippings = [clip for clip in raw_clippings if selected_book in clip]
            exporter = DefaultExporter(raw_clippings, output_path)
            exporter.export()
            print(f"Default-formatted clippings saved to: {output_path}")

    except FileNotFoundError:
        print(f"Error: The file '{args.input_file}' does not exist. Please check the file path.")
    except Exception:
        print(
            f"An unexpected error occurred:\n{traceback.format_exc()}\nPlease check the inputs and"
            " try again."
        )


if __name__ == "__main__":
    main()
