from typing import List, Optional, Dict, Any


class TableData:
    """Class representing table data structure with headers and content."""
    
    def __init__(
        self,
        rows: int, 
        columns: int,
        has_column_headers: bool = False,
        has_row_headers: bool = False,
    ):
        """Initialize table data structure.
        
        Args:
            rows: Number of data rows (excluding headers)
            columns: Number of data columns (excluding headers)
            has_column_headers: Whether the table has column headers
            has_row_headers: Whether the table has row headers
        """
        self.rows = rows
        self.columns = columns
        self.has_column_headers = has_column_headers
        self.has_row_headers = has_row_headers
        
        # Initialize data structures
        self.data: List[List[Optional[str]]] = [[None for _ in range(columns)] for _ in range(rows)]
        self.column_headers: List[Optional[str]] = [None] * columns if has_column_headers else []
        self.row_headers: List[Optional[str]] = [None] * rows if has_row_headers else []
        self.corner_header: Optional[str] = "ID" if has_column_headers and has_row_headers else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert table data to a dictionary representation.
        
        Returns:
            Dictionary containing all table data
        """
        return {
            "data": self.data,
            "has_column_headers": self.has_column_headers,
            "has_row_headers": self.has_row_headers,
            "column_headers": self.column_headers,
            "row_headers": self.row_headers,
            "corner_header": self.corner_header,
        }
    
    @classmethod
    def from_dict(cls, data_dict: Dict[str, Any]) -> 'TableData':
        """Create a TableData instance from a dictionary.
        
        Args:
            data_dict: Dictionary containing table data
            
        Returns:
            New TableData instance
        """
        rows = len(data_dict["data"])
        columns = len(data_dict["data"][0]) if rows > 0 else 0
        
        instance = cls(
            rows=rows,
            columns=columns,
            has_column_headers=data_dict["has_column_headers"],
            has_row_headers=data_dict["has_row_headers"]
        )
        
        instance.data = data_dict["data"]
        instance.column_headers = data_dict["column_headers"]
        instance.row_headers = data_dict["row_headers"]
        instance.corner_header = data_dict["corner_header"]
        
        return instance