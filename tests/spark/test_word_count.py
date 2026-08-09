from pathlib import Path
from pyspark.sql import SparkSession
from src.spark.word_count import word_count


def test_word_count(spark: SparkSession, tmp_path: Path):
    # Create a temporary input file
    d = tmp_path / "data"
    d.mkdir()
    p = d / "hello.txt"
    p.write_text("hello world hello")

    # Run word_count
    results = word_count(spark, str(p))
    
    # Convert results to a dictionary for easier assertion
    results_dict = dict(results)
    
    assert results_dict["hello"] == 2
    assert results_dict["world"] == 1
    assert len(results_dict) == 2
