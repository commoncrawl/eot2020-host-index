"""Query the EOT url index (columnar index) with DuckDB.

Usage:
    python url-select.py "<SELECT columns>" "<WHERE clause>"

The url index is hive-partitioned by crawl on S3, so every row carries a
`crawl` column (e.g. 'EOT-2020', 'EOT-2024').  It is read directly from S3
(needs AWS credentials) and exposed as the view `eot_url`.

This index is very large (many GB per crawl).  Always narrow your query --
in particular add `crawl = 'EOT-2024'` so DuckDB can prune to a single crawl,
and filter on a host so it can skip row groups.
"""
import sys

import duckdb


what = sys.argv[1]
where = sys.argv[2]

# Hive-partitioned table: .../crawl=EOT-2020/, .../crawl=EOT-2024/, ...
url_index = 's3://eotarchive/eot-index/table/eot-main/crawl=EOT-*/*.parquet'

duckdb.sql('INSTALL httpfs; LOAD httpfs;')
duckdb.sql(
    f"CREATE VIEW eot_url AS "
    f"SELECT * FROM read_parquet('{url_index}', "
    f"hive_partitioning = true, union_by_name = true)"
)

sql = f'SELECT {what} FROM eot_url WHERE {where}'
print(sql)

duckdb.sql(sql).show()
