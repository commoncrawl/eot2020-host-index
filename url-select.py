import sys

import duckdb


what = sys.argv[1]
where = sys.argv[2]

#parq = ['https://data.commoncrawl.org/projects/eot2020-host-testing/EOT-2020-with-ranks-v2.parquet']
#parq = ['EOT-2020-with-ranks-v2.parquet']

bucket = 's3://eotarchive/'

parq = open('eot2020.paths').read().split()

parq = [bucket+p for p in parq]

eot2020_url = duckdb.read_parquet(parq)

sql = f'SELECT {what} FROM eot2020_url WHERE {where}'
print(sql)

duckdb.sql(sql).show()
