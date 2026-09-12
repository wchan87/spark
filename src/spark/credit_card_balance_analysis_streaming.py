from pyspark.sql import DataFrame, SparkSession


def main():
    spark_session: SparkSession = SparkSession.builder.appName("FederalReserveCreditCard").getOrCreate()
    df: DataFrame = spark_session.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "host.docker.internal:9092") \
        .option("subscribe", "RCCCBBALTOT") \
        .option("startingOffsets", "earliest") \
        .load()

    # Cast binary key and value columns to string for human-readable console output
    formatted_df = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)", "topic", "partition", "offset", "timestamp", "timestampType")

    # truncate=false ensures the column values in the console output aren't truncated
    query = formatted_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .start()

    # Wait for 60 seconds before stopping
    query.awaitTermination(timeout=60)


if __name__ == "__main__":
    main()
