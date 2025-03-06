import json
from PIL import Image


from table_maker.maker import (
    generate_table,
    generate_tables,
    generate_table_dimensions,
    generate_cell_sizes,
)


def test_generate_table_dimensions():
    """Test that table dimensions are within expected ranges."""
    margin = 10
    min_rows, min_cols = 3, 4
    max_rows, max_cols = 8, 10

    rows, cols, width, height = generate_table_dimensions(
        margin, min_rows, min_cols, max_rows, max_cols
    )

    # Check rows and columns are within specified ranges
    assert min_rows <= rows <= max_rows
    assert min_cols <= cols <= max_cols

    # Check width and height are within reasonable bounds
    min_width = cols * 40
    min_height = rows * 30
    max_width = 2560 - 2 * margin
    max_height = 1600 - 2 * margin

    assert min_width <= width <= max_width
    assert min_height <= height <= max_height


def test_generate_cell_sizes():
    """Test that generated cell sizes meet requirements."""
    # Test uniform distribution
    num_cells = 5
    total_size = 100
    min_size = 10

    uniform_sizes = generate_cell_sizes(num_cells, total_size, min_size, uniform=True)

    # Check count and sum
    assert len(uniform_sizes) == num_cells
    assert sum(uniform_sizes) == total_size

    # Check all sizes are at least min_size
    assert all(size >= min_size for size in uniform_sizes)

    # Test non-uniform distribution
    non_uniform_sizes = generate_cell_sizes(
        num_cells, total_size, min_size, uniform=False
    )

    # Check count and sum
    assert len(non_uniform_sizes) == num_cells
    assert sum(non_uniform_sizes) == total_size

    # Check all sizes are at least min_size
    assert all(size >= min_size for size in non_uniform_sizes)


def test_generate_table(temp_output_dir):
    """Test that generate_table produces expected files."""
    # Generate a table with controlled parameters
    image_path, json_path = generate_table(
        output_dir=temp_output_dir,
        min_rows=2,
        min_columns=3,
        max_rows=5,
        max_columns=6,
        output_filename="test_table",
        is_normal=True,  # Use normal table for deterministic test
        margin=10,
    )

    # Check that the files were created
    assert image_path.exists()
    assert json_path.exists()

    # Check that image file is a valid PNG
    with Image.open(image_path) as img:
        assert img.format == "PNG"
        # Image should have some reasonable dimensions
        assert img.width > 100
        assert img.height > 100

    # Check that JSON file contains expected structure
    with open(json_path) as f:
        data = json.load(f)

    # Verify JSON structure
    assert "data" in data
    assert isinstance(data["data"], list)
    assert "has_column_headers" in data
    assert "has_row_headers" in data


def test_generate_tables(temp_output_dir):
    """Test that generate_tables produces the expected number of files."""
    # Generate multiple tables
    count = 3
    results = generate_tables(
        count=count,
        output_dir=temp_output_dir,
        min_rows=2,
        min_columns=2,
        max_rows=4,
        max_columns=4,
        is_normal=True,  # Use normal table for deterministic test
    )

    # Check that we got the expected number of results
    assert len(results) == count

    # Check that the expected directories were created
    images_dir = temp_output_dir / "images"
    json_dir = temp_output_dir / "json"
    assert images_dir.exists()
    assert json_dir.exists()

    # Check that all files exist
    for image_path, json_path in results:
        assert image_path.exists()
        assert json_path.exists()

    # Check that the number of files in each directory matches count
    assert len(list(images_dir.glob("*.png"))) == count
    assert len(list(json_dir.glob("*.json"))) == count
