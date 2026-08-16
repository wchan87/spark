# Public Use Microdata Sample (PUMS)

[PUMS](https://www.census.gov/programs-surveys/acs/microdata.html) files have various formats over the years and provide "a set of untabulated records about individual people or housing units".
> The Census Bureau’s American Community Survey (ACS) Public Use Microdata Sample (PUMS) files enable data users to create custom estimates and tables, free of charge, that are not available through ACS pretabulated data products.  The ACS PUMS files are a set of records from individual people or housing units, with disclosure protection enabled so that individuals or housing units cannot be identified.

## PUMS Census 2000

[PUMS Census 2000](https://www.census.gov/data/datasets/2000/dec/microdata.html) files have "state-level [...] data containing individual records of the characteristics for a [...] sample of people and housing units."
* [Public Use Microdata Sample | 2000 Census of Population and Housing | Technical Documentation](https://www2.census.gov/programs-surveys/decennial/2000/technical-documentation/complete-tech-docs/pums.pdf) – **Note:** The official link is broken, so this link was found through Google.
* [PUMS 1-Percent](https://www2.census.gov/census_2000/datasets/PUMS/OnePercent/), data files for "1 percent sample of people and housing units."
* [PUMS 5-Percent](https://www2.census.gov/census_2000/datasets/PUMS/FivePercent/), data files for "5 percent sample of people and housing units."

PUMS Census 2000 data is particularly useful as it is a mixed record-type fixed-width file that precedes the adoption of CSV/XML/JSON.

The [pums_census_2000_1_percent.yaml](/src/odcs/pums_census_2000_1_percent.yaml) was initially populated via LLM after feeding the data dictionary in the form of a `pums.txt` file (due to the PDF format not being supported as input) that was generated from the technical documentation mentioned before. Additional prompts along with manual edits to the data contract are used to finalize the data contract for usage by Apache Spark application.
```bash
docker run --rm -v $PWD:/app -w /app minidocks/poppler pdftotext -f 119 -l 167 pums.pdf
```
The following code snippet generates the `REC*_FieldLabels` and `REC*_FieldWidths` for the [Fixed Width Data Visualizer plugin for Notepad++](https://github.com/shriprem/FWDataViz) from the `pums_census_2000_1_percent.yaml`.
```bash
python -c "
from open_data_contract_standard.model import OpenDataContractStandard

data_contract = OpenDataContractStandard.from_file('src/odcs/pums_census_2000_1_percent.yaml')
if data_contract.schema_:
    for schema in data_contract.schema_:
        if schema.properties:
            field_names: list[str] = []
            field_widths: list[int] = []
            for prop in schema.properties:
                field_names.append(prop.name)
                field_start: int = int(prop.customProperties[0].value)
                field_end: int = int(prop.customProperties[1].value)
                field_widths.append(field_end - field_start + 1)
            print(','.join(field_names))
            print(','.join(str(width) for width in field_widths))
"
```
