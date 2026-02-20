import sys

import duckdb


what = sys.argv[1]
where = sys.argv[2]

#parq = ['https://data.commoncrawl.org/projects/eot2020-host-testing/EOT-2020-with-ranks-v2.parquet']
parq = ['EOT-2020-with-ranks-v2.parquet']

eot2020_host = duckdb.read_parquet(parq)

sql = f'SELECT {what} FROM eot2020_host WHERE {where}'
print(sql)

duckdb.sql(sql).show()
