from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ValidationError:
    """Describe a validation error detected during data processing."""

    timestamp: datetime
    rule: str
    message: str


class ColumnMappingValidator:
    """Validate the source-to-destination column mapping integrity."""

    def __init__(self, mapping: dict[str, str]) -> None:
        """Initialize the validator.

        Args:
            mapping: Mapping from source column names to destination
                column names.
        """
        self.mapping = mapping
        self.errors: list[ValidationError] = []

    def __call__(self) -> bool:
        """Validate the configured column mapping.

        Previous validation errors are cleared before running the
        validation rules.

        Returns:
            True if the mapping is valid, otherwise False.
        """
        self.errors.clear()
        self._validate_unique_destinations()
        return not self.errors

    def _validate_unique_destinations(self) -> None:
        """Check that each destination column has a unique source column."""
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
