import argparse
from open_data_contract_standard.model import OpenDataContractStandard, CustomProperty, SchemaObject
from pyspark.sql import DataFrame, SparkSession, Column
from typing import Any, Optional


class FixedWidthFieldConfig:
    field_name: str
    field_type: str
    field_start: int
    field_end: int
    field_length: int

    def __init__(self, field_name: str, field_type: str, field_start: int, field_end: int):
        self.field_name = field_name
        self.field_type = field_type
        self.field_start = field_start
        self.field_end = field_end
        self.field_length = field_end - field_start + 1


class FixedWidthRecordConfig:
    record_name: str
    record_regex: str
    fields: list[FixedWidthFieldConfig]

    def __init__(self, record_name: str, record_regex: str):
        self.record_name = record_name
        self.record_regex = record_regex
        self.fields = []

    def add_field(self, field: FixedWidthFieldConfig):
        self.fields.append(field)


def schema_properties_to_dict(schema_properties: list[CustomProperty]) -> dict[str, Any]:
    schema_properties_dict: dict[str, Any] = {}
    for schema_prop in schema_properties:
        if schema_prop.property and schema_prop.value:
            schema_properties_dict[schema_prop.property] = schema_prop.value
    return schema_properties_dict


def get_fixed_width_field_config(schema: SchemaObject) -> Optional[FixedWidthRecordConfig]:
    if schema.name and schema.customProperties and schema.properties:
        schema_custom_props: dict[str, Any] = schema_properties_to_dict(schema.customProperties)
        regex: str = schema_custom_props["regex"]
        record_config: FixedWidthRecordConfig = FixedWidthRecordConfig(schema.name, regex)
        for schema_prop in schema.properties:
            if schema_prop.name and schema_prop.physicalType and schema_prop.customProperties:
                schema_prop_custom_props: dict[str, Any] = schema_properties_to_dict(schema_prop.customProperties)
                field_start: int = int(schema_prop_custom_props["field_start"])
                field_end: int = int(schema_prop_custom_props["field_end"])
                field_config: FixedWidthFieldConfig = FixedWidthFieldConfig(schema_prop.name, schema_prop.physicalType, field_start, field_end)
                record_config.add_field(field_config)
        return record_config
    else:
        return None


def get_fixed_width_record_configs(data_contract: OpenDataContractStandard) -> list[FixedWidthRecordConfig]:
    record_configs: list[FixedWidthRecordConfig] = []
    if data_contract.schema_:
        for schema in data_contract.schema_:
            record_config: Optional[FixedWidthRecordConfig] = get_fixed_width_field_config(schema)
            if record_config:
                record_configs.append(record_config)
    return record_configs


def get_columns(df: DataFrame, record_config: FixedWidthRecordConfig) -> list[Column]:
    columns: list[Column] = []
    for field in record_config.fields:
        # TODO physicalType = CHAR(X) and VARCHAR(X) isn't supported by Apache Spark 3.X so the cast resolves to String
        columns.append(df.value.substr(field.field_start, field.field_length).alias(field.field_name).cast(field.field_type))
    return columns


def main():
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("--temp_dir")
    parser.add_argument("--odcs_dir")
    parser.add_argument("--pums_file")
    args: argparse.Namespace = parser.parse_args()
    temp_dir: str = args.temp_dir
    odcs_dir: str = args.odcs_dir
    pums_file: str = args.pums_file

    spark_session: SparkSession = SparkSession.builder.appName("ParsePUMS").getOrCreate()

    data_contract: OpenDataContractStandard = OpenDataContractStandard.from_file(f"{odcs_dir}/pums_census_2000_1_percent.yaml")
    record_configs: list[FixedWidthRecordConfig] = get_fixed_width_record_configs(data_contract)

    df: DataFrame = spark_session.read.text(f"{temp_dir}/{pums_file}")
    for record_config in record_configs:
        columns: list[Column] = get_columns(df, record_config)
        record_df = df.select(columns).where(df.value.rlike(record_config.record_regex))
        record_df.write.mode("overwrite").parquet(f"{temp_dir}/output/{record_config.record_name}")


if __name__ == "__main__":
    main()
