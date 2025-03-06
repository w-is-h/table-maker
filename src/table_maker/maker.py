import random
import json
from pathlib import Path
from typing import List, Tuple, Dict, Optional

from .dimensions import TableDimensions, generate_table_dimensions
from .generators import RandomDataGenerator
from .visualizer import TableVisualizer


# Path configuration constants
OUTPUT_DIRS = {"images": "images", "json": "json"}
FILE_EXTENSIONS = {"image": ".png", "json": ".json"}


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
    # Determine if this table is normal
    if is_normal is None:
        is_normal = random.random() < normal_probability
    
    # Generate table dimensions
    rows, columns, total_width, total_height = generate_table_dimensions(
        margin,
        min_rows=min_rows,
        min_columns=min_columns,
        max_rows=max_rows,
        max_columns=max_columns,
    )
    
    # Create the dimensions object
    dimensions = TableDimensions(
        rows=rows,
        columns=columns,
        total_width=total_width,
        total_height=total_height,
        margin=margin,
        is_uniform=is_normal
    )
    
    # Generate the data
    data_generator = RandomDataGenerator()
    table_data = data_generator.generate_table_data(
        rows=rows,
        columns=columns,
        is_normal=is_normal,
        empty_row_probability=empty_row_probability,
        empty_column_probability=empty_column_probability,
        empty_cell_probability=empty_cell_probability,
        large_number_probability=large_number_probability,
        column_header_probability=column_header_probability,
        row_header_probability=row_header_probability,
    )
    
    # Render the table
    visualizer = TableVisualizer(wrap_mode=wrap_mode)
    image = visualizer.render(table_data, dimensions)
    
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
        json.dump(table_data.to_dict(), f, indent=2)
    
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