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
* [Structured Streaming Programming Guide](https://spark.apache.org/docs/latest/streaming/index.html) is a guide to implement Structured Streaming, which "is a scalable and fault-tolerant stream processing engine built on the Spark SQL engine"
  * [Continuous Processing](https://spark.apache.org/docs/latest/streaming/performance-tips.html#continuous-processing) "is a new, experimental streaming execution mode introduced in Spark 2.3 that enables low (~1 ms) end-to-end latency with at-least-once fault-tolerance guarantees. Compare this with the default micro-batch processing engine which can achieve exactly-once guarantees but achieve latencies of ~100ms at best"
* [Structured Streaming + Kafka Integration Guide (Kafka broker version 0.10.0 or higher)](https://spark.apache.org/docs/latest/streaming/structured-streaming-kafka-integration.html)

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
