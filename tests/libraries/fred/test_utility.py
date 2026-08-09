from pandas import DataFrame
from pandas.testing import assert_frame_equal
from pathlib import Path
from pyspark.sql import SparkSession
from unittest.mock import patch, MagicMock


from src.libraries.fred.utility import (
    START_DATE,
    END_DATE,
    TOTAL_BALANCE_FRED_ID,
    REVOLVING_BALANCE_FRED_ID,
    get_large_bank_consumer_credit_card_balances,
    calculate_credit_card_payment
)


@patch("urllib.request.urlretrieve")
def test_get_large_bank_consumer_credit_card_balances(
        mock_urlretrieve: MagicMock,
        tmp_path: Path,
        spark: SparkSession,
        total_balance_dataframe: DataFrame
):
    # ARRANGE
    total_balance_file: Path = tmp_path / "RCCCBBALTOT.csv"
    total_balance_file.write_text("observation_date,RCCCBBALTOT\n2023-01-01,1000.00\n2023-02-01,1100.00")

    # ACT
    total_balance_df: DataFrame = get_large_bank_consumer_credit_card_balances(spark, str(tmp_path), TOTAL_BALANCE_FRED_ID)

    # ASSERT
    mock_urlretrieve.assert_called_once_with(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={TOTAL_BALANCE_FRED_ID}&cosd={START_DATE}&coed={END_DATE}", str(total_balance_file))
    assert_frame_equal(total_balance_df.toPandas(), total_balance_dataframe.toPandas())


@patch("src.libraries.fred.utility.get_large_bank_consumer_credit_card_balances")
def test_calculate_credit_card_payment(
        mock_get_large_bank_consumer_credit_card_balances: MagicMock,
        spark: SparkSession,
        total_balance_dataframe: DataFrame,
        revolving_balance_dataframe: DataFrame,
        payment_dataframe: DataFrame):
    # ARRANGE
    mock_get_large_bank_consumer_credit_card_balances.side_effect = [
        total_balance_dataframe,
        revolving_balance_dataframe
    ]

    # ACT
    payment_df: DataFrame = calculate_credit_card_payment(spark, "/tmp")

    # ASSERT
    mock_get_large_bank_consumer_credit_card_balances.assert_any_call(spark, "/tmp", TOTAL_BALANCE_FRED_ID)
    mock_get_large_bank_consumer_credit_card_balances.assert_any_call(spark, "/tmp", REVOLVING_BALANCE_FRED_ID)
    assert_frame_equal(payment_df.toPandas(), payment_dataframe.toPandas())
