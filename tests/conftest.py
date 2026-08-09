from datetime import datetime
from decimal import Decimal
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, DateType, StructField, DecimalType
import pytest


from src.spark.credit_card_balance_analysis import (
    OBSERVATION_DATE_COL_NAME,
    TOTAL_BALANCE_FRED_ID,
    REVOLVING_BALANCE_FRED_ID,
    TOTAL_BALANCE_COL_NAME,
    REVOLVING_BALANCE_COL_NAME,
    PAYMENT_COL_NAME
)

# scope set to "module" as it causes "java.lang.IllegalStateException: No active or default Spark session found" if scope is "session"
@pytest.fixture(scope="module")
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

