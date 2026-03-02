import sys
import os
import duckdb


what = sys.argv[1]
where = sys.argv[2]

remote_base_url = 'https://data.commoncrawl.org/projects/eot2020-host-testing/'
parquet_file = 'EOT-2020-with-ranks-v4.parquet'

if not os.path.exists(parquet_file):
    print("Reading index over HTTP")
    parquet_file = remote_base_url + parquet_file

parquet_files = [parquet_file]

eot2020_host = duckdb.read_parquet(parquet_files)

sql = f'SELECT {what} FROM eot2020_host WHERE {where}'
print(sql)

duckdb.sql(sql).show()
