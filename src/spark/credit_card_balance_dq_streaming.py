from py4j.java_collections import JavaClass, JavaObject
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, get_json_object
from pyspark.sql.streaming import StreamingQuery
from pyspark.sql.types import DateType, DecimalType, StringType


def evaluate_dq_via_deequ_batch(df: DataFrame, batch_id: int):
    ruleset: str = "Rules = [ColumnExists \"observation_date\", IsComplete \"observation_date\"]"
    # TODO figure out what's the appropriate way to pass a logger
    print(f"Processing DQ rules '{ruleset}' for batch {batch_id} with {df.count()} records")
    spark_session: SparkSession = df.sparkSession
    java_class: JavaClass = spark_session.sparkContext._jvm.com.amazon.deequ.dqdl.EvaluateDataQuality
    result_df_java: JavaObject = java_class.process(df._jdf, ruleset)
    result_df_python: DataFrame = DataFrame(result_df_java, spark_session)
    result_df_python.show(truncate=False)


def main():
    spark_session: SparkSession = SparkSession.builder.appName("FederalReserveCreditCardDQ").getOrCreate()

    df: DataFrame = spark_session.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "host.docker.internal:9092") \
        .option("subscribe", "RCCCBPAYMENT") \
        .option("startingOffsets", "earliest") \
        .load()

    # Cast binary value column back to STRING, parse underlying JSON, cast to appropriate data type and rename to correct column name
    formatted_df: DataFrame = df.select(
        get_json_object(col("value").cast(StringType()), "$.observation_date").cast(DateType()).alias("observation_date"),
        get_json_object(col("value").cast(StringType()), "$.total_balance").cast(DecimalType(15, 0)).alias("total_balance"),
        get_json_object(col("value").cast(StringType()), "$.revolving_balance").cast(DecimalType(15, 0)).alias(
            "revolving_balance"),
        get_json_object(col("value").cast(StringType()), "$.payment").cast(DecimalType(15, 0)).alias(
            "payment"),
    )

    # Convert stream back into batch because com.amazon.deequ.dqdl.EvaluateDataQuality for the underlying Deequ doesn't appear to support Structured Streaming
    write_query: StreamingQuery =  formatted_df.writeStream \
        .foreachBatch(evaluate_dq_via_deequ_batch) \
        .outputMode("append") \
        .start()

    write_query.awaitTermination(timeout=60)

if __name__ == "__main__":
    main()
