# Apache Iceberg

Refer to the [Spark Configuration](https://iceberg.apache.org/docs/latest/spark-configuration/) documentation for other configuration settings used for [Apache Spark](apache-spark.md) to read/write with Apache Iceberg. The `<catalog-name>` is used together with the namespace and/or table within the code to reference the corresponding Iceberg tables.

| Property | Values | Comments |
| -- | -- | -- |
| `spark.sql.catalog.<catalog-name>` | `org.apache.iceberg.spark.SparkCatalog`<br/>`org.apache.iceberg.spark.SparkSessionCatalog` | As per the [Replacing the session catalog](https://iceberg.apache.org/docs/latest/spark-configuration/#replacing-the-session-catalog) documentation, `SparkSessionCatalog` is a wrapper that allows for support of Iceberg and non-Iceberg tables by Spark. The built-in Spark catalog is loaded when non-Iceberg tables are referenced. |

## Iceberg Catalog

The responsibility of the [catalog](https://iceberg.apache.org/terms/#catalog) "is tracking a table's current metadata, which is provided by the catalog when you load a table."

| Property | Values | Comments |
| -- | -- | -- |
| `spark.sql.catalog.<catalog-name>.type` | `hive`, `hadoop`, `rest`, `glue`, `jdbc`, `nessie` | Refer to the "Type" from [Iceberg Catalog Implementations](#iceberg-catalog-implementations). |
| `spark.sql.catalog.<catalog-name>.catalog-impl` | | Refer to the "Java Class" from [Iceberg Catalog Implementations](#iceberg-catalog-implementations). |
| `spark.sql.catalog.<catalog-name>.uri` | `thrift://host:port`<br/>`https://catalog-service/api/catalog` | Hive Metastore URL if `spark.sql.catalog.<catalog-name>.type=hive`. REST URL if `spark.sql.catalog.<catalog-name>.type=rest`. |

### Iceberg Catalog Implementations

`spark.sql.catalog.<catalog-name>.catalog-impl` can refer to the implementations tied to `spark.sql.catalog.<catalog-name>.type` or [custom catalog implementation](https://iceberg.apache.org/docs/latest/custom-catalog/#custom-catalog-implementation) as well.

| Type | Java Class | Comments |
| -- | -- | -- |
| `hive` | [org.apache.iceberg.hive.HiveCatalog](https://iceberg.apache.org/javadoc/latest/org/apache/iceberg/hive/HiveCatalog.html) | Refer to [Iceberg Hive Catalog](#iceberg-hive-catalog). |
| `hadoop` | [org.apache.iceberg.hadoop.HadoopCatalog](https://iceberg.apache.org/javadoc/latest/org/apache/iceberg/hadoop/HadoopCatalog.html) | |
| `rest` | [org.apache.iceberg.rest.RESTCatalog](https://iceberg.apache.org/javadoc/latest/org/apache/iceberg/rest/RESTCatalog.html) | Refer to [Iceberg REST Catalog](#iceberg-rest-catalog). |
| `glue` | [org.apache.iceberg.aws.glue.GlueCatalog](https://iceberg.apache.org/javadoc/latest/org/apache/iceberg/aws/glue/GlueCatalog.html) | Refer to [Glue Catalog](https://iceberg.apache.org/docs/latest/aws/#glue-catalog) documentation. |
| `jdbc` | [org.apache.iceberg.jdbc.JdbcCatalog](https://iceberg.apache.org/javadoc/latest/org/apache/iceberg/jdbc/JdbcCatalog.html) | Refer to [Iceberg JDBC Integration](https://iceberg.apache.org/docs/latest/jdbc/) documentation. |
| `nessie` | [org.apache.iceberg.nessie.NessieCatalog](https://iceberg.apache.org/javadoc/latest/org/apache/iceberg/nessie/NessieCatalog.html) | Refer to [Iceberg Nessie Integration](https://iceberg.apache.org/docs/latest/nessie/) documentation. |

Based on [this reference](https://hive.apache.org/docs/latest/admin/iceberg-rest-catalog/), it appears to be possible to set up both [Thrift](#iceberg-hive-catalog) and [REST](#iceberg-rest-catalog) endpoints against a Hive Metastore.

### Iceberg Hive Catalog

Refer to [Global Hive catalog](https://iceberg.apache.org/docs/latest/hive/#global-hive-catalog) documentation.

The Docker image, [apache/hive:3.1.3](https://hub.docker.com/r/apache/hive/tags?name=3.1.3) can be used to start a Hive Metastore accessible on port 9083.
```bash
docker pull apache/hive:3.1.3
docker run -d -p 9083:9083 --env SERVICE_NAME=metastore --name hive3-metastore apache/hive:3.1.3
```
* The corresponding Spark configuration to connect to the Hive catalog is as follows:
    ```bash
    --conf spark.sql.catalog.local_catalog=org.apache.iceberg.spark.SparkCatalog \
    --conf spark.sql.catalog.local_catalog.type=hive \
    --conf spark.sql.catalog.local_catalog.uri=thrift://host.docker-internal:10000 \
    ```
* There's an alternative command to start the Hive Server
    ```bash
    docker run -d -p 10000:10000 -p 10002:10002 --env SERVICE_NAME=hiveserver2 --name hive3 apache/hive:3.1.3
    ```
    * Hive Web UI is accessible via http://localhost:10002/
    * [HiveServer2](https://hive.apache.org/docs/latest/user/hiveserver2-overview/) is accessible via `jdbc:hive2://localhost:10000/default`

The Docker image, [apache/hive:4.2.1](https://hub.docker.com/r/apache/hive/tags?name=4.2.1) can't be used due to a known issue, [#12878](https://github.com/apache/iceberg/issues/12878) which uses a method that Apache Hive 4 deprecated
```bash
docker pull apache/hive:4.2.1
docker run -d -p 9083:9083 --env SERVICE_NAME=metastore --name hive4-metastore apache/hive:4.2.1
docker run -d -p 10000:10000 -p 10002:10002 --env SERVICE_NAME=hiveserver2 --name hive4 apache/hive:4.2.1
```
* The error that's returned due to this issue is as follows:
    ```
    Caused by: org.apache.thrift.TApplicationException: Invalid method name: 'get_table'
          at org.apache.thrift.TServiceClient.receiveBase(TServiceClient.java:79)
    ```

[PyIceberg](https://py.iceberg.apache.org/) "is a Python implementation for accessing Iceberg tables, without the need of a JVM" through the PyPi package, [pyiceberg](https://pypi.org/project/pyiceberg/).
```bash
pyiceberg --uri thrift://localhost:9083 list
pyiceberg --uri thrift://localhost:9083 describe fred
```

### Iceberg REST Catalog

Refer to the [Iceberg REST Catalog](https://iceberg.apache.org/docs/latest/rest-catalog/) documentation.

The Docker image, [apache/iceberg-rest-fixture:1.10.1](https://hub.docker.com/r/apache/iceberg-rest-fixture/tags?name=1.10.1) can be used to start a standalone Iceberg REST catalog accessible on port 8181.
```bash
docker pull apache/iceberg-rest-fixture:1.10.1
docker run -d -p 8181:8181 --name iceberg-rest apache/iceberg-rest-fixture
```
* The corresponding Spark configuration to connect to the REST catalog is as follows:
    ```bash
    --conf spark.sql.catalog.app.type=rest \
    --conf spark.sql.catalog.app.uri=http://host.docker-internal:8181 \
    ```

[PyIceberg](https://py.iceberg.apache.org/) "is a Python implementation for accessing Iceberg tables, without the need of a JVM" through the PyPi package, [pyiceberg](https://pypi.org/project/pyiceberg/).
```bash
pyiceberg --uri http://localhost:8181 list
pyiceberg --uri http://localhost:8181 describe fred
```

## Iceberg Extensions

Refer to [SQL Extensions](https://iceberg.apache.org/docs/latest/spark-configuration/#sql-extensions), which adds Iceberg extensions to the Spark session.
```bash
--conf spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions
```

## Iceberg Storage

The underlying storage of the data and metadata files are driven by the Spark configuration below.

| Property | Values | Comments |
| -- | -- | -- |
| `spark.sql.catalog.<catalog-name>.io-impl` | [org.apache.iceberg.hadoop.HadoopFileIO](https://iceberg.apache.org/javadoc/latest/org/apache/iceberg/hadoop/HadoopFileIO.html)<br/>[org.apache.iceberg.aws.s3.S3FileIO](https://iceberg.apache.org/javadoc/latest/org/apache/iceberg/aws/s3/S3FileIO.html) | Iceberg storage implementation based on the interface, [org.apache.iceberg.io.FileIO](https://iceberg.apache.org/javadoc/latest/org/apache/iceberg/io/FileIO.html). |
| `spark.sql.catalog.<catalog-name>.warehouse` | `hdfs://example.com:8020/warehouse`<br/>`file:///warehouse`<br/>`s3://my-bucket/my/key/prefix` | `hdfs://` and `file://` are applicable to `org.apache.iceberg.hadoop.HadoopFileIO`. `s3://` is applicable to `org.apache.iceberg.aws.s3.S3FileIO`. |
