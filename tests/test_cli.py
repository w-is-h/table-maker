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
        "--style",
        "uniform",
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
    assert args.style == "uniform"
    assert args.margin == 15
    assert args.wrap_mode == "char"

    # Check that default values are set
    assert args.sparsity == 0.2
    assert not args.allow_empty_rows
    assert not args.allow_empty_columns
    assert args.large_number_probability == 0.05
    assert args.headers == "none"


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
        "--style",
        "uniform",  # Make the output deterministic
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


def test_style_options(temp_output_dir):
    """Test that different style options work correctly."""
    # Test with random style
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
        "--style",
        "random",
        "--sparsity",
        "0.3",
    ]

    # We're not checking stdout, just making sure it runs without errors
    with patch.object(sys, "argv", ["table-maker"] + test_args):
        main()

    # Files should be created
    images_dir = temp_output_dir / "images"
    json_dir = temp_output_dir / "json"
    assert images_dir.exists()
    assert json_dir.exists()
    assert len(list(images_dir.glob("*.png"))) == 1
