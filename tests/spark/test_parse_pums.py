from open_data_contract_standard.model import OpenDataContractStandard, SchemaObject
from pathlib import Path
from pyspark.sql import SparkSession, DataFrame, Column
import pytest
from _pytest.monkeypatch import MonkeyPatch
from unittest.mock import patch, MagicMock


from src.spark.parse_pums import (
    get_fixed_width_record_configs,
    get_columns,
    main,
    FixedWidthRecordConfig
)


@pytest.fixture
def data_contract() -> OpenDataContractStandard:
    data_contract: OpenDataContractStandard = OpenDataContractStandard.from_file("src/odcs/pums_census_2000_1_percent.yaml")
    if data_contract.schema_:
        schema: SchemaObject = SchemaObject()
        schema.name = "test_record"
        data_contract.schema_.append(schema) # added empty schema object to test edge case where it's skipped
    return data_contract


@pytest.fixture
def raw_dataframe(spark: SparkSession) -> DataFrame:
    return spark.read.text("tests/data/pums_36.dat")


@pytest.fixture
def fixed_width_record_configs(data_contract: OpenDataContractStandard) -> list[FixedWidthRecordConfig]:
    return get_fixed_width_record_configs(data_contract)


def test_get_fixed_width_record_configs(
        data_contract: OpenDataContractStandard
    ):
    # ACT
    record_configs: list[FixedWidthRecordConfig] = get_fixed_width_record_configs(data_contract)

    # ASSERT
    assert len(record_configs) == 2
    assert record_configs[0].record_name == "housing_unit_record"
    assert record_configs[1].record_name == "person_record"


def test_get_columns(
        raw_dataframe: DataFrame,
        fixed_width_record_configs: list[FixedWidthRecordConfig]
    ):
    # ACT
    housing_unit_record_columns: list[Column] = get_columns(raw_dataframe, fixed_width_record_configs[0])
    person_record_columns: list[Column] = get_columns(raw_dataframe, fixed_width_record_configs[1])

    # ASSERT
    assert len(housing_unit_record_columns) == 113
    assert len(person_record_columns) == 164


@patch("src.spark.parse_pums.get_fixed_width_record_configs")
@patch("src.spark.parse_pums.OpenDataContractStandard.from_file")
@patch("src.spark.parse_pums.SparkSession")
def test_main(
        mock_spark_session: MagicMock,
        mock_from_file: MagicMock,
        mock_get_fixed_width_record_configs: MagicMock,
        tmp_path: Path,
        monkeypatch: MonkeyPatch,
        spark: SparkSession,
        data_contract: OpenDataContractStandard,
        fixed_width_record_configs: list[FixedWidthRecordConfig],
        raw_dataframe: DataFrame):
    # ARRANGE
    monkeypatch.setattr("sys.argv", ["parse_pums.py", "--temp_dir", str(tmp_path), "--odcs_dir", "src/odcs", "--pums_file", "input/pums_36.dat"])
    # Intercept the spark_session created in the code with the fixture
    mock_spark_session.builder.appName.return_value.getOrCreate.return_value = spark
    mock_from_file.return_value = data_contract
    mock_get_fixed_width_record_configs.return_value = fixed_width_record_configs
    # Copy the contents of the test file into the temp directory
    d = tmp_path / "input"
    d.mkdir()
    p = d / "pums_36.dat"
    with open("tests/data/pums_36.dat", "r") as file:
        content = file.read()
        p.write_text(content)

    # ACT
    main()

    # ASSERT
    mock_get_fixed_width_record_configs.assert_called_once_with(data_contract)
    mock_from_file.assert_called_once_with("src/odcs/pums_census_2000_1_percent.yaml")
    # TODO figure out how to verify the output dataframes which should be written into the temp directory
