from decp_sql.validation.column_mapping_validator import ColumnMappingValidator


def test_valid_mapping():
    mapping = {
        "codeCPV": "code_cpv",
        "dateNotification": "date_notification",
    }

    validator = ColumnMappingValidator(mapping)

    assert validator()
    assert validator.errors == []


MAPPING_PATATE = {
    "patatePatate": "patate_patate",
    "patate_Patate": "patate_patate",
}


def test_duplicate_destination_is_invalid():

    validator = ColumnMappingValidator(MAPPING_PATATE)

    assert not validator()

    assert len(validator.errors) == 1
    assert validator.errors[0].rule == "unique_destination_columns"


def test_validation_clears_previous_errors():
    validator = ColumnMappingValidator(MAPPING_PATATE)

    assert not validator()
    assert len(validator.errors) == 1

    validator.mapping = {
        "fooBar": "foo_bar",
    }

    assert validator()
    assert validator.errors == []
