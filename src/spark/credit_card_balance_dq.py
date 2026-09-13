import argparse
from py4j.java_collections import JavaClass, JavaObject
from pyspark.sql import DataFrame, SparkSession


def evaluate_dq_via_deequ(spark_session: SparkSession, df: DataFrame, ruleset: str) -> DataFrame:
    java_class: JavaClass = spark_session.sparkContext._jvm.com.amazon.deequ.dqdl.EvaluateDataQuality
    result_df_java: JavaObject = java_class.process(df._jdf, ruleset)
    result_df_python: DataFrame = DataFrame(result_df_java, spark_session)
    result_df_python.show()
    return result_df_python


def main():
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("--temp_dir")
    args: argparse.Namespace = parser.parse_args()
    temp_dir: str = args.temp_dir

    spark_session: SparkSession = SparkSession.builder.appName("FederalReserveCreditCardDQ").getOrCreate()
    df: DataFrame = spark_session.read.parquet(f"{temp_dir}/output/payment")
    ruleset: str = "Rules = [ColumnExists \"observation_date\", IsComplete \"observation_date\"]"
    evaluate_dq_via_deequ(spark_session, df, ruleset)


if __name__ == "__main__":
    main()
