import sys
from unittest.mock import patch


from table_maker.cli import parse_args, main


def test_parse_args():
    """Test that command line arguments are parsed correctly."""
    test_args = [
        "--count",
        "5",
        "--min-rows",
        "3",
        "--min-columns",
        "4",
        "--max-rows",
        "10",
        "--max-columns",
        "12",
        "--output",
        "/tmp/test",
        "--normal",
        "--margin",
        "15",
        "--wrap-mode",
        "char",
    ]

    with patch.object(sys, "argv", ["table-maker"] + test_args):
        args = parse_args()

    assert args.count == 5
    assert args.min_rows == 3
    assert args.min_columns == 4
    assert args.max_rows == 10
    assert args.max_columns == 12
    assert args.output == "/tmp/test"
    assert args.normal is True
    assert args.random is False
    assert args.margin == 15
    assert args.wrap_mode == "char"

    # Check that default values are set
    assert args.normal_probability == 0.5
    assert args.empty_row_probability == 0.3
    assert args.empty_column_probability == 0.3
    assert args.empty_cell_probability == 0.2
    assert args.large_number_probability == 0.05
    assert args.column_header_probability == 0.0
    assert args.row_header_probability == 0.0


def test_main_function(temp_output_dir):
    """Test that the main function runs without errors."""
    # Use minimal arguments to make the test fast
    test_args = [
        "--count",
        "1",
        "--min-rows",
        "2",
        "--min-columns",
        "2",
        "--max-rows",
        "3",
        "--max-columns",
        "3",
        "--output",
        str(temp_output_dir),
        "--normal",  # Make the output deterministic
    ]

    with patch.object(sys, "argv", ["table-maker"] + test_args):
        main()  # Should run without errors

    # Check that the expected directories were created
    images_dir = temp_output_dir / "images"
    json_dir = temp_output_dir / "json"
    assert images_dir.exists()
    assert json_dir.exists()

    # Check that files were created
    assert len(list(images_dir.glob("*.png"))) == 1
    assert len(list(json_dir.glob("*.json"))) == 1


def test_main_with_normal_and_random_flags(temp_output_dir):
    """Test that the main function handles conflicting flags gracefully."""
    # Test with both normal and random flags
    test_args = [
        "--count",
        "1",
        "--min-rows",
        "2",
        "--min-columns",
        "2",
        "--max-rows",
        "3",
        "--max-columns",
        "3",
        "--output",
        str(temp_output_dir),
        "--normal",
        "--random",  # Conflicting flag
    ]

    # We're not checking stdout, just making sure it runs without errors
    with patch.object(sys, "argv", ["table-maker"] + test_args):
        main()

    # Files should still be created
    images_dir = temp_output_dir / "images"
    json_dir = temp_output_dir / "json"
    assert images_dir.exists()
    assert json_dir.exists()
    assert len(list(images_dir.glob("*.png"))) == 1
