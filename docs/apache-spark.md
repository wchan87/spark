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
