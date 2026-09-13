from py4j.java_collections import JavaClass, JavaObject
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, get_json_object
from pyspark.sql.types import DateType, DecimalType, StringType


def evaluate_dq_via_deequ(spark_session: SparkSession, df: DataFrame, ruleset: str) -> DataFrame:
    java_class: JavaClass = spark_session.sparkContext._jvm.com.amazon.deequ.dqdl.EvaluateDataQuality
    result_df_java: JavaObject = java_class.process(df._jdf, ruleset)
    result_df_python: DataFrame = DataFrame(result_df_java, spark_session)
    result_df_python.show()
    return result_df_python


def main():
    spark_session: SparkSession = SparkSession.builder.appName("FederalReserveCreditCardDQ").getOrCreate()

    # readStream -> read because com.amazon.deequ.dqdl.EvaluateDataQuality for the underlying Deequ doesn't appear to support Structured Streaming
    df: DataFrame = spark_session.read \
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

    ruleset: str = "Rules = [ColumnExists \"observation_date\", IsComplete \"observation_date\"]"
    evaluate_dq_via_deequ(spark_session, formatted_df, ruleset)


if __name__ == "__main__":
    main()
