from PIL import Image, ImageDraw, ImageFont
import random
from itertools import accumulate
from faker import Faker
import json
from pathlib import Path
from typing import List, Tuple, Optional, Union, Any, Dict


# Path configuration constants
OUTPUT_DIRS = {"images": "images", "json": "json"}

FILE_EXTENSIONS = {"image": ".png", "json": ".json"}


def generate_table_dimensions(
    margin: int,
    min_rows: int = 1,
    min_columns: int = 1,
    max_rows: int = 15,
    max_columns: int = 40,
) -> Tuple[int, int, int, int]:
    """Generate random table dimensions within constraints, accounting for margins.

    Args:
        margin: Margin size in pixels
        min_rows: Minimum number of rows to generate
        min_columns: Minimum number of columns to generate
        max_rows: Maximum number of rows to generate
        max_columns: Maximum number of columns to generate

    Returns:
        Tuple of (rows, columns, total_width, total_height)
    """
    rows = random.randint(min_rows, max(min_rows, max_rows))
    columns = random.randint(min_columns, max(min_columns, max_columns))
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
    empty_cell_probability: float = 0.2,
    large_number_probability: float = 0.05,
    column_header_probability: float = 0.0,
    row_header_probability: float = 0.0,
) -> Dict[str, Any]:
    """Generate diverse cell content using Faker.

    Args:
        rows: Number of rows in the table
        columns: Number of columns in the table
        fake: Faker instance for generating content
        is_normal: If True, no empty rows/columns will be created
        empty_row_probability: Probability of each row being empty (when not normal)
        empty_column_probability: Probability of creating an empty column (when not normal)
        empty_cell_probability: Probability of any individual cell being empty
        large_number_probability: Probability of generating very large numbers (15-30 digits)
        column_header_probability: Probability of generating column headers
        row_header_probability: Probability of generating row headers

    Returns:
        Dictionary with keys:
        - "data": 2D list of cell content (main table body)
        - "column_headers": List of column headers (if present)
        - "row_headers": List of row headers (if present)
        - "corner_header": Corner header text (if both row and column headers are present)
        - "has_column_headers": Boolean indicating if column headers exist
        - "has_row_headers": Boolean indicating if row headers exist
    """
    # Determine if table has headers
    has_column_headers = random.random() < column_header_probability
    has_row_headers = random.random() < row_header_probability

    # Adjust row/column count for data body (excluding headers)
    data_rows = rows - (1 if has_column_headers else 0)
    data_columns = columns - (1 if has_row_headers else 0)

    # Initialize the result structure
    result = {
        "data": [[None for _ in range(data_columns)] for _ in range(data_rows)],
        "has_column_headers": has_column_headers,
        "has_row_headers": has_row_headers,
        "column_headers": [None] * data_columns if has_column_headers else [],
        "row_headers": [None] * data_rows if has_row_headers else [],
        "corner_header": "ID" if has_column_headers and has_row_headers else None,
    }

    # Determine empty rows and columns
    empty_rows: List[bool] = [False] * data_rows
    empty_column: Optional[int] = None

    if not is_normal:
        # Each row has independent chance to be empty
        for i in range(data_rows):
            if random.random() < empty_row_probability:
                empty_rows[i] = True

        # Still using original logic for empty column
        if random.random() < empty_column_probability:
            empty_column = random.randint(0, data_columns - 1)

    # Generate column headers if needed
    if has_column_headers:
        for j in range(data_columns):
            # Skip empty columns
            if j == empty_column:
                continue

            # Generate a header (always text)
            header_options = [
                fake.word().capitalize(),
                " ".join(
                    [word.capitalize() for word in fake.words(nb=random.randint(1, 2))]
                ),
                fake.last_name(),
                fake.currency_name(),
            ]
            result["column_headers"][j] = random.choice(header_options)

    # Generate row headers if needed
    if has_row_headers:
        for i in range(data_rows):
            # Skip empty rows
            if empty_rows[i]:
                continue

            # Generate a header (always text or numbers)
            if random.random() < 0.7:
                # Text header
                header_options = [
                    fake.word().capitalize(),
                    fake.last_name(),
                    fake.first_name(),
                    fake.country(),
                ]
                result["row_headers"][i] = random.choice(header_options)
            else:
                # Numeric header (like row numbers)
                result["row_headers"][i] = str(i)

    # Generate main table data
    for i in range(data_rows):
        for j in range(data_columns):
            # Skip if should be empty
            if empty_rows[i] or j == empty_column:
                continue

            if random.random() < empty_cell_probability:
                continue  # Leave as None
            else:
                if random.random() < 0.6:
                    # Determine if we should generate a large number
                    if random.random() < large_number_probability:
                        # Generate large integers of varying lengths
                        digit_count = random.choice([15, 20, 25, 30])
                        text = "".join(
                            [str(random.randint(0, 9)) for _ in range(digit_count)]
                        )
                    elif random.random() < 0.5:
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
                result["data"][i][j] = text

    return result


def wrap_text(
    text: str, font: ImageFont.FreeTypeFont, max_width: int, wrap_mode: str = "word"
) -> List[str]:
    """Wrap text to fit within a maximum width.

    Args:
        text: The text to wrap
        font: Font object for text measurement
        max_width: Maximum width in pixels for text to fit within
        wrap_mode: Text wrapping mode:
            - "word": Wrap at word boundaries (standard)
            - "none": No wrapping, text may extend beyond cell
            - "char": Break words if necessary to fit within width

    Returns:
        List of lines after wrapping
    """
    if wrap_mode == "none":
        # No wrapping, return single line
        return [text]

    elif wrap_mode == "word":
        # Standard word wrapping
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

    elif wrap_mode == "char":
        # Character-based wrapping (break words if needed)
        lines = []
        current_line = ""
        current_width = 0.0

        for char in text:
            char_width = font.getlength(char)
            if current_width + char_width <= max_width:
                current_line += char
                current_width += char_width
            else:
                if current_line:  # Only add non-empty lines
                    lines.append(current_line)
                current_line = char
                current_width = char_width

        if current_line:  # Add the last line if not empty
            lines.append(current_line)
        return lines

    # Default to word wrapping for any other value
    return wrap_text(text, font, max_width, "word")


def generate_table(
    output_dir: Optional[Path] = None,
    min_rows: int = 1,
    min_columns: int = 1,
    max_rows: int = 15,
    max_columns: int = 40,
    output_filename: str = "table",
    is_normal: Optional[bool] = None,
    normal_probability: float = 0.5,
    margin: int = 10,
    empty_row_probability: float = 0.3,
    empty_column_probability: float = 0.3,
    empty_cell_probability: float = 0.2,
    large_number_probability: float = 0.05,
    column_header_probability: float = 0.0,
    row_header_probability: float = 0.0,
    wrap_mode: str = "word",
    output_paths: Optional[Dict[str, Path]] = None,
) -> Tuple[Path, Path]:
    """Generate and save a table image and JSON data.

    Args:
        output_dir: Directory to save output files. Defaults to current directory.
        min_rows: Minimum number of rows to generate
        min_columns: Minimum number of columns to generate
        max_rows: Maximum number of rows to generate
        max_columns: Maximum number of columns to generate
        output_filename: Base filename for the output files (without extension)
        is_normal: If True, generates a regular table with uniform cells and all solid lines.
                   If False, generates a table with varied cells and mixed line styles.
                   If None (default), randomly decides based on normal_probability.
        normal_probability: Probability of generating a normal table when is_normal is None (0.0-1.0)
        margin: Margin size in pixels around the table
        empty_row_probability: Probability of each row being empty (when not normal)
        empty_column_probability: Probability of creating an empty column (when not normal)
        empty_cell_probability: Probability of any individual cell being empty
        large_number_probability: Probability of generating very large numbers (15-30 digits)
        column_header_probability: Probability of generating column headers (0.0-1.0)
        row_header_probability: Probability of generating row headers (0.0-1.0)
        wrap_mode: Text wrapping mode: "word" (default), "none", or "char"
        output_paths: Optional dict with explicit output paths for 'image' and 'json'

    Returns:
        Tuple of paths to the generated image and JSON files.
    """
    fake = Faker()
    rows, columns, total_width, total_height = generate_table_dimensions(
        margin,
        min_rows=min_rows,
        min_columns=min_columns,
        max_rows=max_rows,
        max_columns=max_columns,
    )

    # Determine if this table is normal
    if is_normal is None:
        is_normal = random.random() < normal_probability

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
    table_data = generate_cell_content(
        rows=rows,
        columns=columns,
        fake=fake,
        is_normal=is_normal,
        empty_row_probability=empty_row_probability,
        empty_column_probability=empty_column_probability,
        empty_cell_probability=empty_cell_probability,
        large_number_probability=large_number_probability,
        column_header_probability=column_header_probability,
        row_header_probability=row_header_probability,
    )

    # Extract values for easier reference
    has_column_headers = table_data["has_column_headers"]
    has_row_headers = table_data["has_row_headers"]
    data = table_data["data"]
    column_headers = table_data["column_headers"]
    row_headers = table_data["row_headers"]
    corner_header = table_data["corner_header"]

    # For rendering, we need to track current position
    padding = 5

    # Try to get a bold font for headers
    try:
        header_font = ImageFont.truetype("Helvetica-Bold.ttf", font_size)
    except IOError:
        try:
            header_font = ImageFont.truetype(
                "/System/Library/Fonts/Helvetica.ttc", font_size, index=1
            )
        except IOError:
            # Fall back to regular font if bold isn't available
            header_font = font

    # Draw corner header if both column and row headers exist
    if has_column_headers and has_row_headers and corner_header is not None:
        left = margin
        top = margin
        cell_width = column_widths[0]
        cell_height = row_heights[0]

        wrapped_text = wrap_text(
            corner_header, header_font, cell_width - 2 * padding, wrap_mode
        )
        ascent, descent = header_font.getmetrics()
        line_height = ascent + descent
        max_lines = (cell_height - 2 * padding) // line_height
        truncated_text = wrapped_text[:max_lines]

        # Center the corner header
        for k, line in enumerate(truncated_text):
            line_width = header_font.getlength(line)
            x = left + (cell_width - line_width) // 2
            y = top + padding + k * line_height
            draw.text((x, y), line, font=header_font, fill="black")

    # Draw column headers
    if has_column_headers:
        header_row_idx = 0
        for j, header in enumerate(column_headers):
            if header is not None:
                # Calculate position (account for row header if present)
                col_offset = 1 if has_row_headers else 0
                left = margin + sum(column_widths[: j + col_offset])
                top = margin
                cell_width = column_widths[j + col_offset]
                cell_height = row_heights[header_row_idx]

                wrapped_text = wrap_text(
                    header, header_font, cell_width - 2 * padding, wrap_mode
                )
                ascent, descent = header_font.getmetrics()
                line_height = ascent + descent
                max_lines = (cell_height - 2 * padding) // line_height
                truncated_text = wrapped_text[:max_lines]

                # Center the header
                for k, line in enumerate(truncated_text):
                    line_width = header_font.getlength(line)
                    x = left + (cell_width - line_width) // 2
                    y = top + padding + k * line_height
                    draw.text((x, y), line, font=header_font, fill="black")

    # Draw row headers
    if has_row_headers:
        header_col_idx = 0
        for i, header in enumerate(row_headers):
            if header is not None:
                # Calculate position (account for column header if present)
                row_offset = 1 if has_column_headers else 0
                left = margin
                top = margin + sum(row_heights[: i + row_offset])
                cell_width = column_widths[header_col_idx]
                cell_height = row_heights[i + row_offset]

                wrapped_text = wrap_text(
                    header, header_font, cell_width - 2 * padding, wrap_mode
                )
                ascent, descent = header_font.getmetrics()
                line_height = ascent + descent
                max_lines = (cell_height - 2 * padding) // line_height
                truncated_text = wrapped_text[:max_lines]

                # Center the header
                for k, line in enumerate(truncated_text):
                    line_width = header_font.getlength(line)
                    x = left + (cell_width - line_width) // 2
                    y = top + padding + k * line_height
                    draw.text((x, y), line, font=header_font, fill="black")

    # Draw data cells
    for i in range(len(data)):
        for j in range(len(data[i])):
            cell_value = data[i][j]
            if cell_value is not None:
                # Calculate position (account for headers)
                row_offset = 1 if has_column_headers else 0
                col_offset = 1 if has_row_headers else 0
                left = margin + sum(column_widths[: j + col_offset])
                top = margin + sum(row_heights[: i + row_offset])
                cell_width = column_widths[j + col_offset]
                cell_height = row_heights[i + row_offset]

                wrapped_text = wrap_text(
                    cell_value, font, cell_width - 2 * padding, wrap_mode
                )
                ascent, descent = font.getmetrics()
                line_height = ascent + descent
                max_lines = (cell_height - 2 * padding) // line_height
                truncated_text = wrapped_text[:max_lines]

                # Regular cell text alignment (left-aligned)
                for k, line in enumerate(truncated_text):
                    x = left + padding
                    y = top + padding + k * line_height
                    draw.text((x, y), line, font=font, fill="black")

    # Determine output paths
    if output_paths:
        # Use explicitly provided paths
        image_path = output_paths["image"]
        json_path = output_paths["json"]
    else:
        # Use output_dir with filename
        if output_dir is None:
            output_dir = Path.cwd()
        else:
            output_dir = Path(output_dir)

        # Ensure directories exist
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create file paths
        image_path = output_dir / f"{output_filename}{FILE_EXTENSIONS['image']}"
        json_path = output_dir / f"{output_filename}{FILE_EXTENSIONS['json']}"

    # Ensure parent directories exist
    image_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    # Save the image
    image.save(image_path)

    # Save the table data as JSON
    with open(json_path, "w") as f:
        json.dump(table_data, f, indent=2)

    return image_path, json_path


def generate_tables(
    count: int = 1,
    output_dir: Optional[Path] = None,
    min_rows: int = 1,
    min_columns: int = 1,
    max_rows: int = 15,
    max_columns: int = 40,
    is_normal: Optional[bool] = None,
    normal_probability: float = 0.5,
    margin: int = 10,
    empty_row_probability: float = 0.3,
    empty_column_probability: float = 0.3,
    empty_cell_probability: float = 0.2,
    large_number_probability: float = 0.05,
    column_header_probability: float = 0.0,
    row_header_probability: float = 0.0,
    wrap_mode: str = "word",
) -> List[Tuple[Path, Path]]:
    """Generate multiple tables with configurable parameters.

    Args:
        count: Number of tables to generate
        output_dir: Directory to save output files. Defaults to current directory.
        min_rows: Minimum number of rows in each table
        min_columns: Minimum number of columns in each table
        max_rows: Maximum number of rows in each table
        max_columns: Maximum number of columns in each table
        is_normal: If True, generates regular tables with uniform cells and solid lines.
                   If False, generates tables with varied cells and mixed line styles.
                   If None (default), randomly decides for each table based on normal_probability.
        normal_probability: Probability of generating a normal table when is_normal is None (0.0-1.0)
        margin: Margin size in pixels around each table
        empty_row_probability: Probability of each row being empty (when not normal)
        empty_column_probability: Probability of creating an empty column (when not normal)
        empty_cell_probability: Probability of any individual cell being empty
        large_number_probability: Probability of generating very large numbers (15-30 digits)
        column_header_probability: Probability of generating column headers (0.0-1.0)
        row_header_probability: Probability of generating row headers (0.0-1.0)
        wrap_mode: Text wrapping mode: "word" (default), "none", or "char"

    Returns:
        List of tuples containing paths to the generated image and JSON files
    """
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Create separate directories for images and JSON files
    images_dir = output_dir / OUTPUT_DIRS["images"]
    json_dir = output_dir / OUTPUT_DIRS["json"]

    images_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for i in range(count):
        # Generate a unique filename for this table
        filename = f"table_{i + 1}" if count > 1 else "table"

        # Set up output paths directly
        output_paths = {
            "image": images_dir / f"{filename}{FILE_EXTENSIONS['image']}",
            "json": json_dir / f"{filename}{FILE_EXTENSIONS['json']}",
        }

        # Generate the table with explicit output paths
        image_path, json_path = generate_table(
            min_rows=min_rows,
            min_columns=min_columns,
            max_rows=max_rows,
            max_columns=max_columns,
            output_filename=filename,
            is_normal=is_normal,
            normal_probability=normal_probability,
            margin=margin,
            empty_row_probability=empty_row_probability,
            empty_column_probability=empty_column_probability,
            empty_cell_probability=empty_cell_probability,
            large_number_probability=large_number_probability,
            column_header_probability=column_header_probability,
            row_header_probability=row_header_probability,
            wrap_mode=wrap_mode,
            output_paths=output_paths,
        )

        results.append((image_path, json_path))

    return results
