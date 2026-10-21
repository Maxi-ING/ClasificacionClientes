import pandas as pd
import pytest


@pytest.fixture
def transactions():
    """Dos productos en un pedido y una cancelación posterior del mismo cliente."""
    return pd.DataFrame(
        {
            "Invoice": ["100", "100", "101", "C102"],
            "StockCode": ["A", "B", "A", "A"],
            "Description": ["Producto A", "Producto B", "Producto A", "Producto A"],
            "Quantity": [2, 1, 1, -1],
            "InvoiceDate": pd.to_datetime(["2011-08-01", "2011-08-01", "2011-08-20", "2011-08-21"]),
            "Price": [10, 5, 10, 10],
            "Customer ID": [123, 123, 456, 123],
            "Country": ["United Kingdom"] * 4,
            "source_sheet": ["one"] * 4,
        }
    )
