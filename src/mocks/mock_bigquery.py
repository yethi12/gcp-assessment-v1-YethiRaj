import duckdb
import pandas as pd
from pathlib import Path
from typing import Optional, Any, List

class MockRow:
    def __init__(self, data: dict):
        self._data = data
        for k, v in data.items():
            setattr(self, k, v)

    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def __getitem__(self, item):
        return self._data[item]

class MockRowIterator:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self._rows = [MockRow(row.to_dict()) for _, row in df.iterrows()]
        self.total_rows = len(self._rows)

    def __iter__(self):
        return iter(self._rows)

    def to_dataframe(self) -> pd.DataFrame:
        return self.df

class MockQueryJob:
    def __init__(self, df: pd.DataFrame):
        self._df = df

    def result(self) -> MockRowIterator:
        return MockRowIterator(self._df)

    def to_dataframe(self) -> pd.DataFrame:
        return self._df

class MockBigQueryClient:
    """Mock BigQuery client powered by local DuckDB engine."""
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = str(db_path) if db_path else ":memory:"
        self.con = duckdb.connect(self.db_path)

    def query(self, query_string: str) -> MockQueryJob:
        try:
            df = self.con.execute(query_string).df()
            return MockQueryJob(df)
        except Exception as e:
            # Return empty dataframe on syntax edge cases or table creation
            return MockQueryJob(pd.DataFrame())

    def load_table_from_dataframe(self, dataframe: pd.DataFrame, destination: str):
        table_name = destination.split(".")[-1]
        self.con.register("temp_load_df", dataframe)
        self.con.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM temp_load_df")

    def close(self):
        self.con.close()
