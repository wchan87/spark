from pyspark.sql import DataFrame, SparkSession


def main():
    spark_session: SparkSession = SparkSession.builder.appName("FederalReserveCreditCard").getOrCreate()
    # TODO need to confirm why connection isn't working
    # 26/09/11 01:34:11 INFO NetworkClient: [AdminClient clientId=adminclient-3] Node 1 disconnected.
    # 26/09/11 01:34:11 WARN NetworkClient: [AdminClient clientId=adminclient-3] Connection to node 1 (localhost/127.0.0.1:9092) could not be established. Node may not be available.
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
