from datetime import datetime
from decimal import Decimal
from pandas.testing import assert_frame_equal
from pathlib import Path
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, DateType, StructField, DecimalType
import pytest
from _pytest.monkeypatch import MonkeyPatch
from unittest.mock import patch, MagicMock


from src.spark.credit_card_balance_analysis import (
    OBSERVATION_DATE_COL_NAME,
    TOTAL_BALANCE_FRED_ID,
    REVOLVING_BALANCE_FRED_ID,
    TOTAL_BALANCE_COL_NAME,
    REVOLVING_BALANCE_COL_NAME,
    PAYMENT_COL_NAME,
    read_credit_card_files,
    calculate_credit_card_payment,
    main
)


@pytest.fixture(scope="session")
def spark():
    spark = SparkSession.builder \
        .master("local[1]") \
        .appName("pytest-pyspark-local-testing") \
        .getOrCreate()
    yield spark
    spark.stop()


@pytest.fixture
def total_balance_dataframe(spark: SparkSession) -> DataFrame:
    schema: StructType = StructType([
        StructField(OBSERVATION_DATE_COL_NAME, DateType(), False),
        StructField(TOTAL_BALANCE_FRED_ID, DecimalType(), False)
    ])
    data = [
        (datetime(2023, 1, 1), Decimal(1000.00)),
        (datetime(2023, 2, 1), Decimal(1100.00))
    ]
    return spark.createDataFrame(data, schema)


@pytest.fixture
def revolving_balance_dataframe(spark: SparkSession) -> DataFrame:
    schema: StructType = StructType([
        StructField(OBSERVATION_DATE_COL_NAME, DateType(), False),
        StructField(REVOLVING_BALANCE_FRED_ID, DecimalType(), False)
    ])
    data = [
        (datetime(2023, 1, 1), Decimal(400.00)),
        (datetime(2023, 2, 1), Decimal(500.00))
    ]
    return spark.createDataFrame(data, schema)


@pytest.fixture
def payment_dataframe(spark: SparkSession) -> DataFrame:
    schema: StructType = StructType([
        StructField(OBSERVATION_DATE_COL_NAME, DateType(), False),
        StructField(TOTAL_BALANCE_COL_NAME, DecimalType(), False),
        StructField(REVOLVING_BALANCE_COL_NAME, DecimalType(), False),
        StructField(PAYMENT_COL_NAME, DecimalType(), False)
    ])
    data = [
        (datetime(2023, 1, 1), Decimal(1000.00), Decimal(400.00), Decimal(600.00)),
        (datetime(2023, 2, 1), Decimal(1100.00), Decimal(500.00), Decimal(600.00))
    ]
    return spark.createDataFrame(data, schema)


def test_credit_card_analysis(
        spark: SparkSession,
        tmp_path: Path,
        total_balance_dataframe: DataFrame,
        revolving_balance_dataframe: DataFrame,
        payment_dataframe: DataFrame):
    # Set up temporary input files
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    total_balance_file: Path = input_dir / "RCCCBBALTOT.csv"
    total_balance_file.write_text("observation_date,RCCCBBALTOT\n2023-01-01,1000.00\n2023-02-01,1100.00")

    revolving_balance_file: Path = input_dir / "RCCCBBALREV.csv"
    revolving_balance_file.write_text("observation_date,RCCCBBALREV\n2023-01-01,400.00\n2023-02-01,500.00")

    # Run functions
    total_df: DataFrame = read_credit_card_files(spark, "RCCCBBALTOT", str(tmp_path))
    revolving_df: DataFrame = read_credit_card_files(spark, "RCCCBBALREV", str(tmp_path))
    payment_df: DataFrame = calculate_credit_card_payment(total_df, revolving_df)

    # Verify results
    # used instead of pyspark.testing.assertDataFrameEqual because of dependency issue not resolved until Spark 4.0
    assert_frame_equal(total_df.toPandas(), total_balance_dataframe.toPandas())
    assert_frame_equal(revolving_df.toPandas(), revolving_balance_dataframe.toPandas())
    assert_frame_equal(payment_df.toPandas(), payment_dataframe.toPandas())


@patch("src.spark.credit_card_balance_analysis.calculate_credit_card_payment")
@patch("src.spark.credit_card_balance_analysis.read_credit_card_files")
@patch("src.spark.credit_card_balance_analysis.SparkSession")
def test_main(
        mock_spark_session: MagicMock,
        mock_read_credit_card_files: MagicMock,
        mock_calculate_credit_card_payment: MagicMock,
        tmp_path: Path,
        monkeypatch: MonkeyPatch,
        spark: SparkSession,
        total_balance_dataframe: DataFrame,
        revolving_balance_dataframe: DataFrame,
        payment_dataframe: DataFrame):
    # ARRANGE
    monkeypatch.setattr("sys.argv", ["credit_card_balance_analysis.py", "--temp_dir", str(tmp_path)])
    # Intercept the spark_session created in the code with the fixture
    mock_spark_session.builder.appName.return_value.getOrCreate.return_value = spark
    # Mock DataFrames to pass between methods
    mock_read_credit_card_files.side_effect = [total_balance_dataframe, revolving_balance_dataframe]
    mock_calculate_credit_card_payment.return_value = payment_dataframe

    # ACT
    main()

    # ASSERT
    mock_read_credit_card_files.assert_any_call(spark, "RCCCBBALTOT", str(tmp_path))
    mock_read_credit_card_files.assert_any_call(spark, "RCCCBBALREV", str(tmp_path))
    mock_calculate_credit_card_payment.assert_called_once_with(total_balance_dataframe, revolving_balance_dataframe)
