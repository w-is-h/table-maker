# Table Maker

Generate random tables as PNG images and JSON data.

## Usage

Direct CLI usage:
```bash
uv run python -m table_maker
```

After installation:
```bash
table-maker
```

### Examples

Generate a single table with default settings:
```bash
table-maker
```

Generate multiple tables with custom settings:
```bash
table-maker --count 5 --min-rows 3 --min-columns 4 --max-rows 10 --max-columns 12 --output ./output
```

Generate a table with column and row headers:
```bash
table-maker --column-header-probability 1.0 --row-header-probability 1.0
```

Generate a non-uniform table with random empty cells:
```bash
table-maker --random --empty-cell-probability 0.3
```

### Available Options

```
--count              Number of tables to generate (default: 1)
--min-rows           Minimum number of rows (default: 2)
--min-columns        Minimum number of columns (default: 2)
--max-rows           Maximum number of rows (default: 10)
--max-columns        Maximum number of columns (default: 15)
--output             Output directory (default: current directory)
--normal             Generate uniform tables with solid borders
--random             Generate non-uniform tables with mixed borders
--margin             Margin size in pixels (default: 10)
--wrap-mode          Text wrapping mode: word, none, char (default: word)
--empty-row-probability      Probability for empty rows (default: 0.3)
--empty-column-probability   Probability for empty columns (default: 0.3)
--empty-cell-probability     Probability for empty cells (default: 0.2)
--column-header-probability  Probability for column headers (default: 0.0)
--row-header-probability     Probability for row headers (default: 0.0)
```

## Output

- `images/table.png`: Visual representation of the generated table
- `json/table.json`: Table data as JSON

## Architecture

The project is structured with separate components for:

- `TableData`: Represents the table content and headers
- `TableDimensions`: Handles layout and grid structure
- `RandomDataGenerator`: Generates random content data
- `TableVisualizer`: Renders visual representation of tables

## Development

Run tests:
```bash
uv run pytest
```

Code quality:
```bash
uv run ruff check .
uv run ruff format .
uv run pyright
```