from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, get_json_object, to_json, struct
from pyspark.sql.streaming import StreamingQuery
from pyspark.sql.types import DateType, DecimalType, StringType
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
        get_json_object(col("value").cast(StringType()), f"$.{OBSERVATION_DATE_COL_NAME}").cast(DateType()).alias(OBSERVATION_DATE_COL_NAME),
        get_json_object(col("value").cast(StringType()), f"$.{fred_id}").cast(DecimalType(15, 0)).alias(fred_id),
    )

    return formatted_df


def main():
    spark_session: SparkSession = SparkSession.builder.appName("FederalReserveCreditCard").getOrCreate()

    # Reading two Kafka topics together
    total_balance_df: DataFrame = get_dataframe_from_fred_kafka_topic(spark_session, TOTAL_BALANCE_FRED_ID)
    revolving_balance_df: DataFrame = get_dataframe_from_fred_kafka_topic(spark_session, REVOLVING_BALANCE_FRED_ID)

    # Joining the DataFrame from the Kafka topics and calculating payment
    result_df: DataFrame = join_credit_card_dataframes(total_balance_df, revolving_balance_df)

    # Write to the console
    # truncate=false ensures the column values in the console output aren't truncated
    console_query: StreamingQuery = result_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .start()

    # Write to a Kafka topic
    # TODO check other options for checkpointLocation as the current value is placeholder proposed by Junie
    write_query: StreamingQuery = result_df.select(
            col("observation_date").cast(StringType()).alias("key"),
            to_json(struct("observation_date", "total_balance", "revolving_balance", "payment")).alias("value")
        ).writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "host.docker.internal:9092") \
        .option("topic", "RCCCBPAYMENT") \
        .option("checkpointLocation", "/tmp/spark-checkpoints/rcccbpayment") \
        .start()

    # Wait for new data on streaming queries for 60 seconds before stopping
    console_query.awaitTermination(timeout=60)
    write_query.awaitTermination(timeout=60)


if __name__ == "__main__":
    main()
