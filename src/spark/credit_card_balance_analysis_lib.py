from pyspark.sql import DataFrame, SparkSession
from fred.utility import calculate_credit_card_payment


def main():
    spark_session: SparkSession = SparkSession.builder.appName("FederalReserveCreditCard").getOrCreate()
    result_df: DataFrame = calculate_credit_card_payment(spark_session, "/tmp")
    result_df.show()


if __name__ == "__main__":
    main()
