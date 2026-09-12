# AWS Glue

Refer to [here](https://docs.aws.amazon.com/glue/latest/dg/release-notes.html) for the open-source equivalent version, [Apache Spark](apache-spark.md).

Refer to [here](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-python-libraries.html#glue-modules-provided) for Python modules already in AWS Glue.

## AWS Glue Docker

Refer to [here](https://docs.aws.amazon.com/glue/latest/dg/develop-local-docker-image.html) on usage of the Docker image for development and testing.

From [DockerHub > amazon/aws-glue-libs](https://hub.docker.com/r/amazon/aws-glue-libs), we will use Glue 5.0 as the starting point by pulling the following image:
```bash
docker pull amazon/aws-glue-libs:5.0.9
```

### AWS Glue Docker Run

To run AWS Glue locally using Docker against [word_count.py](/src/spark/word_count.py), follow these steps:
1. Disable Windows path resolution if running via Git Bash
   ```bash
   export MSYS_NO_PATHCONV=1
   ```
2. Set up workspace and script locations
   ```bash
   SCRIPT_FILE_NAME=word_count.py
   SCRIPT_ARGS=/home/hadoop/workspace/$SCRIPT_FILE_NAME
   ```
3. Run the container with [spark-submit](https://spark.apache.org/docs/latest/submitting-applications.html)
   ```bash
   docker run -it --rm --name glue5_spark_submit \
       -v $PWD/src/spark/:/home/hadoop/workspace/ \
       amazon/aws-glue-libs:5.0.9 \
       spark-submit /home/hadoop/workspace/$SCRIPT_FILE_NAME $SCRIPT_ARGS
   ```
   * `SCRIPT_ARGS` is the same as the script location because we're parsing the lines from the same script to perform word count

### AWS Glue Docker Testing

To run the AWS Glue pytest, use the following command:
```bash
docker run -i --rm --name glue5_pytest \
    -v $PWD/:/home/hadoop/workspace/ \
    --workdir /home/hadoop/workspace/ \
    amazon/aws-glue-libs:5.0.9 \
    -c "python3.11 -m pip install \"open-data-contract-standard==3.1.2\" && python3.11 -m pytest --disable-warnings"
```

To run [coverage](https://coverage.readthedocs.io/en/latest/) as well
```bash
docker run -i --rm --name glue5_pytest \
    -v $PWD/:/home/hadoop/workspace/ \
    --workdir /home/hadoop/workspace/ \
    amazon/aws-glue-libs:5.0.9 \
    -c "python3.11 -m pip install \"open-data-contract-standard==3.1.2\" && python3.11 -m coverage run -m pytest --disable-warnings && python3.11 -m coverage xml && python3.11 -m coverage html"
```

### Federal Reserve Data Analytics

The following instructions are for running PySpark application defined by [src/spark/credit_card_balance_analysis.py](/src/spark/credit_card_balance_analysis.py):
1. Assemble the datasets needed and download the CSV-formatted copies to the [temp/input](/temp/input) folder
   1. Download [Large Bank Consumer Credit Card Balances: Total Balances](https://fred.stlouisfed.org/series/RCCCBBALTOT)
      * `observation_date` is the date in `YYYY-MM-DD`
      * `RCCCBBALTOT` is the balance in billions of dollars
   2. Download [Large Bank Consumer Credit Card Balances: Revolving Balances Only](https://fred.stlouisfed.org/series/RCCCBBALREV)
      * `observation_date` is the date in `YYYY-MM-DD`
      * `RCCCBBALREV` is the balance in billions of dollars
2. Disable Windows path resolution if running via Git Bash
   ```bash
   export MSYS_NO_PATHCONV=1
   ```
3. Set up workspace and script locations
   ```bash
   SCRIPT_FILE_NAME=credit_card_balance_analysis.py
   SPARK_SUBMIT_ARGS=
   SCRIPT_ARGS="--temp_dir /home/hadoop/temp"
   ```
4. Run the container with [spark-submit](https://spark.apache.org/docs/latest/submitting-applications.html)
   ```bash
   docker run -it --rm --name glue5_spark_submit \
       -v $PWD/src/spark/:/home/hadoop/workspace/ \
       -v $PWD/temp/:/home/hadoop/temp/ \
       amazon/aws-glue-libs:5.0.9 \
       spark-submit $SPARK_SUBMIT_ARGS /home/hadoop/workspace/$SCRIPT_FILE_NAME $SCRIPT_ARGS
   ```

### Federal Reserve Data Analytics with Library

The following instructions are for running PySpark application defined by [src/spark/credit_card_balance_analysis_lib.py](/src/spark/credit_card_balance_analysis_lib.py):
1. Disable Windows path resolution if running via Git Bash
   ```bash
   export MSYS_NO_PATHCONV=1
   ```
2. Set up workspace and script locations
   ```bash
   SCRIPT_FILE_NAME=credit_card_balance_analysis_lib.py
   SPARK_SUBMIT_ARGS=
   SCRIPT_ARGS=
   ```
3. Run the container with [spark-submit](https://spark.apache.org/docs/latest/submitting-applications.html)
   ```bash
   docker run -it --rm --name glue5_spark_submit \
       -v $PWD/src/spark/:/home/hadoop/workspace/ \
       -v $PWD/src/libraries/:/home/hadoop/libraries/ \
       amazon/aws-glue-libs:5.0.9 \
       -c "export PYTHONPATH=\$PYTHONPATH:/home/hadoop/libraries/ && spark-submit $SPARK_SUBMIT_ARGS /home/hadoop/workspace/$SCRIPT_FILE_NAME $SCRIPT_ARGS"
   ```
   * [src/libraries/](/src/libraries/) and `export PYTHONPATH=\$PYTHONPATH:/home/hadoop/libraries/` is mounted to make it accessible as if a zip file with the same content is passed to `--extra-py-files`

### PUMS Parsing

The following instructions are for running PySpark application defined by [src/spark/parse_pums.py](/src/spark/parse_pums.py) to parse [PUMS Census 2000](/docs/pums.md#pums-census-2000) files:
1. Download relevant files from [here](https://www2.census.gov/census_2000/datasets/PUMS/OnePercent/)
2. Disable Windows path resolution if running via Git Bash
   ```bash
   export MSYS_NO_PATHCONV=1
   ```
3. Set up workspace and script locations
   ```bash
   SCRIPT_FILE_NAME=parse_pums.py
   SPARK_SUBMIT_ARGS=
   SCRIPT_ARGS="--temp_dir /home/hadoop/temp --odcs_dir /home/hadoop/config --pums_file input/pums_36.dat"
   ```
4. Run the container with [spark-submit](https://spark.apache.org/docs/latest/submitting-applications.html)
   ```bash
   docker run -it --rm --name glue5_spark_submit \
       -v $PWD/src/spark/:/home/hadoop/workspace/ \
       -v $PWD/src/odcs/:/home/hadoop/config/ \
       -v $PWD/temp/:/home/hadoop/temp/ \
       amazon/aws-glue-libs:5.0.9 \
       -c "python3.11 -m pip install \"open-data-contract-standard==3.1.2\" && spark-submit $SPARK_SUBMIT_ARGS /home/hadoop/workspace/$SCRIPT_FILE_NAME $SCRIPT_ARGS"
   ```

**Note:** Apache Spark doesn't respect `CHAR(X)` or `VARCHAR(X)` and resolves to `StringType`
> 26/08/16 21:41:30 WARN CharVarcharUtils: The Spark cast operator does not support char/varchar type and simply treats them as string type. Please use string type directly to avoid confusion. Otherwise, you can set spark.sql.legacy.charVarcharAsString to true, so that Spark treat them as string type as same as Spark 3.0 and earlier

### OpenLineage Integration

Refer to the following documentation
* [OpenLineage > Integrations > Apache Spark > Quickstart > Quickstart with AWS Glue](https://openlineage.io/docs/integrations/spark/quickstart/quickstart_glue/)
* [OpenLineage > Integrations > Apache Spark > Configuration > Usage](https://openlineage.io/docs/integrations/spark/configuration/usage)
* [AWS Big Data Blog > Build data lineage for data lakes using AWS Glue, Amazon Neptune, and Spline](https://aws.amazon.com/blogs/big-data/amazon-datazone-introduces-openlineage-compatible-data-lineage-visualization-in-preview/)

The following instructions are to publish OpenLineage information to a local instance
1. Make the following changes to the prior [Federal Reserve Data Analytics](#federal-reserve-data-analytics)
   ```bash
   export SPARK_SUBMIT_ARGS="--conf spark.extraListeners=io.openlineage.spark.agent.OpenLineageSparkListener --conf spark.openlineage.transport.type=http --conf spark.openlineage.transport.url=http://host.docker.internal:5000 --conf spark.openlineage.namespace=spark_namespace --conf spark.openlineage.parentJobNamespace=airflow_namespace --conf spark.openlineage.parentJobName=airflow_dag.airflow_task --conf spark.openlineage.parentRunId=xxxx-xxxx-xxxx-xxxx --packages io.openlineage:openlineage-spark_2.12:1.44.0"
   ```
2. Run the container with [spark-submit](https://spark.apache.org/docs/latest/submitting-applications.html)
   ```bash
   docker run -it --rm --name glue5_spark_submit \
       -v $PWD/src/spark/:/home/hadoop/workspace/ \
       -v $PWD/temp/:/home/hadoop/temp/ \
       amazon/aws-glue-libs:5.0.9 \
       spark-submit $SPARK_SUBMIT_ARGS /home/hadoop/workspace/$SCRIPT_FILE_NAME $SCRIPT_ARGS
   ```
3. Check the data lineage through http://localhost:3000/

### AWS Glue Streaming

The following instructions are for setting up a local Kafka and running a Glue Streaming job
1. Based on [Developing event-driven applications with Kafka and Docker > Starting Kafka](https://docs.docker.com/guides/kafka/#starting-kafka)
   1. Start the Kafka container
      ```bash
      docker run --name=kafka -p 9092:9092 -d \
        -e KAFKA_NODE_ID=1 \
        -e KAFKA_PROCESS_ROLES=broker,controller \
        -e KAFKA_LISTENERS=CONTROLLER://0.0.0.0:9093,BROKER://0.0.0.0:9092 \
        -e KAFKA_ADVERTISED_LISTENERS=BROKER://host.docker.internal:9092 \
        -e KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER \
        -e KAFKA_INTER_BROKER_LISTENER_NAME=BROKER \
        -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,BROKER:PLAINTEXT \
        -e KAFKA_CONTROLLER_QUORUM_VOTERS=1@localhost:9093 \
        -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
        apache/kafka:4.3.1
      ```
      * See [Kafka Docker Image Usage Guide](https://github.com/apache/kafka/blob/trunk/docker/examples/README.md) for more information
      * Check the status of the Kafka broker via [kafka-cluster.sh](https://docs.confluent.io/kafka/operations-tools/kafka-tools.html#kafka-cluster-sh)
         ```bash
         docker exec kafka /opt/kafka/bin/kafka-cluster.sh cluster-id --bootstrap-server :9092
         ```
   2. Create the `RCCCBBALTOT`, `RCCCBBALREV` and `RCCCBPAYMENT` topics via [kafka-topics.sh](https://docs.confluent.io/kafka/operations-tools/kafka-tools.html#kafka-topics-sh)
      ```bash
      docker exec kafka /opt/kafka/bin/kafka-topics.sh --create --bootstrap-server :9092 --topic RCCCBBALTOT --replication-factor 1
      docker exec kafka /opt/kafka/bin/kafka-topics.sh --create --bootstrap-server :9092 --topic RCCCBBALREV --replication-factor 1
      docker exec kafka /opt/kafka/bin/kafka-topics.sh --create --bootstrap-server :9092 --topic RCCCBPAYMENT --replication-factor 1
      ```
      * Write messages and exit with `Ctrl + C` via [kafka-console-producer.sh](https://docs.confluent.io/kafka/operations-tools/kafka-tools.html#kafka-console-producer-sh)
   3. Write messages into the `RCCCBBALTOT` and `RCCCBBALREV` topics
      ```bash
      python src/scripts/write_fred_data_to_kafka.py
      ```
   4. Stop and remove the Kafka container
      ```bash
      docker stop kafka
      docker rm kafka
      ```
2. Disable Windows path resolution if running via Git Bash
   ```bash
   export MSYS_NO_PATHCONV=1
   ```
3. Set up workspace and script locations
   ```bash
   SCRIPT_FILE_NAME=credit_card_balance_analysis_streaming.py
   SPARK_SUBMIT_ARGS="--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.4"
   SCRIPT_ARGS=
   ```
4. Run the container with [spark-submit](https://spark.apache.org/docs/latest/submitting-applications.html)
   ```bash
   docker run -it --rm --name glue5_spark_submit \
       -v $PWD/src/spark/:/home/hadoop/workspace/ \
       -v $PWD/src/libraries/:/home/hadoop/libraries/ \
       amazon/aws-glue-libs:5.0.9 \
       -c "export PYTHONPATH=\$PYTHONPATH:/home/hadoop/libraries/ && spark-submit $SPARK_SUBMIT_ARGS /home/hadoop/workspace/$SCRIPT_FILE_NAME $SCRIPT_ARGS"
   ```
   * Check what's published in the `RCCCBPAYMENT` topic via [kafka-console-consumer.sh](https://docs.confluent.io/kafka/operations-tools/kafka-tools.html#kafka-console-consumer-sh)
      ```bash
      docker exec -ti kafka /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server :9092 --topic RCCCBPAYMENT --from-beginning
      ```

AWS Glue Streaming has [two execution models](https://docs.aws.amazon.com/glue/latest/dg/glue-streaming-execution-models.html)
* [Micro-batch mode](https://docs.aws.amazon.com/glue/latest/dg/glue-streaming-execution-models.html#glue-streaming-micro-batch-mode) which "is the default execution model for all AWS Glue streaming jobs. This mode uses [forEachBatch](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-api-crawler-pyspark-extensions-glue-context.html#aws-glue-api-crawler-pyspark-extensions-glue-context-forEachBatch) or `Trigger.ProcessingTime` to poll the source at configured intervals."
* [Real-time mode (AWS Glue 6.0+)](https://docs.aws.amazon.com/glue/latest/dg/glue-streaming-execution-models.html#glue-streaming-concepts-real-time-mode) which "is a new execution model for [Spark Structured Streaming](/docs/apache-spark.md#apache-spark-streaming) available starting in AWS Glue 6.0 that reduces end-to-end latency to sub-second. Real-time mode can also help achieve millisecond-level latencies for eligible workloads. Tasks run continuously, processing records as they arrive rather than waiting for data to accumulate. Real-time mode applies only to Spark Structured Streaming and does not apply to legacy Spark Streaming (DStreams)."
