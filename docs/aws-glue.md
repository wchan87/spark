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
    -c "python3.11 -m pytest --disable-warnings"
```

To run [coverage](https://coverage.readthedocs.io/en/latest/) as well
```bash
docker run -i --rm --name glue5_pytest \
    -v $PWD/:/home/hadoop/workspace/ \
    --workdir /home/hadoop/workspace/ \
    amazon/aws-glue-libs:5.0.9 \
    -c "python3.11 -m coverage run -m pytest --disable-warnings && python3.11 -m coverage xml && python3.11 -m coverage html"
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

The following instructions are to publish OpenLineage information to a local instance of 
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
