from confluent_kafka import Producer
import csv
import io
import json
import urllib.request

start_date: str = "2012-07-01"
end_date: str = "2026-01-01"
total_balance_fred_id: str = "RCCCBBALTOT"
revolving_balance_fred_id: str = "RCCCBBALREV"
fred_ids: list[str] = [total_balance_fred_id, revolving_balance_fred_id]

conf = {
    'bootstrap.servers': 'localhost:9092'
}

producer: Producer = Producer(conf)

for fred_id in fred_ids:
    url: str = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={fred_id}&cosd={start_date}&coed={end_date}"
    buffer = urllib.request.urlopen(url)
    text_buffer: io.TextIOWrapper = io.TextIOWrapper(buffer, "UTF-8")
    csv_reader: csv.DictReader = csv.DictReader(text_buffer)
    for row in csv_reader:
        row[fred_id] = float(row[fred_id]) * 1_000_000_000
        producer.produce(fred_id, key=row["observation_date"], value=json.dumps(row))
    producer.flush()
