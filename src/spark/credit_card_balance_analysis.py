import argparse
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import DateType, DecimalType, StructType, StructField


OBSERVATION_DATE_COL_NAME: str = "observation_date"
PAYMENT_COL_NAME: str = "payment"
TOTAL_BALANCE_COL_NAME: str = "total_balance"
REVOLVING_BALANCE_COL_NAME: str = "revolving_balance"
TOTAL_BALANCE_FRED_ID: str = "RCCCBBALTOT"
REVOLVING_BALANCE_FRED_ID: str = "RCCCBBALREV"


def read_credit_card_files(spark_session: SparkSession, fred_id: str, temp_dir: str) -> DataFrame:
    schema: StructType = StructType([
        StructField(OBSERVATION_DATE_COL_NAME, DateType(), False),
        StructField(fred_id, DecimalType(6, 0), False) # supports 999,999
    ])

    df: DataFrame = spark_session.read.option("header", True).schema(schema).csv(f"{temp_dir}/input/{fred_id}.csv")
    df = df.withColumn(fred_id, (df[fred_id] * 1_000_000_000).cast(DecimalType(15, 0))) # supports 999,999,999,999,999
    return df


def calculate_credit_card_payment(total_balance_df: DataFrame, revolving_balance_df: DataFrame) -> DataFrame:
    joined_df: DataFrame = total_balance_df.join(revolving_balance_df, on=[OBSERVATION_DATE_COL_NAME], how="inner")
    result_df: DataFrame = joined_df.withColumn(PAYMENT_COL_NAME, (joined_df[TOTAL_BALANCE_FRED_ID] - joined_df[REVOLVING_BALANCE_FRED_ID]).cast(DecimalType(15, 0)))
    result_df = result_df.withColumnRenamed(TOTAL_BALANCE_FRED_ID, TOTAL_BALANCE_COL_NAME)
    result_df = result_df.withColumnRenamed(REVOLVING_BALANCE_FRED_ID, REVOLVING_BALANCE_COL_NAME)
    return result_df


def main():
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("--temp_dir")
    args: argparse.Namespace = parser.parse_args()
    temp_dir: str = args.temp_dir

    spark_session: SparkSession = SparkSession.builder.appName("FederalReserveCreditCard").getOrCreate()

    total_balance_df: DataFrame = read_credit_card_files(spark_session, TOTAL_BALANCE_FRED_ID, temp_dir)
    revolving_balance_df: DataFrame = read_credit_card_files(spark_session, REVOLVING_BALANCE_FRED_ID, temp_dir)

    total_balance_df.show()
    revolving_balance_df.show()

    payment_df: DataFrame = calculate_credit_card_payment(total_balance_df, revolving_balance_df)
    payment_df.write.option("header", True).mode("overwrite").parquet(f"{temp_dir}/output/payment")

    spark_session.stop()


if __name__ == "__main__":
    main()
