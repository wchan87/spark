# Documentation

* [Apache Spark](apache-spark.md)
* [AWS Glue](aws-glue.md)

## SonarQube

If you don't have local SonarQube setup, then use the following commands
1. Create the Docker volume, `sonarvol` and [volume subdirectory](https://docs.docker.com/engine/storage/volumes/#mount-a-volume-subdirectory)
    ```bash
    docker volume create sonarvol
    docker run --rm --mount src=sonarvol,dst=/sonarvol alpine mkdir -p /sonarvol/data /sonarvol/logs /sonarvol/extensions /sonarvol/temp
    ```
2. Run the Docker container, `sonarqube`
    ```bash
    docker run --name sonarqube -d \
        -p 9000:9000 \
        --mount type=volume,src=sonarvol,dst=/opt/sonarqube/data,volume-subpath=data \
        --mount type=volume,src=sonarvol,dst=/opt/sonarqube/logs,volume-subpath=logs \
        --mount type=volume,src=sonarvol,dst=/opt/sonarqube/extensions,volume-subpath=extensions \
        --mount type=volume,src=sonarvol,dst=/opt/sonarqube/temp,volume-subpath=temp \
        sonarqube:26.8.0.126808-community
    ```
   * Access via http://localhost:9000 with `admin` / `admin` credentials
   * Change the default password
   * Go to http://localhost:9000/account/security and create a new token to be set to `SONAR_TOKEN` environment variable

Run the Sonar analysis on the codebase with `SONAR_TOKEN` environment variable which depends on [coverage](aws-glue.md#aws-glue-docker-testing) being ran to generate `coverage.xml` and [sonar-project.properties](/sonar-project.properties) file.
```bash
docker run --rm \
    -e SONAR_HOST_URL="http://host.docker.internal:9000" \
    -e SONAR_TOKEN=$SONAR_TOKEN \
    -v $PWD:/usr/src \
    sonarsource/sonar-scanner-cli
```
