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
   WORKSPACE_LOCATION=$PWD
   SCRIPT_FILE_NAME=word_count.py
   SCRIPT_ARGS=/opt/spark/work-dir/$SCRIPT_FILE_NAME
   ```
3. Run the container with [spark-submit](https://spark.apache.org/docs/latest/submitting-applications.html)
    ```bash
    docker run -it --rm --name spark \
        -v $WORKSPACE_LOCATION/src/spark/:/opt/spark/work-dir/ \
        spark:3.5.4-scala2.12-java17-python3-ubuntu \
        /opt/spark/bin/spark-submit /opt/spark/work-dir/$SCRIPT_FILE_NAME $SCRIPT_ARGS
    ```
   * `SCRIPT_ARGS` is the same as the script location because we're parsing the lines from the same script to perform word count

### Apache Spark Docker Testing

Refer to [pytest option](https://spark.apache.org/docs/latest/api/python/getting_started/testing_pyspark.html#Option-3:-Using-Pytest) for how we can test Spark code. It isn't straightforward to install `pytest` on the Docker container to run the [tests/spark/](/tests/spark/) similar to [AWS Glue](aws-glue.md#aws-glue-docker-testing). The error that is thrown when you attempt to run a similar command to `python3 -m pytest` is as follows:
```
WARNING: The directory '/home/spark/.cache/pip' or its parent directory is not owned or is not writable by the current user. The cache has been disabled. Check the permissions and owner of that directory. If executing pip with sudo, you should use sudo's -H flag.
Defaulting to user installation because normal site-packages is not writeable
```
