import pandas as pd
import pathlib


class CSVLoader:
    def __init__(self, path: pathlib.Path, sep: str = ";") -> None:
        self.path = path.absolute()
        self.sep = sep

    def __call__(self) -> pd.DataFrame:
        df = pd.read_csv(self.path, sep=self.sep)
        return df
