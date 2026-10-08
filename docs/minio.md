# MinIO

1. Run the Docker container, `minio` based on the  Docker image, [dhi.io/minio](https://hub.docker.com/hardened-images/catalog/dhi/minio)
    ```bash
    docker run -d --name minio -p 9000:9000 -p 9001:9001 \
        -e MINIO_ROOT_USER=admin \
        -e MINIO_ROOT_PASSWORD=password \
        dhi.io/minio:0.20251015.172955 \
        server /data --console-address ":9001"
    ```
    * Access MinIO Console via http://localhost:9001/
2. Interact with the Docker container via [AWS Command Line Interface](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html)
   1. Set the credentials
      ```bash
      export AWS_ACCESS_KEY_ID=admin
      export AWS_SECRET_ACCESS_KEY=password
      ```
   2. Create a S3 bucket via [aws s3 mb](https://docs.aws.amazon.com/cli/latest/reference/s3/mb.html)
      ```bash
      aws --endpoint-url=http://localhost:9000 s3 mb s3://test-bucket
      ```
   3. Copy a local file to S3 via [aws s3 cp](https://docs.aws.amazon.com/cli/latest/reference/s3/cp.html)
      ```bash
      aws --endpoint-url=http://localhost:9000 s3 cp test-file.txt s3://test-bucket/
      ```
   4. List S3 objects via [aws s3 ls](https://docs.aws.amazon.com/cli/latest/reference/s3/ls.html)
      ```bash
      aws --endpoint-url=http://localhost:9000 s3 ls s3://test-bucket/
      ```
3. Stop the Docker container, `minio`
    ```bash
    docker stop minio
    ```
4. Remove the Docker container, `minio`
    ```bash
    docker rm minio
    ```
