from pathlib import Path
from pyspark.sql import SparkSession
import pytest
from unittest.mock import patch, MagicMock, ANY

from src.spark.credit_card_balance_analysis import (
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


def test_credit_card_analysis(spark: SparkSession, tmp_path: Path):
    # Set up temporary input files
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    total_balance_file = input_dir / "RCCCBBALTOT.csv"
    total_balance_file.write_text("observation_date,RCCCBBALTOT\n2023-01-01,1000.00\n2023-02-01,1100.00")

    revolving_balance_file = input_dir / "RCCCBBALREV.csv"
    revolving_balance_file.write_text("observation_date,RCCCBBALREV\n2023-01-01,400.00\n2023-02-01,500.00")

    # Run functions
    total_df = read_credit_card_files(spark, "RCCCBBALTOT", str(tmp_path))
    revolving_df = read_credit_card_files(spark, "RCCCBBALREV", str(tmp_path))
    payment_df = calculate_credit_card_payment(total_df, revolving_df)

    # Verify results
    assert payment_df.count() == 2
    results = payment_df.orderBy("observation_date").collect()
    assert results[0]["payment"] == 600.00
    assert results[1]["payment"] == 600.00


@patch("src.spark.credit_card_balance_analysis.calculate_credit_card_payment")
@patch("src.spark.credit_card_balance_analysis.read_credit_card_files")
def test_main(
        mock_read_credit_card_files: MagicMock,
        mock_calculate_credit_card_payment: MagicMock,
        monkeypatch,
        spark: SparkSession):
    # ARRANGE
    monkeypatch.setattr("sys.argv", ["credit_card_balance_analysis.py", "--temp_dir", "/temp"])
    # TODO override the spark_session created in the code with the fixture
    # TODO pass DataFrame between the methods

    # ACT
    main()

    # ASSERT
    mock_read_credit_card_files.assert_any_call(ANY, "RCCCBBALTOT", "/temp")
    mock_read_credit_card_files.assert_any_call(ANY, "RCCCBBALREV", "/temp")
    mock_calculate_credit_card_payment.assert_called_once()
