from pathlib import Path
from pyspark.sql import SparkSession
import pytest
from _pytest.monkeypatch import MonkeyPatch
from unittest.mock import patch, MagicMock

from src.spark.word_count import (
    word_count,
    main
)

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

@patch("src.spark.word_count.word_count")
@patch("src.spark.word_count.SparkSession")
def test_main(
        mock_spark_session: MagicMock,
        mock_word_count: MagicMock,
        monkeypatch: MonkeyPatch,
        spark: SparkSession):
    # ARRANGE
    file_path: str = "src/spark/word_count.py"
    monkeypatch.setattr("sys.argv", ["word_count.py", file_path])
    mock_spark_session.builder.appName.return_value.getOrCreate.return_value = spark
    mock_word_count.return_value = [
        ("hello", 2),
        ("world", 1),
    ]

    # ACT
    main()

    # ASSERT
    mock_word_count.assert_called_once_with(spark, file_path)


def test_main_no_args(monkeypatch: MonkeyPatch):
    # ARRANGE
    monkeypatch.setattr("sys.argv", ["word_count.py"])

    with pytest.raises(SystemExit) as exc_info:
        # ACT
        main()

        # ASSERT
        assert exc_info.value.args[0] == -1
