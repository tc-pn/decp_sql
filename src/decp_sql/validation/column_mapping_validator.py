from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ValidationError:
    timestamp: datetime
    rule: str
    message: str


class ColumnMappingValidator:
    def __init__(self, mapping: dict[str, str]) -> None:
        self.mapping = mapping
        self.errors: list[ValidationError] = []

    def __call__(self) -> bool:
        self.errors.clear()
        self._validate_unique_destinations()
        return not self.errors

    def _validate_unique_destinations(self) -> None:
        destination_to_sources = {
            destination: [] for destination in self.mapping.values()
        }
        for source, destination in self.mapping.items():
            destination_to_sources[destination].append(source)

        for destination, sources in destination_to_sources.items():
            if len(sources) == 1:
                continue
            self.errors.append(
                ValidationError(
                    timestamp=datetime.now(timezone.utc),
                    rule="unique_destination_columns",
                    message=(f"Columns {sources} map to '{destination}'."),
                )
            )
