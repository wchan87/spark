# Apache Spark

## Apache Spark Docker

From [DockerHub > spark](https://hub.docker.com/_/spark), we will use Spark 3.5.4 as the starting point:
```bash
docker pull spark:3.5.4-scala2.12-java17-python3-ubuntu
```

### Apache Spark Run

To run Apache Spark locally using Docker against [word_count.py](/src/spark/word_count.py), follow these steps:
1. Disable Windows path resolution if running via Git Bash
   ```bash
   export MSYS_NO_PATHCONV=1
   ```
2. Set up workspace and script locations
   ```bash
   SCRIPT_FILE_NAME=word_count.py
   SCRIPT_ARGS=/opt/spark/work-dir/$SCRIPT_FILE_NAME
   ```
3. Run the container with [spark-submit](https://spark.apache.org/docs/latest/submitting-applications.html)
   ```bash
    docker run -it --rm --name spark \
        -v $PWD/src/spark/:/opt/spark/work-dir/ \
        spark:3.5.4-scala2.12-java17-python3-ubuntu \
        /opt/spark/bin/spark-submit /opt/spark/work-dir/$SCRIPT_FILE_NAME $SCRIPT_ARGS
   ```
   * `SCRIPT_ARGS` is the same as the script location because we're parsing the lines from the same script to perform word count

### Apache Spark Docker Testing

Refer to [pytest option](https://spark.apache.org/docs/latest/api/python/getting_started/testing_pyspark.html#Option-3:-Using-Pytest) for how we can test Spark code. It isn't straightforward to install `pytest` on the Docker container to run the [tests/spark/](/tests/spark/) similar to [AWS Glue](aws-glue.md#aws-glue-docker-testing). The error thrown when you attempt to run a similar command to `python3 -m pytest` is as follows:
```
WARNING: The directory '/home/spark/.cache/pip' or its parent directory is not owned or is not writable by the current user. The cache has been disabled. Check the permissions and owner of that directory. If executing pip with sudo, you should use sudo's -H flag.
Defaulting to user installation because normal site-packages is not writeable
```

Enable `-u 0` to switch user to `root` to enable `pip install` to work (which is a similar approach as [Testing pyspark with pytest](https://garybake.com/pyspark_pytest.html))
```bash
docker run -it --rm --name spark -u 0 \
    -v $PWD/:/opt/spark/work-dir/ \
    spark:3.5.4-scala2.12-java17-python3-ubuntu \
    bash -c "python3 -m pip install pytest \"pyspark==3.5.4\" \"pandas==2.3.3\" py4j && python3 -m pytest --disable-warnings"
```
* **Note**: Be careful with `-u 0` on Windows when mounting a sensitive folder due to [this](https://docs.docker.com/desktop/setup/install/windows-permission-requirements/#privileged-helper)
   > The privileged helper `com.docker.service` is a Windows service which runs in the background with `SYSTEM` privileges.

### Federal Reserve Data Analytics

Refer to the similar [AWS Glue](/docs/aws-glue.md#federal-reserve-data-analytics) instructions for the initial setup
1. Set up workspace and script locations
   ```bash
   SCRIPT_FILE_NAME=credit_card_balance_analysis.py
   SPARK_SUBMIT_ARGS=
   SCRIPT_ARGS="--temp_dir /opt/spark/temp"
   ```
2. Run the container with [spark-submit](https://spark.apache.org/docs/latest/submitting-applications.html)
   ```bash
   docker run -it --rm --name spark \
       -v $PWD/src/spark/:/opt/spark/work-dir/ \
       -v $PWD/temp/:/opt/spark/temp/ \
       spark:3.5.4-scala2.12-java17-python3-ubuntu \
       /opt/spark/bin/spark-submit /opt/spark/work-dir/$SCRIPT_FILE_NAME $SCRIPT_ARGS
   ```

### Federal Reserve Data Analytics with Library

Refer to the similar [AWS Glue](/docs/aws-glue.md#federal-reserve-data-analytics-with-library) instructions for the initial setup
1. Set up workspace and script locations
   ```bash
   SCRIPT_FILE_NAME=credit_card_balance_analysis_lib.py
   SPARK_SUBMIT_ARGS=
   SCRIPT_ARGS=
   ```
2. Run the container with [spark-submit](https://spark.apache.org/docs/latest/submitting-applications.html)
   ```bash
   docker run -it --rm --name spark \
       -v $PWD/src/spark/:/opt/spark/work-dir/ \
       -v $PWD/src/libraries/:/opt/spark/libraries/ \
       -v $PWD/temp/:/opt/spark/temp/ \
       spark:3.5.4-scala2.12-java17-python3-ubuntu \
       bash -c "export PYTHONPATH=\$PYTHONPATH:/opt/spark/libraries/ && /opt/spark/bin/spark-submit /opt/spark/work-dir/$SCRIPT_FILE_NAME $SCRIPT_ARGS"
   ```
   * [src/libraries/](/src/libraries/) and `export PYTHONPATH=\$PYTHONPATH:/opt/spark/libraries/` is mounted 

### PUMS Parsing

Refer to the similar [AWS Glue](/docs/aws-glue.md#pums-parsing) for the initial setup
1. Set up workspace and script locations
   ```bash
   SCRIPT_FILE_NAME=parse_pums.py
   SPARK_SUBMIT_ARGS=
   SCRIPT_ARGS="--temp_dir /opt/spark/temp --odcs_dir /opt/spark/config --pums_file input/pums_36.dat"
   ```
2. Run the container with [spark-submit](https://spark.apache.org/docs/latest/submitting-applications.html)
   ```bash
   docker run -it --rm --name spark_4 -u 0 \
       -v $PWD/src/spark/:/opt/spark/work-dir/ \
       -v $PWD/src/odcs/:/opt/spark/config/ \
       -v $PWD/temp/:/opt/spark/temp/ \
       spark:4.1.2-scala2.13-java21-python3-ubuntu \
       bash -c "python3 -m pip install \"open-data-contract-standard==3.1.2\" && /opt/spark/bin/spark-submit $SPARK_SUBMIT_ARGS /opt/spark/work-dir/$SCRIPT_FILE_NAME $SCRIPT_ARGS"
   ```

### Apache Spark Streaming

See the related documentation:
* [Spark Streaming Programming Guide](https://spark.apache.org/docs/latest/streaming-programming-guide.html) is a guide to implement "Spark Streaming[, which] is the previous generation of Spark’s streaming engine,"
* [Structured Streaming Programming Guide](https://spark.apache.org/docs/latest/streaming/index.html) is a guide to implement Structured Streaming, which "is a scalable and fault-tolerant stream processing engine built on the Spark SQL engine
  > Internally, by default, Structured Streaming queries are processed using a micro-batch processing engine, which processes data streams as a series of small batch jobs thereby achieving end-to-end latencies as low as 100 milliseconds and exactly-once fault-tolerance guarantees.
  * [Continuous Processing](https://spark.apache.org/docs/latest/streaming/performance-tips.html#continuous-processing) "is a new, experimental streaming execution mode introduced in Spark 2.3 that enables low (~1 ms) end-to-end latency with at-least-once fault-tolerance guarantees. Compare this with the default micro-batch processing engine which can achieve exactly-once guarantees but achieve latencies of ~100ms at best"
* [Structured Streaming + Kafka Integration Guide (Kafka broker version 0.10.0 or higher)](https://spark.apache.org/docs/latest/streaming/structured-streaming-kafka-integration.html)
  * Kafka doesn't have to be processed via Structured Streaming based on the following documentation:
    * [pyspark.sql.SparkSession.read](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.SparkSession.read.html#pyspark.sql.SparkSession.read) can be used instead of [pyspark.sql.SparkSession.readStream](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.SparkSession.readStream.html) to operate as batch processing instead of stream processing based on [Creating a Kafka Source for Batch Queries](https://spark.apache.org/docs/latest/streaming/structured-streaming-kafka-integration.html#creating-a-kafka-source-for-batch-queries)
      * `pyspark.sql.SparkSession.read` returns [pyspark.sql.DataFrameReader](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameReader.html)
      * `pyspark.sql.SparkSession.readStream` returns [pyspark.sql.streaming.DataStreamReader](https://spark.apache.org/docs/latest/api/python/reference/pyspark.ss/api/pyspark.sql.streaming.DataStreamReader.html)
    * [pyspark.sql.DataFrame.write](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.write.html) can be used instead of [pyspark.sql.DataFrame.writeStream](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.writeStream.html) based on [Writing the output of Batch Queries to Kafka](https://spark.apache.org/docs/latest/streaming/structured-streaming-kafka-integration.html#writing-the-output-of-batch-queries-to-kafka)
      * `pyspark.sql.SparkSession.write` returns [pyspark.sql.DataFrameWriter](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrameWriter.html)
      * `pyspark.sql.SparkSession.writeStream` returns [pyspark.sql.streaming.DataStreamWriter](https://spark.apache.org/docs/latest/api/python/reference/pyspark.ss/api/pyspark.sql.streaming.DataStreamWriter.html)

Refer to the similar [AWS Glue](/docs/aws-glue.md#aws-glue-streaming) for the initial setup
1. Set up workspace and script locations
   ```bash
   SCRIPT_FILE_NAME=credit_card_balance_analysis_streaming.py
   SPARK_SUBMIT_ARGS="--packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.1.2"
   SCRIPT_ARGS=
   ```
2. Run the container with [spark-submit](https://spark.apache.org/docs/latest/submitting-applications.html)
   ```bash
   docker run -it --rm --name spark_4 -u 0 \
       -v $PWD/src/spark/:/opt/spark/work-dir/ \
       -v $PWD/src/libraries/:/opt/spark/libraries/ \
       spark:4.1.2-scala2.13-java21-python3-ubuntu \
       bash -c "export PYTHONPATH=\$PYTHONPATH:/opt/spark/libraries/ && /opt/spark/bin/spark-submit $SPARK_SUBMIT_ARGS /opt/spark/work-dir/$SCRIPT_FILE_NAME $SCRIPT_ARGS"
   ```

The `DataFrame` that is created from reading the Kafka topic has the columns mentioned below with `key` and `value` needing to be cast back to `STRING`. If the `value` is stringified via [json.dumps](https://docs.python.org/3/library/json.html#json.dumps), then [pyspark.sql.functions.from_json](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.from_json.html) is needed to reverse it.
```python
from pyspark.sql import DataFrame
from pyspark.sql.functions import col

df: DataFrame = ... # read from Kafka topic

# Cast binary key and value columns to string
formatted_df: DataFrame = df.select(
   col("key").cast("STRING"), 
   col("value").cast("STRING"),
   col("partition"),
   col("offset"),
   col("timestamp"),
   col("timestampType"))
)
```

**Note:** The [checkpoint location](https://spark.apache.org/docs/latest/streaming/apis-on-dataframes-and-datasets.html#recovering-from-failures-with-checkpointing) is necessary or the following stack trace would be thrown
```
Traceback (most recent call last):
  ...
  File "/usr/lib/spark/python/lib/pyspark.zip/pyspark/sql/streaming/readwriter.py", line 1527, in start
  File "/usr/lib/spark/python/lib/py4j-0.10.9.7-src.zip/py4j/java_gateway.py", line 1322, in __call__
  File "/usr/lib/spark/python/lib/pyspark.zip/pyspark/errors/exceptions/captured.py", line 185, in deco
: checkpointLocation must be specified either through option("checkpointLocation", ...) or SparkSession.conf.set("spark.sql.streaming.checkpointLocation", ...).
```

**Note:** Based on [pyspark.sql.streaming.DataStreamWriter.trigger](https://spark.apache.org/docs/latest/api/python/reference/pyspark.ss/api/pyspark.sql.streaming.DataStreamWriter.trigger.html) function description,
* `processingTime` appears to correspond to the "default micro-batch processing engine"
* `continuous` appears to correspond to "continuous processing" mode which is experimental
* `realTime` appears to correspond to the "real-time mode" for AWS Glue Streaming which was introduced in AWS Glue 6.0
* "If this is not set it will run the query as fast as possible, which is equivalent to setting the trigger to `processingTime='0 seconds'`."

## Spark + Deequ

Refer to the similar [AWS Glue](/docs/aws-glue.md#aws-glue-dq) for the initial setup
1. Set up workspace and script locations
   ```bash
   SCRIPT_FILE_NAME=credit_card_balance_dq.py
   SPARK_SUBMIT_ARGS="--packages com.amazon.deequ:deequ:2.0.18-spark-4.1,software.amazon.glue:dqdl:1.0.2"
   SCRIPT_ARGS="--temp_dir /opt/spark/temp"
   ```
2. Run the container with [spark-submit](https://spark.apache.org/docs/latest/submitting-applications.html)
   ```bash
   docker run -it --rm --name spark_4 -u 0 \
       -v $PWD/src/spark/:/opt/spark/work-dir/ \
       -v $PWD/temp/:/opt/spark/temp/ \
       spark:4.1.2-scala2.13-java21-python3-ubuntu \
       /opt/spark/bin/spark-submit $SPARK_SUBMIT_ARGS /opt/spark/work-dir/$SCRIPT_FILE_NAME $SCRIPT_ARGS
   ```
