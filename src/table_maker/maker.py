from PIL import Image, ImageDraw, ImageFont
import random
from itertools import accumulate
from faker import Faker
import json
import argparse
import shutil
from pathlib import Path
from typing import List, Tuple, Optional, Union, Any


def generate_table_dimensions(
    margin: int, min_rows: int = 1, min_columns: int = 1
) -> Tuple[int, int, int, int]:
    """Generate random table dimensions within constraints, accounting for margins.
    
    Args:
        margin: Margin size in pixels
        min_rows: Minimum number of rows to generate
        min_columns: Minimum number of columns to generate
        
    Returns:
        Tuple of (rows, columns, total_width, total_height)
    """
    rows = random.randint(min_rows, max(min_rows, 15))
    columns = random.randint(min_columns, max(min_columns, 40))
    min_width = columns * 40
    min_height = rows * 30
    max_width = 2560 - 2 * margin
    max_height = 1600 - 2 * margin
    total_width = random.randint(max(500, min_width), max_width)
    total_height = random.randint(max(500, min_height), max_height)
    return rows, columns, total_width, total_height


def generate_cell_sizes(
    num_cells: int, total_size: int, min_size: int, uniform: bool = False
) -> List[int]:
    """Generate sizes for num_cells that sum to total_size, each at least min_size."""
    if uniform:
        base_size = total_size // num_cells
        remainder = total_size % num_cells
        sizes = [base_size + (1 if i < remainder else 0) for i in range(num_cells)]
    else:
        sizes = [min_size] * num_cells
        remaining = total_size - min_size * num_cells
        while remaining > 0:
            sizes[random.randint(0, num_cells - 1)] += 1
            remaining -= 1
    return sizes


def generate_line_styles(
    rows: int, columns: int, is_normal: bool
) -> Tuple[List[str], List[str]]:
    """Determine line styles for the table grid."""
    if is_normal:
        hor_styles = ["solid_black"] * (rows + 1)
        ver_styles = ["solid_black"] * (columns + 1)
    else:
        styles = ["solid_black", "dotted_black", "solid_gray", "removed"]
        weights = [0.7, 0.1, 0.1, 0.1]
        hor_styles = [
            random.choices(styles, weights=weights)[0] for _ in range(rows + 1)
        ]
        ver_styles = [
            random.choices(styles, weights=weights)[0] for _ in range(columns + 1)
        ]
    return hor_styles, ver_styles


def draw_dotted_line(
    draw: Any, x1: int, y1: int, x2: int, y2: int, fill: Union[str, tuple]
) -> None:
    """Draw a dotted line between two points."""
    if x1 == x2:  # Vertical
        for y in range(y1, y2, 10):
            draw.line([(x1, y), (x1, min(y + 1, y2))], fill=fill, width=1)
    elif y1 == y2:  # Horizontal
        for x in range(x1, x2, 10):
            draw.line([(x, y1), (min(x + 1, x2), y1)], fill=fill, width=1)


def draw_grid(
    draw: Any,
    column_widths: List[int],
    row_heights: List[int],
    line_styles: Tuple[List[str], List[str]],
    margin: int,
) -> None:
    """Draw the table grid with specified line styles, accounting for margins."""
    hor_styles, ver_styles = line_styles
    x_positions = [margin + x for x in [0] + list(accumulate(column_widths))]
    for i, x in enumerate(x_positions):
        style = ver_styles[i]
        if style == "solid_black":
            draw.line(
                [(x, margin), (x, margin + sum(row_heights))], fill="black", width=1
            )
        elif style == "dotted_black":
            draw_dotted_line(
                draw, x, margin, x, margin + sum(row_heights), fill="black"
            )
        elif style == "solid_gray":
            draw.line(
                [(x, margin), (x, margin + sum(row_heights))],
                fill=(192, 192, 192),
                width=1,
            )
    y_positions = [margin + y for y in [0] + list(accumulate(row_heights))]
    for i, y in enumerate(y_positions):
        style = hor_styles[i]
        if style == "solid_black":
            draw.line(
                [(margin, y), (margin + sum(column_widths), y)], fill="black", width=1
            )
        elif style == "dotted_black":
            draw_dotted_line(
                draw, margin, y, margin + sum(column_widths), y, fill="black"
            )
        elif style == "solid_gray":
            draw.line(
                [(margin, y), (margin + sum(column_widths), y)],
                fill=(192, 192, 192),
                width=1,
            )


def generate_cell_content(
    rows: int, 
    columns: int, 
    fake: Faker, 
    is_normal: bool,
    empty_row_probability: float = 0.3,
    empty_column_probability: float = 0.3,
    empty_cell_probability: float = 0.2
) -> List[List[Optional[str]]]:
    """Generate diverse cell content using Faker.
    
    Args:
        rows: Number of rows in the table
        columns: Number of columns in the table
        fake: Faker instance for generating content
        is_normal: If True, no empty rows/columns will be created
        empty_row_probability: Probability of creating an empty row (when not normal)
        empty_column_probability: Probability of creating an empty column (when not normal)
        empty_cell_probability: Probability of any individual cell being empty
    
    Returns:
        2D list of cell content, with None representing empty cells
    """
    content: List[List[Optional[str]]] = [
        [None for _ in range(columns)] for _ in range(rows)
    ]
    empty_row: Optional[int] = None
    empty_column: Optional[int] = None
    if not is_normal:
        if random.random() < empty_row_probability:
            empty_row = random.randint(0, rows - 1)
        if random.random() < empty_column_probability:
            empty_column = random.randint(0, columns - 1)
    for i in range(rows):
        for j in range(columns):
            if i == empty_row or j == empty_column:
                continue  # Leave as None
            elif random.random() < empty_cell_probability:
                continue  # Leave as None
            else:
                if random.random() < 0.6:
                    if random.random() < 0.5:
                        text = str(fake.random_int(min=0, max=999))
                    else:
                        text = f"{fake.pyfloat(left_digits=2, right_digits=2, positive=True):.2f}"
                else:
                    if random.random() < 0.5:
                        text = "".join(
                            [fake.random_letter() for _ in range(random.randint(1, 3))]
                        )
                    else:
                        text = " ".join(fake.words(nb=random.randint(1, 5)))
                content[i][j] = text
    return content


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    """Wrap text to fit within a maximum width."""
    words = text.split()
    lines = []
    current_line = []
    current_width = 0.0
    space_width = font.getlength(" ")
    for word in words:
        word_width = font.getlength(word)
        if current_width + word_width > max_width and current_line:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_width = word_width
        else:
            current_line.append(word)
            current_width += word_width + (space_width if current_line else 0)
    if current_line:
        lines.append(" ".join(current_line))
    return lines


def generate_table(
    output_dir: Optional[Path] = None,
    min_rows: int = 1,
    min_columns: int = 1,
    output_filename: str = "table",
    is_normal: Optional[bool] = None,
    margin: int = 10,
    empty_row_probability: float = 0.3,
    empty_column_probability: float = 0.3,
    empty_cell_probability: float = 0.2
) -> Tuple[Path, Path]:
    """Generate and save a table image and JSON data.

    Args:
        output_dir: Directory to save output files. Defaults to current directory.
        min_rows: Minimum number of rows to generate
        min_columns: Minimum number of columns to generate
        output_filename: Base filename for the output files (without extension)
        is_normal: If True, generates a regular table with uniform cells and all solid lines.
                   If False, generates a table with varied cells and mixed line styles.
                   If None (default), randomly decides with 50% probability.
        margin: Margin size in pixels around the table
        empty_row_probability: Probability of creating an empty row (when not normal)
        empty_column_probability: Probability of creating an empty column (when not normal)
        empty_cell_probability: Probability of any individual cell being empty

    Returns:
        Tuple of paths to the generated image and JSON files.
    """
    fake = Faker()
    rows, columns, total_width, total_height = generate_table_dimensions(
        margin, min_rows=min_rows, min_columns=min_columns
    )

    # Determine if this table is normal
    if is_normal is None:
        is_normal = random.random() < 0.5

    # Generate sizes: uniform for normal, varied for modified
    column_widths = generate_cell_sizes(
        columns, total_width, min_size=40, uniform=is_normal
    )
    row_heights = generate_cell_sizes(
        rows, total_height, min_size=30, uniform=is_normal
    )

    # Font setup
    font_size = random.randint(12, 16)
    try:
        font = ImageFont.truetype("Helvetica.ttf", font_size)
    except IOError:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)

    # Generate line styles
    line_styles = generate_line_styles(rows, columns, is_normal)

    # Create image with margins
    image = Image.new(
        "RGB", (total_width + 2 * margin, total_height + 2 * margin), "white"
    )
    draw = ImageDraw.Draw(image)
    draw_grid(draw, column_widths, row_heights, line_styles, margin)

    # Add cell content
    cell_content = generate_cell_content(
        rows=rows, 
        columns=columns, 
        fake=fake, 
        is_normal=is_normal,
        empty_row_probability=empty_row_probability,
        empty_column_probability=empty_column_probability,
        empty_cell_probability=empty_cell_probability
    )
    padding = 5
    for i in range(rows):
        for j in range(columns):
            text = cell_content[i][j]
            if text is not None:
                left = margin + sum(column_widths[:j])
                top = margin + sum(row_heights[:i])
                cell_width = column_widths[j]
                cell_height = row_heights[i]
                wrapped_text = wrap_text(text, font, cell_width - 2 * padding)
                ascent, descent = font.getmetrics()
                line_height = ascent + descent
                max_lines = (cell_height - 2 * padding) // line_height
                truncated_text = wrapped_text[:max_lines]
                for k, line in enumerate(truncated_text):
                    x = left + padding
                    y = top + padding + k * line_height
                    draw.text((x, y), line, font=font, fill="black")

    # Setup output directory
    if output_dir is None:
        # Use a temporary directory if none is provided
        output_dir = Path.cwd() / "temp"
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Save the image
    image_path = output_dir / f"{output_filename}.png"
    image.save(image_path)

    # Save the table data as JSON
    json_path = output_dir / f"{output_filename}.json"
    with open(json_path, "w") as f:
        json.dump(cell_content, f)

    return image_path, json_path


def generate_tables(
    count: int = 1,
    output_dir: Optional[Path] = None,
    min_rows: int = 1,
    min_columns: int = 1,
    is_normal: Optional[bool] = None,
    margin: int = 10,
    empty_row_probability: float = 0.3,
    empty_column_probability: float = 0.3,
    empty_cell_probability: float = 0.2
) -> List[Tuple[Path, Path]]:
    """Generate multiple tables with configurable parameters.
    
    Args:
        count: Number of tables to generate
        output_dir: Directory to save output files. Defaults to current directory.
        min_rows: Minimum number of rows in each table
        min_columns: Minimum number of columns in each table
        is_normal: If True, generates regular tables with uniform cells and solid lines.
                   If False, generates tables with varied cells and mixed line styles.
                   If None (default), randomly decides for each table with 50% probability.
        margin: Margin size in pixels around each table
        empty_row_probability: Probability of creating an empty row (when not normal)
        empty_column_probability: Probability of creating an empty column (when not normal)
        empty_cell_probability: Probability of any individual cell being empty
        
    Returns:
        List of tuples containing paths to the generated image and JSON files
    """
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create separate directories for images and JSON files
    images_dir = output_dir / "images"
    json_dir = output_dir / "json"
    
    images_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)
        
    results = []
    for i in range(count):
        # Generate a unique filename for this table
        filename = f"table_{i+1}" if count > 1 else "table"
        
        # Generate the table, specifying the separate output directories
        image_path, json_path = generate_table(
            output_dir=None,  # We'll set this manually below
            min_rows=min_rows,
            min_columns=min_columns,
            output_filename=filename,
            is_normal=is_normal,
            margin=margin,
            empty_row_probability=empty_row_probability,
            empty_column_probability=empty_column_probability,
            empty_cell_probability=empty_cell_probability
        )
        
        # Save to the appropriate directories
        final_image_path = images_dir / f"{filename}.png"
        final_json_path = json_dir / f"{filename}.json"
        
        # Move the files to their final locations
        image_path.rename(final_image_path)
        json_path.rename(final_json_path)
        
        results.append((final_image_path, final_json_path))
    
    return results


def main() -> None:
    """Generate table image and JSON data based on command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate random tables as PNG images and JSON data")
    
    parser.add_argument(
        "--count", "-c", 
        type=int, 
        default=1, 
        help="Number of tables to generate (default: 1)"
    )
    parser.add_argument(
        "--min-rows", "-r", 
        type=int, 
        default=1, 
        help="Minimum number of rows for each table (default: 1)"
    )
    parser.add_argument(
        "--min-columns", "-m", 
        type=int, 
        default=1, 
        help="Minimum number of columns for each table (default: 1)"
    )
    parser.add_argument(
        "--output", "-o", 
        type=str, 
        default=None, 
        help="Output directory (default: current directory)"
    )
    parser.add_argument(
        "--normal",
        action="store_true",
        help="Generate normal tables with uniform cells and solid lines"
    )
    parser.add_argument(
        "--random",
        action="store_true",
        help="Generate random tables with varied cells and mixed line styles"
    )
    parser.add_argument(
        "--margin",
        type=int,
        default=10,
        help="Margin size in pixels around each table (default: 10)"
    )
    parser.add_argument(
        "--empty-row-probability",
        type=float,
        default=0.3,
        help="Probability of creating an empty row (default: 0.3)"
    )
    parser.add_argument(
        "--empty-column-probability",
        type=float,
        default=0.3,
        help="Probability of creating an empty column (default: 0.3)"
    )
    parser.add_argument(
        "--empty-cell-probability",
        type=float,
        default=0.2,
        help="Probability of any individual cell being empty (default: 0.2)"
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output) if args.output else None
    
    # Handle normal/random options
    is_normal = None  # Default: random 50/50
    if args.normal and args.random:
        print("Warning: Both --normal and --random specified; using default random behavior")
    elif args.normal:
        is_normal = True
    elif args.random:
        is_normal = False
    
    results = generate_tables(
        count=args.count,
        min_rows=args.min_rows,
        min_columns=args.min_columns,
        output_dir=output_dir,
        is_normal=is_normal,
        margin=args.margin,
        empty_row_probability=args.empty_row_probability,
        empty_column_probability=args.empty_column_probability,
        empty_cell_probability=args.empty_cell_probability
    )
    
    # Group results by directory for clearer output
    if results:
        images_dir = results[0][0].parent
        json_dir = results[0][1].parent
        
        print(f"Generated {len(results)} tables:")
        print(f"  Images saved in: {images_dir}")
        print(f"  JSON data saved in: {json_dir}")
        
        for i, (image_path, json_path) in enumerate(results):
            print(f"  Table {i+1}: {image_path.name}, {json_path.name}")


if __name__ == "__main__":
    main()
