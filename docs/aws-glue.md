# AWS Glue

Refer to [here](https://docs.aws.amazon.com/glue/latest/dg/release-notes.html) for the open-source equivalent version, [Apache Spark](apache-spark.md).

## AWS Glue Docker 

From [DockerHub > amazon/aws-glue-libs](https://hub.docker.com/r/amazon/aws-glue-libs), we will use Glue 5.0 as the starting point by pulling the following image:
```bash
docker pull amazon/aws-glue-libs:5
```

### AWS Glue Docker Run

To run AWS Glue locally using Docker against [word_count.py](/src/word_count.py), follow these steps:
1. Disable Windows path resolution if running via Git Bash
    ```bash
    export MSYS_NO_PATHCONV=1
    ```
2. Set up workspace and script locations
   ```bash
   WORKSPACE_LOCATION=$PWD
   SCRIPT_FILE_NAME=word_count.py
   SCRIPT_ARGS=/home/hadoop/workspace/src/$SCRIPT_FILE_NAME
   ```
3. Run container with spark-submit
   ```bash
   docker run -it --rm \
       -v ~/.aws:/home/hadoop/.aws \
       -v $WORKSPACE_LOCATION:/home/hadoop/workspace/ \
       -e AWS_PROFILE=$PROFILE_NAME \
       --name glue5_spark_submit \
       amazon/aws-glue-libs:5 \
       spark-submit /home/hadoop/workspace/src/$SCRIPT_FILE_NAME $SCRIPT_ARGS
   ```

### AWS Glue Docker Testing

```bash
docker run -i --rm \
    -v ~/.aws:/home/hadoop/.aws \
    -v $WORKSPACE_LOCATION:/home/hadoop/workspace/ \
    --workdir /home/hadoop/workspace \
    -e AWS_PROFILE=$PROFILE_NAME \
    --name glue5_pytest \
    amazon/aws-glue-libs:5 \
    -c "python3.11 -m pytest --disable-warnings"
```
