import json
from PIL import Image


from table_maker import (
    generate_table,
    generate_tables,
    generate_table_dimensions,
    TableDimensions,
    TableData,
    RandomDataGenerator,
    TableVisualizer,
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


def test_table_dimensions_cell_sizes():
    """Test that table dimensions generate correct cell sizes."""
    # Test uniform distribution
    num_cells = 5
    total_width = 500
    total_height = 400
    margin = 10
    
    # Create a dimensions object with uniform cell sizing
    uniform_dims = TableDimensions(
        rows=num_cells,
        columns=num_cells,
        total_width=total_width,
        total_height=total_height,
        margin=margin,
        is_uniform=True
    )
    
    # Check column widths
    assert len(uniform_dims.column_widths) == num_cells
    assert sum(uniform_dims.column_widths) == total_width
    assert all(width >= 40 for width in uniform_dims.column_widths)
    
    # Check row heights
    assert len(uniform_dims.row_heights) == num_cells
    assert sum(uniform_dims.row_heights) == total_height
    assert all(height >= 30 for height in uniform_dims.row_heights)
    
    # Test non-uniform distribution
    non_uniform_dims = TableDimensions(
        rows=num_cells,
        columns=num_cells,
        total_width=total_width,
        total_height=total_height,
        margin=margin,
        is_uniform=False
    )
    
    # Check column widths for non-uniform
    assert len(non_uniform_dims.column_widths) == num_cells
    assert sum(non_uniform_dims.column_widths) == total_width
    assert all(width >= 40 for width in non_uniform_dims.column_widths)
    
    # Check row heights for non-uniform
    assert len(non_uniform_dims.row_heights) == num_cells
    assert sum(non_uniform_dims.row_heights) == total_height
    assert all(height >= 30 for height in non_uniform_dims.row_heights)


def test_table_data():
    """Test the TableData class functionality."""
    # Create a table data instance
    table = TableData(
        rows=3,
        columns=4,
        has_column_headers=True,
        has_row_headers=True
    )
    
    # Check initialization
    assert table.rows == 3
    assert table.columns == 4
    assert table.has_column_headers is True
    assert table.has_row_headers is True
    assert len(table.data) == 3
    assert len(table.data[0]) == 4
    assert len(table.column_headers) == 4
    assert len(table.row_headers) == 3
    assert table.corner_header == "ID"
    
    # Test setting values
    table.data[0][0] = "Cell 0,0"
    table.data[1][2] = "Cell 1,2"
    table.column_headers[1] = "Column B"
    table.row_headers[2] = "Row 3"
    
    # Test dictionary conversion
    data_dict = table.to_dict()
    assert data_dict["data"][0][0] == "Cell 0,0"
    assert data_dict["data"][1][2] == "Cell 1,2"
    assert data_dict["column_headers"][1] == "Column B"
    assert data_dict["row_headers"][2] == "Row 3"
    
    # Test reconstruction from dictionary
    reconstructed = TableData.from_dict(data_dict)
    assert reconstructed.data[0][0] == "Cell 0,0"
    assert reconstructed.data[1][2] == "Cell 1,2"
    assert reconstructed.column_headers[1] == "Column B"
    assert reconstructed.row_headers[2] == "Row 3"


def test_random_data_generator():
    """Test the RandomDataGenerator produces expected data."""
    # Use fixed seed for deterministic test
    data_generator = RandomDataGenerator(faker_seed=42)
    
    # Test with normal settings
    table_data = data_generator.generate_table_data(
        rows=3,
        columns=4,
        is_normal=True,
        column_header_probability=1.0,  # Always generate headers for testing
        row_header_probability=1.0,     # Always generate headers for testing
    )
    
    # Check basic structure
    assert table_data.rows == 3
    assert table_data.columns == 4
    assert table_data.has_column_headers is True
    assert table_data.has_row_headers is True
    
    # Check that data is properly sized
    assert len(table_data.data) == 3
    assert len(table_data.data[0]) == 4
    assert len(table_data.column_headers) == 4
    assert len(table_data.row_headers) == 3
    
    # Test non-normal settings
    non_normal_data = data_generator.generate_table_data(
        rows=5,
        columns=5,
        is_normal=False,
        empty_row_probability=0.5,
        empty_column_probability=0.5,
        empty_cell_probability=0.5,
    )
    
    # Basic structure checks
    assert non_normal_data.rows == 5
    assert non_normal_data.columns == 5


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


def test_table_visualizer():
    """Test the TableVisualizer class."""
    # Create test data
    table_data = TableData(
        rows=3,
        columns=3,
        has_column_headers=True,
        has_row_headers=True
    )
    
    # Fill with sample data
    table_data.corner_header = "ID"
    for i in range(3):
        table_data.column_headers[i] = f"Column {i+1}"
        table_data.row_headers[i] = f"Row {i+1}"
        for j in range(3):
            table_data.data[i][j] = f"Cell {i+1},{j+1}"
    
    # Create dimensions
    dimensions = TableDimensions(
        rows=4,  # +1 for headers
        columns=4,  # +1 for headers
        total_width=400,
        total_height=300,
        margin=10,
        is_uniform=True
    )
    
    # Create visualizer
    visualizer = TableVisualizer()
    
    # Render the table
    image = visualizer.render(table_data, dimensions, font_size=12)
    
    # Basic checks
    assert image is not None
    assert image.width == 400 + 2 * 10  # total_width + 2*margin
    assert image.height == 300 + 2 * 10  # total_height + 2*margin


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
