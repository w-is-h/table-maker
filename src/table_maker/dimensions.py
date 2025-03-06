import random
from typing import List, Tuple


class TableDimensions:
    """Class representing table physical dimensions and layout."""
    
    def __init__(
        self, 
        rows: int, 
        columns: int, 
        total_width: int, 
        total_height: int,
        margin: int = 10,
        is_uniform: bool = True
    ):
        """Initialize table dimensions.
        
        Args:
            rows: Number of rows (including headers)
            columns: Number of columns (including headers)
            total_width: Total width in pixels (excluding margins)
            total_height: Total height in pixels (excluding margins)
            margin: Margin size in pixels
            is_uniform: Whether cells should be uniform in size
        """
        self.rows = rows
        self.columns = columns
        self.total_width = total_width
        self.total_height = total_height
        self.margin = margin
        self.is_uniform = is_uniform
        
        # Generate cell sizes
        self.column_widths = self._generate_cell_sizes(
            columns, total_width, min_size=40, uniform=is_uniform
        )
        self.row_heights = self._generate_cell_sizes(
            rows, total_height, min_size=30, uniform=is_uniform
        )
        
        # Generate line styles
        self.horizontal_styles, self.vertical_styles = self._generate_line_styles()
    
    def _generate_cell_sizes(
        self, num_cells: int, total_size: int, min_size: int, uniform: bool = True
    ) -> List[int]:
        """Generate sizes for num_cells that sum to total_size, each at least min_size."""
        if uniform:
            base_size = total_size // num_cells
            remainder = total_size % num_cells
            return [base_size + (1 if i < remainder else 0) for i in range(num_cells)]
        else:
            sizes = [min_size] * num_cells
            remaining = total_size - min_size * num_cells
            while remaining > 0:
                sizes[random.randint(0, num_cells - 1)] += 1
                remaining -= 1
            return sizes
    
    def _generate_line_styles(self) -> Tuple[List[str], List[str]]:
        """Determine line styles for the table grid."""
        if self.is_uniform:
            hor_styles = ["solid_black"] * (self.rows + 1)
            ver_styles = ["solid_black"] * (self.columns + 1)
        else:
            styles = ["solid_black", "dotted_black", "solid_gray", "removed"]
            weights = [0.7, 0.1, 0.1, 0.1]
            hor_styles = [
                random.choices(styles, weights=weights)[0] for _ in range(self.rows + 1)
            ]
            ver_styles = [
                random.choices(styles, weights=weights)[0] for _ in range(self.columns + 1)
            ]
        return hor_styles, ver_styles


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