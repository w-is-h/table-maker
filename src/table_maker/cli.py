#!/usr/bin/env python3
import argparse
from pathlib import Path
from typing import Optional

from table_maker.maker import generate_tables


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for table generation."""
    parser = argparse.ArgumentParser(
        description="Generate random tables as PNG images and JSON data"
    )

    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=1,
        help="Number of tables to generate (default: 1)",
    )
    parser.add_argument(
        "--min-rows",
        "-r",
        type=int,
        default=1,
        help="Minimum number of rows for each table (default: 1)",
    )
    parser.add_argument(
        "--min-columns",
        "-m",
        type=int,
        default=1,
        help="Minimum number of columns for each table (default: 1)",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=15,
        help="Maximum number of rows for each table (default: 15)",
    )
    parser.add_argument(
        "--max-columns",
        type=int,
        default=40,
        help="Maximum number of columns for each table (default: 40)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output directory (default: current directory)",
    )
    parser.add_argument(
        "--normal",
        action="store_true",
        help="Generate normal tables with uniform cells and solid lines",
    )
    parser.add_argument(
        "--random",
        action="store_true",
        help="Generate random tables with varied cells and mixed line styles",
    )
    parser.add_argument(
        "--normal-probability",
        type=float,
        default=0.5,
        help="Probability of generating normal tables when neither --normal nor --random is specified (default: 0.5)",
    )
    parser.add_argument(
        "--margin",
        type=int,
        default=10,
        help="Margin size in pixels around each table (default: 10)",
    )
    parser.add_argument(
        "--empty-row-probability",
        type=float,
        default=0.3,
        help="Probability of creating an empty row (default: 0.3)",
    )
    parser.add_argument(
        "--empty-column-probability",
        type=float,
        default=0.3,
        help="Probability of creating an empty column (default: 0.3)",
    )
    parser.add_argument(
        "--empty-cell-probability",
        type=float,
        default=0.2,
        help="Probability of any individual cell being empty (default: 0.2)",
    )
    parser.add_argument(
        "--wrap-mode",
        type=str,
        default="word",
        choices=["word", "char", "none"],
        help="Text wrapping mode: word (default), char (break words), none (no wrapping)",
    )
    parser.add_argument(
        "--large-number-probability",
        type=float,
        default=0.05,
        help="Probability of generating very large numbers (15-30 digits) (default: 0.05)",
    )
    parser.add_argument(
        "--column-header-probability",
        type=float,
        default=0.0,
        help="Probability of generating column headers (default: 0.0)",
    )
    parser.add_argument(
        "--row-header-probability",
        type=float,
        default=0.0,
        help="Probability of generating row headers (default: 0.0)",
    )

    return parser.parse_args()


def main() -> None:
    """Generate table image and JSON data based on command-line arguments."""
    args = parse_args()

    output_dir = Path(args.output) if args.output else None

    # Handle normal/random options
    is_normal: Optional[bool] = None  # Default: Use normal_probability
    if args.normal and args.random:
        print(
            "Warning: Both --normal and --random specified; using normal_probability for randomization"
        )
    elif args.normal:
        is_normal = True
    elif args.random:
        is_normal = False

    # Validate normal_probability is between 0 and 1
    if not 0 <= args.normal_probability <= 1:
        print(
            f"Warning: normal_probability ({args.normal_probability}) should be between 0 and 1; using 0.5"
        )
        args.normal_probability = 0.5

    results = generate_tables(
        count=args.count,
        min_rows=args.min_rows,
        min_columns=args.min_columns,
        max_rows=args.max_rows,
        max_columns=args.max_columns,
        output_dir=output_dir,
        is_normal=is_normal,
        normal_probability=args.normal_probability,
        margin=args.margin,
        empty_row_probability=args.empty_row_probability,
        empty_column_probability=args.empty_column_probability,
        empty_cell_probability=args.empty_cell_probability,
        large_number_probability=args.large_number_probability,
        column_header_probability=args.column_header_probability,
        row_header_probability=args.row_header_probability,
        wrap_mode=args.wrap_mode,
    )

    # Group results by directory for clearer output
    if results:
        images_dir = results[0][0].parent
        json_dir = results[0][1].parent

        print(f"Generated {len(results)} tables:")
        print(f"  Images saved in: {images_dir}")
        print(f"  JSON data saved in: {json_dir}")

        for i, (image_path, json_path) in enumerate(results):
            print(f"  Table {i + 1}: {image_path.name}")


if __name__ == "__main__":
    main()
