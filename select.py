from pathlib import Path
import sys
import os
import duckdb


what = sys.argv[1]
where = sys.argv[2]


if not what:
    raise ValueError("`what` parameter is missing")

if not where:
    raise ValueError("`where` parameter is missing")


default_parquet_file_path = 'https://data.commoncrawl.org/projects/eot2020-host-testing/EOT-2020-with-ranks-v5.parquet'

parquet_file_path = os.environ.get('EOT_PATH', default_parquet_file_path)

if not os.path.exists(parquet_file_path):
    # try local path
    parquet_file_name = Path(parquet_file_path).name

    if os.path.exists(parquet_file_name):
        print("Index file exists locally, using local instead of remote path.")

        parquet_file_path = str(parquet_file_name)

parquet_files = [parquet_file_path]

eot2020_host = duckdb.read_parquet(parquet_files)

sql = f'SELECT {what} FROM eot2020_host WHERE {where}'
print(sql)

duckdb.sql(sql).show()
