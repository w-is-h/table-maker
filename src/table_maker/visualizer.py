from PIL import Image, ImageDraw, ImageFont
import random
from itertools import accumulate
from typing import List, Optional, Union, Any
from .table_data import TableData
from .dimensions import TableDimensions


class TableVisualizer:
    """Class for rendering table data as images."""
    
    def __init__(self, wrap_mode: str = "word"):
        """Initialize the table visualizer.
        
        Args:
            wrap_mode: Text wrapping mode ("word", "none", or "char")
        """
        self.wrap_mode = wrap_mode
        self.padding = 5
        
        # Font setup - will be initialized on first use
        self.font: Optional[ImageFont.FreeTypeFont] = None
        self.header_font: Optional[ImageFont.FreeTypeFont] = None
        self.font_size = 0
    
    def _initialize_fonts(self, font_size: Optional[int] = None):
        """Initialize fonts for table rendering.
        
        Args:
            font_size: Font size to use, or None for random size
        """
        if font_size is None:
            self.font_size = random.randint(12, 16)
        else:
            self.font_size = font_size
        
        # Try to load the regular font
        try:
            self.font = ImageFont.truetype("Helvetica.ttf", self.font_size)
        except IOError:
            self.font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", self.font_size)
        
        # Try to get a bold font for headers
        try:
            self.header_font = ImageFont.truetype("Helvetica-Bold.ttf", self.font_size)
        except IOError:
            try:
                self.header_font = ImageFont.truetype(
                    "/System/Library/Fonts/Helvetica.ttc", self.font_size, index=1
                )
            except IOError:
                # Fall back to regular font if bold isn't available
                self.header_font = self.font
    
    def _draw_dotted_line(
        self, draw: Any, x1: int, y1: int, x2: int, y2: int, fill: Union[str, tuple]
    ) -> None:
        """Draw a dotted line between two points."""
        if x1 == x2:  # Vertical
            for y in range(y1, y2, 10):
                draw.line([(x1, y), (x1, min(y + 1, y2))], fill=fill, width=1)
        elif y1 == y2:  # Horizontal
            for x in range(x1, x2, 10):
                draw.line([(x, y1), (min(x + 1, x2), y1)], fill=fill, width=1)
    
    def _draw_grid(
        self,
        draw: Any,
        dimensions: TableDimensions,
    ) -> None:
        """Draw the table grid with specified line styles, accounting for margins."""
        margin = dimensions.margin
        column_widths = dimensions.column_widths
        row_heights = dimensions.row_heights
        hor_styles = dimensions.horizontal_styles
        ver_styles = dimensions.vertical_styles
        
        # Draw vertical lines
        x_positions = [margin + x for x in [0] + list(accumulate(column_widths))]
        for i, x in enumerate(x_positions):
            style = ver_styles[i]
            if style == "solid_black":
                draw.line(
                    [(x, margin), (x, margin + sum(row_heights))], fill="black", width=1
                )
            elif style == "dotted_black":
                self._draw_dotted_line(
                    draw, x, margin, x, margin + sum(row_heights), fill="black"
                )
            elif style == "solid_gray":
                draw.line(
                    [(x, margin), (x, margin + sum(row_heights))],
                    fill=(192, 192, 192),
                    width=1,
                )
        
        # Draw horizontal lines
        y_positions = [margin + y for y in [0] + list(accumulate(row_heights))]
        for i, y in enumerate(y_positions):
            style = hor_styles[i]
            if style == "solid_black":
                draw.line(
                    [(margin, y), (margin + sum(column_widths), y)], fill="black", width=1
                )
            elif style == "dotted_black":
                self._draw_dotted_line(
                    draw, margin, y, margin + sum(column_widths), y, fill="black"
                )
            elif style == "solid_gray":
                draw.line(
                    [(margin, y), (margin + sum(column_widths), y)],
                    fill=(192, 192, 192),
                    width=1,
                )
    
    def _wrap_text(
        self, text: str, font: ImageFont.FreeTypeFont, max_width: int, wrap_mode: Optional[str] = None
    ) -> List[str]:
        """Wrap text to fit within a maximum width.
        
        Args:
            text: The text to wrap
            font: Font object for text measurement
            max_width: Maximum width in pixels for text to fit within
            wrap_mode: Text wrapping mode, or None to use instance default
            
        Returns:
            List of lines after wrapping
        """
        if wrap_mode is None:
            wrap_mode = self.wrap_mode
            
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
        return self._wrap_text(text, font, max_width, "word")
    
    def render(
        self, 
        table_data: TableData, 
        dimensions: TableDimensions,
        font_size: Optional[int] = None,
    ) -> Image.Image:
        """Render table data as an image.
        
        Args:
            table_data: The table data to render
            dimensions: Table dimensions for rendering
            font_size: Font size to use, or None for random size
            
        Returns:
            PIL Image containing the rendered table
        """
        # Initialize fonts if needed
        if self.font is None or font_size is not None:
            self._initialize_fonts(font_size)
        
        # Ensure fonts are initialized
        assert self.font is not None, "Font must be initialized before rendering"
        assert self.header_font is not None, "Header font must be initialized before rendering"
        
        margin = dimensions.margin
        
        # Create image with margins
        image = Image.new(
            "RGB", 
            (dimensions.total_width + 2 * margin, dimensions.total_height + 2 * margin), 
            "white"
        )
        draw = ImageDraw.Draw(image)
        
        # Draw the grid
        self._draw_grid(draw, dimensions)
        
        # Extract values for easier reference
        has_column_headers = table_data.has_column_headers
        has_row_headers = table_data.has_row_headers
        data = table_data.data
        column_headers = table_data.column_headers
        row_headers = table_data.row_headers
        corner_header = table_data.corner_header
        
        column_widths = dimensions.column_widths
        row_heights = dimensions.row_heights
        
        # Draw corner header if both column and row headers exist
        if has_column_headers and has_row_headers and corner_header is not None:
            left = margin
            top = margin
            cell_width = column_widths[0]
            cell_height = row_heights[0]
            
            wrapped_text = self._wrap_text(
                corner_header, self.header_font, cell_width - 2 * self.padding
            )
            ascent, descent = self.header_font.getmetrics()
            line_height = ascent + descent
            max_lines = (cell_height - 2 * self.padding) // line_height
            truncated_text = wrapped_text[:max_lines]
            
            # Center the corner header
            for k, line in enumerate(truncated_text):
                line_width = self.header_font.getlength(line)
                x = left + (cell_width - line_width) // 2
                y = top + self.padding + k * line_height
                draw.text((x, y), line, font=self.header_font, fill="black")
        
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
                    
                    wrapped_text = self._wrap_text(
                        header, self.header_font, cell_width - 2 * self.padding
                    )
                    ascent, descent = self.header_font.getmetrics()
                    line_height = ascent + descent
                    max_lines = (cell_height - 2 * self.padding) // line_height
                    truncated_text = wrapped_text[:max_lines]
                    
                    # Center the header
                    for k, line in enumerate(truncated_text):
                        line_width = self.header_font.getlength(line)
                        x = left + (cell_width - line_width) // 2
                        y = top + self.padding + k * line_height
                        draw.text((x, y), line, font=self.header_font, fill="black")
        
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
                    
                    wrapped_text = self._wrap_text(
                        header, self.header_font, cell_width - 2 * self.padding
                    )
                    ascent, descent = self.header_font.getmetrics()
                    line_height = ascent + descent
                    max_lines = (cell_height - 2 * self.padding) // line_height
                    truncated_text = wrapped_text[:max_lines]
                    
                    # Center the header
                    for k, line in enumerate(truncated_text):
                        line_width = self.header_font.getlength(line)
                        x = left + (cell_width - line_width) // 2
                        y = top + self.padding + k * line_height
                        draw.text((x, y), line, font=self.header_font, fill="black")
        
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
                    
                    wrapped_text = self._wrap_text(
                        cell_value, self.font, cell_width - 2 * self.padding
                    )
                    ascent, descent = self.font.getmetrics()
                    line_height = ascent + descent
                    max_lines = (cell_height - 2 * self.padding) // line_height
                    truncated_text = wrapped_text[:max_lines]
                    
                    # Regular cell text alignment (left-aligned)
                    for k, line in enumerate(truncated_text):
                        x = left + self.padding
                        y = top + self.padding + k * line_height
                        draw.text((x, y), line, font=self.font, fill="black")
        
        return image