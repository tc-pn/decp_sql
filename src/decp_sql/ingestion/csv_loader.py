import pandas as pd
import pathlib


class CSVLoader:
    """Load de CSV file into a DataFrame."""

    def __init__(self, path: pathlib.Path, sep: str = ";") -> None:
        """Initialize the CSV loader.

        Args:
            path: Path to the CSV file.
            sep: Field separator used in the CSV file.
        """
        self.path = path.absolute()
        self.sep = sep

    def __call__(self) -> pd.DataFrame:
        """Load the configured CSV file.

        Returns:
            A pandas DataFrame containing the CSV data.
        """
        df = pd.read_csv(self.path, sep=self.sep)
        return df
