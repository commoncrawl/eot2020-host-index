# eot-host-index

PRELIMINARY VERSION

This readme describes a host index database that aggregates
information about the contents in the End of Term Archive.

https://eotarchive.org/

It currently covers two crawls, **EOT-2020** and **EOT-2024**. The data is
stored as a hive-partitioned parquet dataset, partitioned by version (`v`) and
crawl year (`crawl`):

```
v=5/crawl=2020/host-index.parquet
v=5/crawl=2024/host-index.parquet
```

Every row therefore carries a `crawl` column (and a `v` column), so a single
query can look at one crawl (`WHERE crawl = 2024`) or compare both (`GROUP BY
crawl`).

The dataset is available two ways:

- over HTTP (default, no credentials):
  `https://data.commoncrawl.org/projects/eot-host-index-testing/`
- on S3 (needs AWS credentials):
  `s3://commoncrawl/projects/eot-host-index-testing/`

## Install the duckdb cli

https://duckdb.org/install/

and the python client library

```bash
pip install duckdb
```

## Schema

The helper scripts read the dataset directly from its source -- no download
needed. To inspect the schema over HTTP:

```bash
duckdb -c "DESCRIBE FROM read_parquet('https://data.commoncrawl.org/projects/eot-host-index-testing/v=5/crawl=2024/host-index.parquet')"
```

To inspect both crawls at once (and see the `v`/`crawl` partition columns), point
duckdb at the hive layout on S3:

```bash
duckdb -c "DESCRIBE FROM read_parquet('s3://commoncrawl/projects/eot-host-index-testing/v=*/crawl=*/host-index.parquet', hive_partitioning = true)"
```

<details><summary>click to see output</summary>

```
┌────────────────────────────┬─────────────┬─────────┬─────────┬─────────┬─────────┐
│        column_name         │ column_type │  null   │   key   │ default │  extra  │
│          varchar           │   varchar   │ varchar │ varchar │ varchar │ varchar │
├────────────────────────────┼─────────────┼─────────┼─────────┼─────────┼─────────┤
│ surt_host_name             │ VARCHAR     │ YES     │ NULL    │ NULL    │ NULL    │
│ url_host_name_reversed     │ VARCHAR     │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_200                  │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ url_host_name              │ VARCHAR     │ YES     │ NULL    │ NULL    │ NULL    │
│ url_host_tld               │ VARCHAR     │ YES     │ NULL    │ NULL    │ NULL    │
│ url_host_registered_domain │ VARCHAR     │ YES     │ NULL    │ NULL    │ NULL    │
│ warc_record_length_av      │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ warc_record_length_median  │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_200_lote             │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_200_lote_pct         │ TINYINT     │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_3xx                  │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_4xx                  │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_5xx                  │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_gone                 │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_notModified          │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_other                │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_redirPerm            │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_redirTemp            │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ robots_200                 │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ robots_3xx                 │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ robots_4xx                 │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ robots_5xx                 │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ robots_gone                │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ robots_notModified         │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ robots_other               │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ robots_redirPerm           │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ robots_redirTemp           │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ hcrank_pos                 │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ hcrank_raw                 │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ hcrank100s                 │ INTEGER     │ YES     │ NULL    │ NULL    │ NULL    │
│ hcrank100p                 │ INTEGER     │ YES     │ NULL    │ NULL    │ NULL    │
│ prank_pos                  │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ prank_raw                  │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ prank100s                  │ INTEGER     │ YES     │ NULL    │ NULL    │ NULL    │
│ prank100p                  │ INTEGER     │ YES     │ NULL    │ NULL    │ NULL    │
│ is_us_federal              │ BOOLEAN     │ YES     │ NULL    │ NULL    │ NULL    │
│ crawl                      │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ v                          │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
└────────────────────────────┴─────────────┴─────────┴─────────┴─────────┴─────────┘
  38 rows                                                                6 columns
```
</details>

The schema has multiple parts:

### Partitioning

- `crawl` is the crawl year, `2020` or `2024`
- `v` is the version of the host index (currently `5`)

These are hive partition columns derived from the file path; filtering on `crawl`
lets duckdb skip the partitions you don't need.

### Hostnames

- `url_host_name`, `surt_host_name` and `url_host_name_reversed` are what they say they are
- `url_host_tld` and `url_host_registered_domain` are useful for wider queries
- `is_us_federal` is true for hosts that are actual US federal government websites

> [!NOTE]
> `is_us_federal` is probably correct for the .gov tld but is still a bit broad
> for other tlds.

### Crawl Summary

- `fetch_*` shows the count of status codes for this host. `fetch_200`, for example, is the number of successful fetches.
- `robots_*` does the same for robots.txt.
- `_lote` is "Languages Other Than English." `fetch_200_lote_pct` is the percentage of `fetch_200` that has a primary language other than English.

### Ranking information

We use a web graph to compute search engine-style ranks. We have 2
different algorithms (harmonic centrality and pagerank) and
(currently) 2 different ways of normalizing these ranks to the range
0-100. (Eventually we'll choose one of the two.) Ranks are computed
per crawl, so a host's rank in 2020 and 2024 can differ.

- `hcrank_raw`, `prank_raw`, `hcrank_pos`, `prank_pos` are unnormalized, so you should probably ignore them
- `hcrank100s` and `hcrank100p` are two different 0-100 normalizations of the harmonic centrality rank
- ditto for `prank100s` and `prank100p`

### Other

- `warc_record_length_av` and `warc_record_length_median` are the average and median size of all of the warc records for this host

## Examples

We'll query the index in Python using a helper script `select.py`. This
script takes 2 arguments, the SELECT and WHERE clauses, and exposes the dataset
as the view `eot_host`. By default it reads from the public HTTP mirror; no
download is required.

To read from S3 instead (requires AWS credentials), set `EOT_SOURCE=s3`:

```bash
EOT_SOURCE=s3 python select.py "crawl, COUNT(*) AS hosts, COUNT(*) FILTER (WHERE is_us_federal) AS federal_hosts" "url_host_tld = 'gov' GROUP BY crawl ORDER BY crawl"
```

```
┌───────┬────────┬───────────────┐
│ crawl │ hosts  │ federal_hosts │
│ int64 │ int64  │     int64     │
├───────┼────────┼───────────────┤
│  2020 │  52536 │         27889 │
│  2024 │ 108162 │         37248 │
└───────┴────────┴───────────────┘
```

Because the index spans two crawls, every query should either filter on a
specific `crawl` (e.g. `crawl = 2020`) or `GROUP BY crawl` (so the crawl year is part
of the output). The walkthrough below looks at **congress.gov** in EOT-2020;
we'll save some typing with a shell variable that pins the crawl:

```bash
WHERE="surt_host_name = 'gov,congress' AND crawl = 2020"
```

### Names

```bash
python select.py "url_host_name, surt_host_name, url_host_name_reversed, url_host_tld, url_host_registered_domain, is_us_federal" "$WHERE"
```

```
┌──────────────────┬────────────────┬────────────────────────┬──────────────┬────────────────────────────┬───────────────┐
│  url_host_name   │ surt_host_name │ url_host_name_reversed │ url_host_tld │ url_host_registered_domain │ is_us_federal │
│     varchar      │    varchar     │        varchar         │   varchar    │          varchar           │    boolean    │
├──────────────────┼────────────────┼────────────────────────┼──────────────┼────────────────────────────┼───────────────┤
│ www.congress.gov │ gov,congress   │ gov.congress.www       │ gov          │ congress.gov               │ true          │
└──────────────────┴────────────────┴────────────────────────┴──────────────┴────────────────────────────┴───────────────┘
```

### Crawl

```bash
python ./select.py "fetch_200, fetch_200_lote, fetch_200_lote_pct, fetch_gone, fetch_notModified" "$WHERE"
```

```
┌───────────┬────────────────┬────────────────────┬────────────┬───────────────────┐
│ fetch_200 │ fetch_200_lote │ fetch_200_lote_pct │ fetch_gone │ fetch_notModified │
│   int64   │     int64      │        int8        │   int64    │       int64       │
├───────────┼────────────────┼────────────────────┼────────────┼───────────────────┤
│   2819681 │            812 │                  0 │      46765 │                 0 │
└───────────┴────────────────┴────────────────────┴────────────┴───────────────────┘
```

```bash
python ./select.py "fetch_3xx, fetch_4xx, fetch_5xx" "$WHERE"
```

```
┌───────────┬───────────┬───────────┐
│ fetch_3xx │ fetch_4xx │ fetch_5xx │
│   int64   │   int64   │   int64   │
├───────────┼───────────┼───────────┤
│         0 │   1933097 │      2414 │
└───────────┴───────────┴───────────┘
```

> [!NOTE]
> That's an alarming 4xx result -- 404 and 410 are gone, these 4xxs might be bot defenses? Spoiler: they're all 400s.

### Robots

```bash
python ./select.py "robots_200, robots_gone, robots_notModified" "$WHERE"
```

```
┌────────────┬─────────────┬────────────────────┐
│ robots_200 │ robots_gone │ robots_notModified │
│   int64    │    int64    │       int64        │
├────────────┼─────────────┼────────────────────┤
│     771803 │       46765 │                  0 │
└────────────┴─────────────┴────────────────────┘
```

```bash
python ./select.py "robots_3xx, robots_4xx, robots_5xx" "$WHERE"
```

```
┌────────────┬────────────┬────────────┐
│ robots_3xx │ robots_4xx │ robots_5xx │
│   int64    │   int64    │   int64    │
├────────────┼────────────┼────────────┤
│          0 │    1933097 │       2414 │
└────────────┴────────────┴────────────┘
```

### Ranks

```bash
python ./select.py "hcrank100s, hcrank100p, prank100s, prank100p" "$WHERE"
```

```
┌────────────┬────────────┬───────────┬───────────┐
│ hcrank100s │ hcrank100p │ prank100s │ prank100p │
│   int32    │   int32    │   int32   │   int32   │
├────────────┼────────────┼───────────┼───────────┤
│        100 │        100 │       100 │       100 │
└────────────┴────────────┴───────────┴───────────┘
```

```bash
python ./select.py "hcrank_raw, hcrank_pos, prank_raw, prank_pos" "$WHERE"
```

```
┌────────────┬────────────┬───────────────────────┬───────────┐
│ hcrank_raw │ hcrank_pos │       prank_raw       │ prank_pos │
│   double   │   int64    │        double         │   int64   │
├────────────┼────────────┼───────────────────────┼───────────┤
│ 21142028.0 │       1172 │ 5.100846383868066e-06 │      1793 │
└────────────┴────────────┴───────────────────────┴───────────┘
```

### Subdomains

This needs a different WHERE clause (still pinned to one crawl):

```bash
python ./select.py "url_host_name, url_host_name_reversed, is_us_federal, hcrank100s, hcrank100p, prank100s, prank100p" "url_host_registered_domain = 'congress.gov' AND crawl = 2020"
```

```
SELECT url_host_name, url_host_name_reversed, is_us_federal, hcrank100s, hcrank100p, prank100s, prank100p FROM eot_host WHERE url_host_registered_domain = 'congress.gov' AND crawl = 2020
┌────────────────────────────┬────────────────────────────┬───────────────┬────────────┬────────────┬───────────┬───────────┐
│       url_host_name        │   url_host_name_reversed   │ is_us_federal │ hcrank100s │ hcrank100p │ prank100s │ prank100p │
│          varchar           │          varchar           │    boolean    │   int32    │   int32    │   int32   │   int32   │
├────────────────────────────┼────────────────────────────┼───────────────┼────────────┼────────────┼───────────┼───────────┤
│ smon.congress.gov          │ gov.congress.smon          │ true          │         33 │         28 │         0 │         0 │
│ lda.congress.gov           │ gov.congress.lda           │ true          │         73 │         83 │        96 │       100 │
│ test.congress.gov          │ gov.congress.test          │ true          │         62 │         69 │         0 │         0 │
│ www.congress.gov           │ gov.congress.www           │ true          │        100 │        100 │       100 │       100 │
│ beta.congress.gov          │ gov.congress.beta          │ true          │         98 │        100 │        98 │       100 │
│ bioguide.congress.gov      │ gov.congress.bioguide      │ true          │         98 │        100 │        98 │       100 │
│ crsreports.congress.gov    │ gov.congress.crsreports    │ true          │         98 │        100 │        98 │       100 │
│ constitution.congress.gov  │ gov.congress.constitution  │ true          │         97 │        100 │        97 │       100 │
│ bioguideretro.congress.gov │ gov.congress.bioguideretro │ true          │         97 │        100 │        97 │       100 │
└────────────────────────────┴────────────────────────────┴───────────────┴────────────┴────────────┴───────────┴───────────┘
```

## Let's ask some questions

### What are the highest ranked federal .gov hosts that we have nothing for?

```bash
python ./select.py "url_host_name_reversed, hcrank100s" "url_host_tld = 'gov' AND is_us_federal AND fetch_200 = 0 AND crawl = 2020 ORDER BY hcrank100s DESC LIMIT 10"
```

```
SELECT url_host_name_reversed, hcrank100s FROM eot_host WHERE url_host_tld = 'gov' AND is_us_federal AND fetch_200 = 0 AND crawl = 2020 ORDER BY hcrank100s DESC LIMIT 10
┌────────────────────────┬────────────┐
│ url_host_name_reversed │ hcrank100s │
│        varchar         │   int32    │
├────────────────────────┴────────────┤
│               0 rows                │
└─────────────────────────────────────┘
```
Well that was boring.

### What hosts have a large fraction of LOTE (languages other than english) pages?

```bash
python ./select.py "hcrank100s, url_host_name_reversed, fetch_200, fetch_200_lote_pct" "fetch_200_lote_pct > 10 AND url_host_tld = 'gov' AND is_us_federal AND crawl = 2020 ORDER BY hcrank100s DESC LIMIT 20"
```

```
SELECT hcrank100s, url_host_name_reversed, fetch_200, fetch_200_lote_pct FROM eot_host WHERE fetch_200_lote_pct > 10 AND url_host_tld = 'gov' AND is_us_federal AND crawl = 2020 ORDER BY hcrank100s DESC LIMIT 20
┌────────────┬────────────────────────────┬───────────┬────────────────────┐
│ hcrank100s │   url_host_name_reversed   │ fetch_200 │ fetch_200_lote_pct │
│   int32    │          varchar           │   int64   │        int8        │
├────────────┼────────────────────────────┼───────────┼────────────────────┤
│        100 │ gov.irs                    │    285880 │                 33 │
│        100 │ gov.usa                    │     10153 │                 12 │
│        100 │ gov.fema                   │     90320 │                 21 │
│        100 │ gov.medlineplus.www        │     80914 │                 22 │
│         99 │ gov.uscis                  │     30177 │                 13 │
│         99 │ gov.womenshealth.www       │     10399 │                 14 │
│         99 │ gov.atf.www                │     46592 │                 11 │
│         98 │ gov.uscg.navcen            │     58883 │                 15 │
│         98 │ gov.loc.cdn                │     67138 │                 17 │
│         98 │ gov.nasa.nascom.sohowww    │    258690 │                 15 │
│         98 │ gov.fec.transition         │     21291 │                 13 │
│         98 │ gov.usembassy.mx           │     12447 │                 26 │
│         98 │ gov.hhs.acf.ohs.eclkc      │     93908 │                 21 │
│         98 │ gov.vaccines               │      1401 │                 12 │
│         98 │ gov.nasa.gsfc.lambda       │     42493 │                 25 │
│         98 │ gov.econsumer.www          │      2104 │                 21 │
│         98 │ gov.nasa.nascom.soho       │    228403 │                 14 │
│         97 │ gov.america.share.www      │    158923 │                 32 │
│         97 │ gov.usgs.wr.planetarynames │      9058 │                 21 │
│         97 │ gov.cdc.espanol            │     16039 │                 20 │
├────────────┴────────────────────────────┴───────────┴────────────────────┤
│ 20 rows                                                        4 columns │
└──────────────────────────────────────────────────────────────────────────┘
```

### What are the top US federal government websites according to harmonic centrality?

```bash
python ./select.py "url_host_name, is_us_federal, fetch_200, hcrank_pos, hcrank_raw, hcrank100s" "is_us_federal AND crawl = 2020 ORDER BY hcrank_pos ASC LIMIT 10"
```

```
SELECT url_host_name, is_us_federal, fetch_200, hcrank_pos, hcrank_raw, hcrank100s FROM eot_host WHERE is_us_federal AND crawl = 2020 ORDER BY hcrank_pos ASC LIMIT 10
┌───────────────────────┬───────────────┬───────────┬────────────┬────────────┬────────────┐
│     url_host_name     │ is_us_federal │ fetch_200 │ hcrank_pos │ hcrank_raw │ hcrank100s │
│        varchar        │    boolean    │   int64   │   int64    │   double   │   int32    │
├───────────────────────┼───────────────┼───────────┼────────────┼────────────┼────────────┤
│ www.nasa.gov          │ true          │     26809 │        128 │ 23268830.0 │        100 │
│ cdc.gov               │ true          │    777329 │        140 │ 23232876.0 │        100 │
│ www.ncbi.nlm.nih.gov  │ true          │   3641163 │        178 │ 23025570.0 │        100 │
│ www.loc.gov           │ true          │   1746500 │        275 │ 22444530.0 │        100 │
│ www.whitehouse.gov    │ true          │     82638 │        318 │ 22309318.0 │        100 │
│ www.privacyshield.gov │ true          │      2712 │        368 │ 22142958.0 │        100 │
│ www.fda.gov           │ true          │     15471 │        383 │ 22108202.0 │        100 │
│ ftc.gov               │ true          │    281639 │        526 │ 21787366.0 │        100 │
│ justice.gov           │ true          │   2324332 │        550 │ 21741378.0 │        100 │
│ www.nps.gov           │ true          │    318360 │        572 │ 21716190.0 │        100 │
└───────────────────────┴───────────────┴───────────┴────────────┴────────────┴────────────┘
```

## Comparing EOT-2020 and EOT-2024

Because both crawls live in the same dataset, `GROUP BY crawl` gives a side-by-side
view. How many hosts, federal hosts, and successful fetches does each crawl have?

```bash
python ./select.py "crawl, COUNT(*) AS hosts, COUNT(*) FILTER (WHERE is_us_federal) AS federal_hosts, SUM(fetch_200) AS fetch_200" "TRUE GROUP BY crawl ORDER BY crawl"
```

```
┌───────┬─────────┬───────────────┬────────────┐
│ crawl │  hosts  │ federal_hosts │ fetch_200  │
│ int64 │  int64  │     int64     │   int128   │
├───────┼─────────┼───────────────┼────────────┤
│  2020 │ 1183935 │         29330 │ 1621287473 │
│  2024 │ 1187443 │         39687 │ 3688514985 │
└───────┴─────────┴───────────────┴────────────┘
```

And here's congress.gov in both crawls -- selecting `crawl` keeps the crawl year
in the output:

```bash
python ./select.py "crawl, fetch_200, fetch_3xx, fetch_4xx, robots_200, hcrank_pos, prank_pos" "surt_host_name = 'gov,congress' ORDER BY crawl"
```

```
┌───────┬───────────┬───────────┬───────────┬────────────┬────────────┬───────────┐
│ crawl │ fetch_200 │ fetch_3xx │ fetch_4xx │ robots_200 │ hcrank_pos │ prank_pos │
│ int64 │   int64   │   int64   │   int64   │   int64    │   int64    │   int64   │
├───────┼───────────┼───────────┼───────────┼────────────┼────────────┼───────────┤
│  2020 │   2819681 │         0 │   1933097 │     771803 │       1172 │      1793 │
│  2024 │   1147686 │         0 │    610001 │     415191 │        802 │      1775 │
└───────┴───────────┴───────────┴───────────┴────────────┴────────────┴───────────┘
```

The top federal hosts by harmonic centrality in EOT-2024:

```bash
python ./select.py "url_host_name, fetch_200, hcrank_pos, hcrank100s" "is_us_federal AND crawl = 2024 ORDER BY hcrank_pos ASC LIMIT 10"
```

```
┌─────────────────────────────┬───────────┬────────────┬────────────┐
│        url_host_name        │ fetch_200 │ hcrank_pos │ hcrank100s │
│           varchar           │   int64   │   int64    │   int32    │
├─────────────────────────────┼───────────┼────────────┼────────────┤
│ www.ncbi.nlm.nih.gov        │ 157549482 │         48 │        100 │
│ www.ftc.gov                 │    338452 │         77 │        100 │
│ whitehouse.gov              │    343131 │        218 │        100 │
│ www.irs.gov                 │   1828589 │        283 │        100 │
│ www.census.gov              │  13776171 │        303 │        100 │
│ www.pubmed.ncbi.nlm.nih.gov │  83388733 │        309 │        100 │
│ fda.gov                     │   1126806 │        314 │        100 │
│ www.nasa.gov                │   2151308 │        319 │        100 │
│ loc.gov                     │  17642789 │        352 │        100 │
│ www.justice.gov             │   1487783 │        361 │        100 │
└─────────────────────────────┴───────────┴────────────┴────────────┘
```

## Let's also look at the url index

[The url index schema is described elsewhere.](https://commoncrawl.org/columnar-index)
The url index is much larger than the host index, so we won't download it -- the
helper program `url-select.py` tells duckdb to directly access the parquet files
from s3 (this needs AWS credentials).

Like the host index, the url index is hive-partitioned -- by `crawl` -- so every
row carries a `crawl` column (`EOT-2020`, `EOT-2024`, ...) and the view is named
`eot_url`. Because this index is many GB per crawl, **always** narrow your query:
add `crawl = 'EOT-2024'` so duckdb can prune to one crawl, and filter on a host so
it can skip row groups.

> [!NOTE]
> In Common Crawl's normal url index there's a `subset = 'robotstxt'` hive
> partition. To find robots.txt records in the EOT url index, filter on
> `url_path = '/robots.txt'` instead.

### congress.gov's robots.txt across both crawls

congress.gov returns a 400 for its robots.txt. Has that changed between crawls?
A `GROUP BY crawl` answers it:

```bash
python ./url-select.py "crawl, fetch_status, COUNT(*)" "url_host_name = 'www.congress.gov' AND url_path = '/robots.txt' AND fetch_status >= 400 AND crawl IN ('EOT-2020','EOT-2024') GROUP BY crawl, fetch_status ORDER BY crawl, fetch_status"
```

```
SELECT crawl, fetch_status, COUNT(*) FROM eot_url WHERE url_host_name = 'www.congress.gov' AND url_path = '/robots.txt' AND fetch_status >= 400 AND crawl IN ('EOT-2020','EOT-2024') GROUP BY crawl, fetch_status ORDER BY crawl, fetch_status
┌──────────┬──────────────┬──────────────┐
│  crawl   │ fetch_status │ count_star() │
│ varchar  │    int16     │    int64     │
├──────────┼──────────────┼──────────────┤
│ EOT-2020 │          400 │          300 │
│ EOT-2024 │          403 │          457 │
│ EOT-2024 │          429 │            2 │
└──────────┴──────────────┴──────────────┘
```

The 400s from EOT-2020 became 403s (plus a couple of 429 rate-limits) in
EOT-2024 -- the bot defenses changed but congress.gov still won't serve its
robots.txt to the crawler.

### What are some of the LOTE urls, for example on irs.gov in EOT-2024?

```bash
python ./url-select.py "url, content_languages" "crawl = 'EOT-2024' AND url_host_registered_domain = 'irs.gov' AND url_path NOT LIKE '/es%' AND content_languages NOT LIKE 'eng%' LIMIT 10"
```

```
SELECT url, content_languages FROM eot_url WHERE crawl = 'EOT-2024' AND url_host_registered_domain = 'irs.gov' AND url_path NOT LIKE '/es%' AND content_languages NOT LIKE 'eng%' LIMIT 10
┌──────────────────────────────────────────────────────────────────────────────────────┬───────────────────┐
│                                         url                                          │ content_languages │
│                                       varchar                                        │      varchar      │
├──────────────────────────────────────────────────────────────────────────────────────┼───────────────────┤
│ https://www.irs.gov/66C_qrW8OH_5XoHt2HCVdwkXUQA/1Q5mzcVkXcmJG1iL/YxxmKQ/CzBbPG/pXR0s │ dan,eng,nld       │
│ https://www.irs.gov/help/information-about-federal-taxes-arabic                      │ ara,eng,kor       │
│ https://www.irs.gov/help/information-about-federal-taxes-arabic                      │ ara,eng,kor       │
│ https://www.irs.gov/help/information-about-federal-taxes-arabic                      │ ara,eng,kor       │
│ https://www.irs.gov/help/information-about-federal-taxes-arabic                      │ ara,eng,kor       │
│ https://www.irs.gov/help/information-about-federal-taxes-arabic                      │ ara,eng,kor       │
│ https://www.irs.gov/help/information-about-federal-taxes-arabic                      │ ara,eng,kor       │
│ https://www.irs.gov/help/information-about-federal-taxes-bengali                     │ ben,eng,asm       │
│ https://www.irs.gov/help/information-about-federal-taxes-bengali                     │ ben,eng,asm       │
│ https://www.irs.gov/help/information-about-federal-taxes-bengali                     │ ben,eng,asm       │
└──────────────────────────────────────────────────────────────────────────────────────┴───────────────────┘
```

This streams the matching urls (non-`/es` paths whose primary language isn't
English) directly from the EOT-2024 partition.
