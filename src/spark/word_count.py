import sys
from operator import add
from pyspark.sql import SparkSession


def word_count(spark_session: SparkSession, file_path: str):
    lines = spark_session.read.text(file_path).rdd.map(lambda r: r[0])
    counts = lines.flatMap(lambda x: x.split(' ')) \
                  .map(lambda x: (x, 1)) \
                  .reduceByKey(add)
    return counts.collect()


def main():
    spark_session: SparkSession = SparkSession.builder.appName("PythonWordCount").getOrCreate()

    output = word_count(spark_session, sys.argv[1])
    for (word, count) in output:
        print("%s: %i" % (word, count))

    spark_session.stop()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: word_count <file>", file=sys.stderr)
        sys.exit(-1)
    main()
