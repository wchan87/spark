import urllib.request
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructField, StructType, DateType, DecimalType

# Large Bank Consumer Credit Card Balances: Total Balances (RCCCBBALTOT)
# Large Bank Consumer Credit Card Balances: Revolving Balances Only (RCCCBBALREV)
# Large Bank Consumer Credit Card Balances: 90 or More Days Past Due Rates: Accounts Based (RCCCBACTDPD90P)
# Large Bank Consumer Credit Card Balances: 30 or More Days Past Due Rates: Accounts Based (RCCCBACTDPD30P)
# Large Bank Consumer Credit Card Balances: Share of Accounts Making the Minimum Payment (RCCCBSHRMIN)
# Large Bank Consumer Credit Card Balances: Share of Accounts Making Greater Than the Minimum Payment but Less Than the Full Balance (RCCCBSHRGTMINLTMAX)
# Large Bank Consumer Credit Card Balances: Share of Accounts Making the Full Balance Payment (RCCCBSHRFULL)
TOTAL_BALANCE_FRED_ID: str = "RCCCBBALTOT"
REVOLVING_BALANCE_FRED_ID: str = "RCCCBBALREV"
OBSERVATION_DATE_COL_NAME: str = "observation_date"
PAYMENT_COL_NAME: str = "payment"
TOTAL_BALANCE_COL_NAME: str = "total_balance"
REVOLVING_BALANCE_COL_NAME: str = "revolving_balance"
START_DATE: str = "2012-07-01"
END_DATE: str = "2026-01-01"


def get_large_bank_consumer_credit_card_balances(spark: SparkSession, temp_dir: str, fred_id: str) -> DataFrame:
    url: str = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={fred_id}&cosd={START_DATE}&coed={END_DATE}"
    temp_path: str = f"{temp_dir}/{fred_id}.csv"
    urllib.request.urlretrieve(url, temp_path)
    schema: StructType = StructType([
        StructField(OBSERVATION_DATE_COL_NAME, DateType(), False),
        StructField(fred_id, DecimalType(), False)
    ])
    df: DataFrame = spark.read.csv(temp_path, schema=schema, header=True)
    return df


def calculate_credit_card_payment(spark: SparkSession, temp_dir: str) -> DataFrame:
    total_balance_df: DataFrame = get_large_bank_consumer_credit_card_balances(spark, temp_dir, TOTAL_BALANCE_FRED_ID)
    revolving_balance_df: DataFrame = get_large_bank_consumer_credit_card_balances(spark, temp_dir, REVOLVING_BALANCE_FRED_ID)
    joined_df: DataFrame = total_balance_df.join(revolving_balance_df, on=[OBSERVATION_DATE_COL_NAME], how="inner")
    result_df: DataFrame = joined_df.withColumn(PAYMENT_COL_NAME, joined_df[TOTAL_BALANCE_FRED_ID] - joined_df[REVOLVING_BALANCE_FRED_ID])
    result_df = result_df.withColumnRenamed(TOTAL_BALANCE_FRED_ID, TOTAL_BALANCE_COL_NAME)
    result_df = result_df.withColumnRenamed(REVOLVING_BALANCE_FRED_ID, REVOLVING_BALANCE_COL_NAME)
    return result_df
