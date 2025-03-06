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