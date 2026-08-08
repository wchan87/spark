from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import DateType, DecimalType, StructType, StructField


def read_credit_card_total_balance(spark_session: SparkSession) -> DataFrame:
    schema: StructType = StructType([
        StructField("observation_date", DateType(), False),
        StructField("RCCCBBALTOT", DecimalType(), False)
    ])

    df: DataFrame = spark_session.read \
        .option("header", True) \
        .schema(schema) \
        .csv("/home/hadoop/temp/input/RCCCBBALTOT.csv")
    return df


def read_credit_card_revolving_balance(spark_session: SparkSession) -> DataFrame:
    schema: StructType = StructType([
        StructField("observation_date", DateType(), False),
        StructField("RCCCBBALREV", DecimalType(), False)
    ])

    df: DataFrame = spark_session.read \
        .option("header", True) \
        .schema(schema) \
        .csv("/home/hadoop/temp/input/RCCCBBALREV.csv")
    return df


def calculate_credit_card_payment(total_balance_df: DataFrame, revolving_balance_df: DataFrame) -> DataFrame:
    joined_df: DataFrame = total_balance_df.join(revolving_balance_df, on=["observation_date"], how="inner")
    result_df: DataFrame = joined_df.withColumn("payment", joined_df["RCCCBBALTOT"] - joined_df["RCCCBBALREV"])
    result_df = result_df.withColumnRenamed('RCCCBBALTOT', 'total_balance')
    result_df = result_df.withColumnRenamed('RCCCBBALREV', 'revolving_balance')
    return result_df


def write_payment(payment_df: DataFrame) -> None:
    payment_df.write \
        .option("header", True) \
        .mode("overwrite") \
        .csv("/home/hadoop/temp/output/payment")


def main():
    spark_session: SparkSession = SparkSession\
        .builder\
        .appName("FederalReserveCreditCard")\
        .getOrCreate()

    total_balance_df: DataFrame = read_credit_card_total_balance(spark_session)
    revolving_balance_df: DataFrame = read_credit_card_revolving_balance(spark_session)

    total_balance_df.show()
    revolving_balance_df.show()

    payment_df: DataFrame = calculate_credit_card_payment(total_balance_df, revolving_balance_df)
    write_payment(payment_df)

    spark_session.stop()


if __name__ == "__main__":
    main()
