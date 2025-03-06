import random
from faker import Faker
from typing import Optional
from .table_data import TableData


class RandomDataGenerator:
    """Generator for random table data."""
    
    def __init__(self, faker_seed: Optional[int] = None):
        """Initialize the random data generator.
        
        Args:
            faker_seed: Optional seed for the Faker instance
        """
        self.fake = Faker()
        if faker_seed is not None:
            self.fake.seed_instance(faker_seed)
    
    def generate_table_data(
        self,
        rows: int,
        columns: int,
        is_normal: bool = True,
        empty_row_probability: float = 0.3,
        empty_column_probability: float = 0.3,
        empty_cell_probability: float = 0.2,
        large_number_probability: float = 0.05,
        column_header_probability: float = 0.0,
        row_header_probability: float = 0.0,
    ) -> TableData:
        """Generate table data with random content.
        
        Args:
            rows: Number of rows in the table
            columns: Number of columns in the table
            is_normal: If True, no empty rows/columns will be created
            empty_row_probability: Probability of each row being empty (when not normal)
            empty_column_probability: Probability of creating an empty column (when not normal)
            empty_cell_probability: Probability of any individual cell being empty
            large_number_probability: Probability of generating very large numbers (15-30 digits)
            column_header_probability: Probability of generating column headers
            row_header_probability: Probability of generating row headers
            
        Returns:
            TableData object containing the generated content
        """
        # Determine if table has headers
        has_column_headers = random.random() < column_header_probability
        has_row_headers = random.random() < row_header_probability
        
        # Create the table data structure
        table = TableData(
            rows=rows,
            columns=columns,
            has_column_headers=has_column_headers,
            has_row_headers=has_row_headers,
        )
        
        # Determine empty rows and columns
        empty_rows = [False] * rows
        empty_column = None
        
        if not is_normal:
            # Each row has independent chance to be empty
            for i in range(rows):
                if random.random() < empty_row_probability:
                    empty_rows[i] = True
            
            # Still using original logic for empty column
            if random.random() < empty_column_probability:
                empty_column = random.randint(0, columns - 1)
        
        # Generate column headers if needed
        if has_column_headers:
            for j in range(columns):
                # Skip empty columns
                if j == empty_column:
                    continue
                
                # Generate a header (always text)
                header_options = [
                    self.fake.word().capitalize(),
                    " ".join(
                        [word.capitalize() for word in self.fake.words(nb=random.randint(1, 2))]
                    ),
                    self.fake.last_name(),
                    self.fake.currency_name(),
                ]
                table.column_headers[j] = random.choice(header_options)
        
        # Generate row headers if needed
        if has_row_headers:
            for i in range(rows):
                # Skip empty rows
                if empty_rows[i]:
                    continue
                
                # Generate a header (always text or numbers)
                if random.random() < 0.7:
                    # Text header
                    header_options = [
                        self.fake.word().capitalize(),
                        self.fake.last_name(),
                        self.fake.first_name(),
                        self.fake.country(),
                    ]
                    table.row_headers[i] = random.choice(header_options)
                else:
                    # Numeric header (like row numbers)
                    table.row_headers[i] = str(i)
        
        # Generate main table data
        for i in range(rows):
            for j in range(columns):
                # Skip if should be empty
                if empty_rows[i] or j == empty_column:
                    continue
                
                if random.random() < empty_cell_probability:
                    continue  # Leave as None
                else:
                    if random.random() < 0.6:
                        # Determine if we should generate a large number
                        if random.random() < large_number_probability:
                            # Generate large integers of varying lengths
                            digit_count = random.choice([15, 20, 25, 30])
                            text = "".join(
                                [str(random.randint(0, 9)) for _ in range(digit_count)]
                            )
                        elif random.random() < 0.5:
                            text = str(self.fake.random_int(min=0, max=999))
                        else:
                            text = f"{self.fake.pyfloat(left_digits=2, right_digits=2, positive=True):.2f}"
                    else:
                        if random.random() < 0.5:
                            text = "".join(
                                [self.fake.random_letter() for _ in range(random.randint(1, 3))]
                            )
                        else:
                            text = " ".join(self.fake.words(nb=random.randint(1, 5)))
                    table.data[i][j] = text
        
        return table