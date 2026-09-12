from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, get_json_object
from fred.utility import OBSERVATION_DATE_COL_NAME, TOTAL_BALANCE_FRED_ID, REVOLVING_BALANCE_FRED_ID, join_credit_card_dataframes


def get_dataframe_from_fred_kafka_topic(spark_session: SparkSession, fred_id: str) -> DataFrame:
    df: DataFrame = spark_session.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "host.docker.internal:9092") \
        .option("subscribe", fred_id) \
        .option("startingOffsets", "earliest") \
        .load()

    # Cast binary value column back to STRING, parse underlying JSON, cast to appropriate data type and rename to correct column name
    formatted_df: DataFrame = df.select(
        get_json_object(col("value").cast("STRING"), f"$.{OBSERVATION_DATE_COL_NAME}").cast("DATE").alias(OBSERVATION_DATE_COL_NAME),
        get_json_object(col("value").cast("STRING"), f"$.{fred_id}").cast("DECIMAL(15, 0)").alias(fred_id),
    )

    return formatted_df


def main():
    spark_session: SparkSession = SparkSession.builder.appName("FederalReserveCreditCard").getOrCreate()

    # Reading two Kafka topics together
    total_balance_df: DataFrame = get_dataframe_from_fred_kafka_topic(spark_session, TOTAL_BALANCE_FRED_ID)
    revolving_balance_df: DataFrame = get_dataframe_from_fred_kafka_topic(spark_session, REVOLVING_BALANCE_FRED_ID)

    # Joining the DataFrame from the Kafka topics and calculating payment
    result_df: DataFrame = join_credit_card_dataframes(total_balance_df, revolving_balance_df)

    # truncate=false ensures the column values in the console output aren't truncated
    query = result_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .start()

    # Wait for new data on streaming query for 60 seconds before stopping
    query.awaitTermination(timeout=60)


if __name__ == "__main__":
    main()
