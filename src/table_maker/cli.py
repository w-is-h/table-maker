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
    # Table style argument group
    style_group = parser.add_mutually_exclusive_group()
    style_group.add_argument(
        "--style",
        choices=["uniform", "random", "mixed"],
        default="mixed",
        help="Table style: 'uniform' (regular cells, solid lines), 'random' (varied cells, mixed lines), or 'mixed' (random mix of both) (default: mixed)",
    )
    parser.add_argument(
        "--margin",
        type=int,
        default=10,
        help="Margin size in pixels around each table (default: 10)",
    )
    # Data sparsity options
    sparsity_group = parser.add_argument_group('data sparsity options')
    sparsity_group.add_argument(
        "--sparsity",
        type=float,
        default=0.2,
        help="Overall cell emptiness (0.0=dense, 1.0=sparse) (default: 0.2)",
    )
    sparsity_group.add_argument(
        "--allow-empty-rows",
        action="store_true",
        help="Allow completely empty rows (default: False)",
    )
    sparsity_group.add_argument(
        "--allow-empty-columns",
        action="store_true",
        help="Allow completely empty columns (default: False)",
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
    # Header options
    header_group = parser.add_argument_group('header options')
    header_group.add_argument(
        "--headers",
        choices=["none", "column", "row", "both"],
        default="none",
        help="Include headers: 'none', 'column', 'row', or 'both' (default: none)",
    )

    return parser.parse_args()


def main() -> None:
    """Generate table image and JSON data based on command-line arguments."""
    args = parse_args()

    output_dir = Path(args.output) if args.output else None

    # Convert style argument to is_normal parameter
    is_normal: Optional[bool] = None  # Default for mixed
    if args.style == "uniform":
        is_normal = True
    elif args.style == "random":
        is_normal = False
    # else mixed: is_normal remains None, will use normal_probability

    # Set header probabilities based on headers argument
    column_header_probability = 0.0
    row_header_probability = 0.0
    if args.headers == "column":
        column_header_probability = 1.0
    elif args.headers == "row":
        row_header_probability = 1.0
    elif args.headers == "both":
        column_header_probability = 1.0
        row_header_probability = 1.0

    # Set empty probabilities
    # Use sparsity for empty_cell_probability
    empty_cell_probability = args.sparsity
    # Only use row/column emptiness if allowed and in random style
    empty_row_probability = 0.3 if args.allow_empty_rows and args.style != "uniform" else 0.0
    empty_column_probability = 0.3 if args.allow_empty_columns and args.style != "uniform" else 0.0

    # Normal probability is only used for mixed style
    normal_probability = 0.5 if args.style == "mixed" else 1.0

    results = generate_tables(
        count=args.count,
        min_rows=args.min_rows,
        min_columns=args.min_columns,
        max_rows=args.max_rows,
        max_columns=args.max_columns,
        output_dir=output_dir,
        is_normal=is_normal,
        normal_probability=normal_probability,
        margin=args.margin,
        empty_row_probability=empty_row_probability,
        empty_column_probability=empty_column_probability,
        empty_cell_probability=empty_cell_probability,
        large_number_probability=args.large_number_probability,
        column_header_probability=column_header_probability,
        row_header_probability=row_header_probability,
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
