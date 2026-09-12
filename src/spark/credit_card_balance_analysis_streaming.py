from pyspark.sql import DataFrame, SparkSession


def main():
    spark_session: SparkSession = SparkSession.builder.appName("FederalReserveCreditCard").getOrCreate()
    df: DataFrame = spark_session.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "host.docker.internal:9092") \
        .option("subscribe", "input") \
        .load()

    query = df.writeStream \
        .outputMode("append") \
        .format("console") \
        .start()

    query.awaitTermination()


if __name__ == "__main__":
    main()
