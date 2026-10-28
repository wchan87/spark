from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType


def main():
    spark_session: SparkSession = SparkSession.builder.appName("FederalReserveCreditCardIceberg").getOrCreate()
    spark_session.sql("CREATE DATABASE IF NOT EXISTS local_catalog.fred")
    data: list = [("Alice", 1), ("Bob", 2)]
    schema = StructType([
        StructField("name", StringType(), True),
        StructField("age", IntegerType(), True)
    ])
    df: DataFrame = spark_session.createDataFrame(data, schema)
    df.writeTo("local_catalog.fred.customer").tableProperty("format-version", "2").createOrReplace()
    spark_session.stop()


if __name__ == "__main__":
    main()
