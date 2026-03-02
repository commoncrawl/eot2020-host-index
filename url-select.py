import sys

import duckdb


what = sys.argv[1]
where = sys.argv[2]

bucket = 's3://eotarchive/'

parq = open('eot2020.paths').read().split()

parq = [bucket+p for p in parq]

eot2020_url = duckdb.read_parquet(parq)

sql = f'SELECT {what} FROM eot2020_url WHERE {where}'
print(sql)

duckdb.sql(sql).show()
