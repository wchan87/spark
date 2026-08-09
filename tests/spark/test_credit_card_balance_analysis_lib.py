from unittest.mock import patch, MagicMock
from pandas import DataFrame
from pyspark.sql import SparkSession
import sys


# Intercept the import of fred before it happens in src.spark.credit_card_balance_analysis_lib
sys.modules["fred"] = MagicMock()
sys.modules["fred.utility"] = MagicMock()
from src.spark.credit_card_balance_analysis_lib import (
    main
)


@patch("src.spark.credit_card_balance_analysis_lib.calculate_credit_card_payment")
@patch("src.spark.credit_card_balance_analysis_lib.SparkSession")
def test_main(
        mock_spark_session: MagicMock,
        mock_calculate_credit_card_payment: MagicMock,
        spark: SparkSession,
        payment_dataframe: DataFrame
    ):
    # ARRANGE
    # Intercept the spark_session created in the code with the fixture
    mock_spark_session.builder.appName.return_value.getOrCreate.return_value = spark
    mock_calculate_credit_card_payment.return_value = payment_dataframe

    # ACT
    main()

    # ASSERT
    mock_calculate_credit_card_payment.assert_called_once_with(spark, "/tmp")
