"""Query the EOT host index with DuckDB.

Usage:
    python select.py "<SELECT columns>" "<WHERE clause>"

The host index is hive-partitioned by version (`v`) and EOT crawl year
(`crawl`), so every row carries `v` and `crawl` columns.  It is exposed as
the view `eot_host` and read directly from the source (no download needed).

By default the public HTTP mirror is used.  Set the environment variable
EOT_SOURCE=s3 to read from S3 instead (needs AWS credentials).

Add e.g. `crawl = 2024` to the WHERE clause to restrict a query to a single
crawl; without it you query every crawl (currently 2020 and 2024).
"""
import os
import sys

import duckdb


what = sys.argv[1]
where = sys.argv[2]

if not what:
    raise ValueError("`what` parameter is missing")

if not where:
    raise ValueError("`where` parameter is missing")

# Hive partitions currently published: (version v, crawl year).
partitions = [(5, 2020), (5, 2024)]
relative = 'v={v}/crawl={crawl}/host-index.parquet'

source = os.environ.get('EOT_SOURCE', 'http').lower()

if source == 's3':
    base = 's3://commoncrawl/projects/eot-host-index-testing/'
    # S3 supports globbing, so hive columns are discovered automatically.
    files = [base + 'v=*/crawl=*/host-index.parquet']
else:
    base = 'https://data.commoncrawl.org/projects/eot-host-index-testing/'
    # Plain HTTP can't list directories, so enumerate the partition files.
    files = [base + relative.format(v=v, crawl=crawl) for v, crawl in partitions]

duckdb.sql('INSTALL httpfs; LOAD httpfs;')
duckdb.sql(
    f"CREATE VIEW eot_host AS "
    f"SELECT * FROM read_parquet({files!r}, hive_partitioning = true)"
)

sql = f'SELECT {what} FROM eot_host WHERE {where}'
print(sql)

duckdb.sql(sql).show()
