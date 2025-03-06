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

Generate a uniform table with both column and row headers:
```bash
table-maker --style uniform --headers both
```

Generate a random table with higher sparsity:
```bash
table-maker --style random --sparsity 0.4 --allow-empty-rows --allow-empty-columns
```

For a complete list of options and their descriptions, run:
```bash
table-maker --help
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