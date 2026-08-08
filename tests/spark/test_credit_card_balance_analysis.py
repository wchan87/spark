import os
from pathlib import Path
import pytest
from pyspark.sql import SparkSession
from src.spark.credit_card_balance_analysis import (
    read_credit_card_total_balance,
    read_credit_card_revolving_balance,
    calculate_credit_card_payment,
    write_payment
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
    total_df = read_credit_card_total_balance(spark, str(tmp_path))
    revolving_df = read_credit_card_revolving_balance(spark, str(tmp_path))
    payment_df = calculate_credit_card_payment(total_df, revolving_df)
    write_payment(payment_df, str(tmp_path))

    # Verify results
    assert payment_df.count() == 2
    results = payment_df.orderBy("observation_date").collect()
    assert results[0]["payment"] == 600.00
    assert results[1]["payment"] == 600.00
