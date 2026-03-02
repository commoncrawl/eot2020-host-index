# eot2020-host-index

PRELIMINARY VERSION

This readme describes an host index database that aggregates
information about the contents in the End of Term Archive.

https://eotarchive.org/

It only has the year 2020 for now. The parquet file is stored on S3 but also accessible via HTTP.

## Install the duckdb cli

https://duckdb.org/install/

and the python client library

```bash
pip install duckdb
```

## Schema

```bash
duckdb -c "DESCRIBE FROM 'https://data.commoncrawl.org/projects/eot2020-host-testing/EOT-2020-with-ranks-v4.parquet'"
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
│ is_us_federal              │ BOOLEAN     │ YES     │ NULL    │ NULL    │ NULL    │
│ hcrank_pos                 │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ hcrank_raw                 │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ hcrank100s                 │ INTEGER     │ YES     │ NULL    │ NULL    │ NULL    │
│ hcrank100p                 │ INTEGER     │ YES     │ NULL    │ NULL    │ NULL    │
│ prank_pos                  │ BIGINT      │ YES     │ NULL    │ NULL    │ NULL    │
│ prank_raw                  │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ prank100s                  │ INTEGER     │ YES     │ NULL    │ NULL    │ NULL    │
│ prank100p                  │ INTEGER     │ YES     │ NULL    │ NULL    │ NULL    │
├────────────────────────────┴─────────────┴─────────┴─────────┴─────────┴─────────┤
│ 36 rows                                                                6 columns │
└──────────────────────────────────────────────────────────────────────────────────┘
```
</details>

The schema has multiple parts:

### Hostnames

- `url_host_name`, `surt_host_name` and `url_host_name_reversed` are what they say they are
- `url_host_tld` and `url_host_registered_domain` are useful for wider queries
- `is_us_federal` is true for hosts that are actual US federal government websites

> [!NOTE]
> BUG: `is_us_federal` is too broad in the v2 testing database. It's probably correct for the .gov tld. This bug is resolved in V4.


### Crawl Summary

- `fetch_*` shows the count of status codes for this host. `fetch_200`, for example, is the number of successful fetches.
- `robots_*` does the same for robots.txt.
- `_lote` is "Languages Other Than English." `fetch_200_lote_pct` is the percentage of `fetch_200` that has a primary language other than English.

> [!NOTE]
> BUG: In the v2 testing database, all of the `fetch_` and `robots_` should be integers.

### Ranking information

We use a web graph to compute search engine-style ranks. We have 2
different algorithms (harmonic centrality and pagerank) and
(currently) 2 different ways of normalizing these ranks to the range
0-100. (Eventually we'll choose one of the two.)

- `hcrank_raw`, `prank_raw`, `hcrank_pos`, `prank_pos` are unnormalized, so you should probably ignore them
- `hcrank100s` and `hcrank100p` are two different 0-100 normalizations of the harmonic centrality rank
- ditto for `prank100s` and `prank100p`

### Other

- `warc_record_length_av` and `warc_record_length_median` are the average and median size of all of the warc records for this host

## Examples

Let's look at an entire row for **congress.gov**. We'll do it in Python
using a helper script `select.py`. This script takes 2 arguments, the
SELECT and WHERE clauses. We'll use some shell variables to reduce
typing.

Since the parquet file is only 80 megabytes, we'll download it

```bash
wget https://data.commoncrawl.org/projects/eot2020-host-testing/EOT-2020-with-ranks-v4.parquet
```

And to save typing:
```bash
WHERE="surt_host_name = 'gov,congress'"
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

> [!WARNING]
> In V2, these rank values were nulls due to a www/not-www issue that was fixed in V3.


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

This needs a different WHERE clause:

```bash
python ./select.py "url_host_name, url_host_name_reversed, is_us_federal, hcrank100s, hcrank100p, prank100s, prank100p" "url_host_registered_domain = 'congress.gov'"
```

```
SELECT url_host_name, url_host_name_reversed, is_us_federal, hcrank100s, hcrank100p, prank100s, prank100p FROM eot2020_host WHERE url_host_registered_domain = 'congress.gov'
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
python ./select.py "url_host_name_reversed, hcrank100s" "url_host_tld = 'gov' AND is_us_federal AND fetch_200 = 0 ORDER BY hcrank100s DESC LIMIT 10"
```

```
SELECT url_host_name_reversed, hcrank100s FROM eot2020_host WHERE url_host_tld = 'gov' AND is_us_federal AND fetch_200 = 0 ORDER BY hcrank100s DESC LIMIT 10
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
python ./select.py "hcrank100s, url_host_name_reversed, fetch_200, fetch_200_lote_pct" "fetch_200_lote_pct > 10 AND url_host_tld = 'gov' AND is_us_federal ORDER BY hcrank100s DESC LIMIT 20"
```

```
SELECT hcrank100s, url_host_name_reversed, fetch_200, fetch_200_lote_pct FROM eot2020_host WHERE fetch_200_lote_pct > 10 AND url_host_tld = 'gov' AND is_us_federal ORDER BY hcrank100s DESC LIMIT 20
┌────────────┬─────────────────────────┬───────────┬────────────────────┐
│ hcrank100s │ url_host_name_reversed  │ fetch_200 │ fetch_200_lote_pct │
│   int32    │         varchar         │   int64   │        int8        │
├────────────┼─────────────────────────┼───────────┼────────────────────┤
│        100 │ gov.irs                 │    285880 │                 33 │
│        100 │ gov.usa                 │     10153 │                 12 │
│        100 │ gov.fema                │     90320 │                 21 │
│        100 │ gov.medlineplus.www     │     80914 │                 22 │
│         99 │ gov.uscis               │     30177 │                 13 │
│         99 │ gov.womenshealth.www    │     10399 │                 14 │
│         99 │ gov.atf.www             │     46592 │                 11 │
│         98 │ gov.uscg.navcen         │     58883 │                 15 │
│         98 │ gov.loc.cdn             │     67138 │                 17 │
│         98 │ gov.nasa.nascom.sohowww │    258690 │                 15 │
│         98 │ gov.fec.transition      │     21291 │                 13 │
│         98 │ gov.usembassy.mx        │     12447 │                 26 │
│         98 │ gov.hhs.acf.ohs.eclkc   │     93908 │                 21 │
│         98 │ gov.vaccines            │      1401 │                 12 │
│         98 │ gov.nasa.gsfc.lambda    │     42493 │                 25 │
│         98 │ gov.econsumer.www       │      2104 │                 21 │
│         98 │ gov.nasa.nascom.soho    │    228403 │                 14 │
│         97 │ gov.usembassy.kr        │      8177 │                 11 │
│         97 │ gov.america.share.www   │    158923 │                 32 │
│         97 │ gov.nasa.gsfc.asd       │     37567 │                 13 │
├────────────┴─────────────────────────┴───────────┴────────────────────┤
│ 20 rows                                                     4 columns │
└───────────────────────────────────────────────────────────────────────┘
```

## Let's also look at the url index

[The url index schema is described elsewhere.](https://commoncrawl.org/columnar-index)
We won't download the entire index like we did before -- the helper
program `url-select.py` tells duckdb to directly access the parquet
files from s3.

### What are those 4xxs for congress.gov?

First let's look at all non-200s:

```bash
python ./url-select.py "url, fetch_status" "url_host_tld = 'gov' AND url_host_registered_domain = 'congress.gov' AND fetch_status <> 200 LIMIT 10"
```

```
SELECT url, fetch_status FROM eot2020_url WHERE url_host_tld = 'gov' AND url_host_registered_domain = 'congress.gov' AND fetch_status <> 200 LIMIT 10
┌───────────────────────────┬──────────────┐
│            url            │ fetch_status │
│          varchar          │    int16     │
├───────────────────────────┼──────────────┤
│ http://www.congress.gov// │          301 │
│ http://www.congress.gov/  │          301 │
│ https://www.congress.gov/ │          400 │
│ http://congress.gov/      │          301 │
│ http://www.congress.gov/  │          301 │
│ https://congress.gov/     │          302 │
│ http://congress.gov/      │          301 │
│ http://www.congress.gov/  │          301 │
│ https://congress.gov/     │          302 │
│ http://congress.gov/      │          301 │
├───────────────────────────┴──────────────┤
│ 10 rows                        2 columns │
└──────────────────────────────────────────┘
```

OK but what about 4xx/5xx?

```bash
python ./url-select.py "url, fetch_status" "url_host_tld = 'gov' AND url_host_registered_domain = 'congress.gov' AND fetch_status >= 400 LIMIT 10"
```

```
SELECT url, fetch_status FROM eot2020_url WHERE url_host_tld = 'gov' AND url_host_registered_domain = 'congress.gov' AND fetch_status >= 400 LIMIT 10
┌──────────────────────────────────────────────────────────────────────┬──────────────┐
│                                 url                                  │ fetch_status │
│                               varchar                                │    int16     │
├──────────────────────────────────────────────────────────────────────┼──────────────┤
│ https://www.congress.gov/                                            │          400 │
│ https://www.congress.gov/%20-%20legislation-text                     │          404 │
│ https://www.congress.gov/'/'                                         │          404 │
│ https://www.congress.gov/103/bills/hjres281/BILLS-103hjres281cph.pdf │          400 │
│ https://www.congress.gov/103/bills/hr1804/BILLS-103hr1804pcs.pdf     │          400 │
│ https://www.congress.gov/103/bills/hr1834/BILLS-103hr1834ih.pdf      │          400 │
│ https://www.congress.gov/103/bills/hr20/BILLS-103hr20cds.pdf         │          400 │
│ https://www.congress.gov/103/bills/hr2876/BILLS-103hr2876eh.pdf      │          400 │
│ https://www.congress.gov/103/bills/hr3508/BILLS-103hr3508eh.pdf      │          503 │
│ https://www.congress.gov/103/bills/hr4165/BILLS-103hr4165ih.pdf      │          400 │
├──────────────────────────────────────────────────────────────────────┴──────────────┤
│ 10 rows                                                                   2 columns │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

404s are fetch_gone, so the 400s and 503 are concerning.

How about for robots? (Note the trick of `url_path = '/robots.txt'` ... in Common Crawl's normal url index
there's `subset = 'robotstxt'`, but that hive partition does not exist in the EOT2020 url index.)

```bash
python ./url-select.py "url, fetch_status" "url_host_tld = 'gov' AND url_host_registered_domain = 'congress.gov' AND fetch_status >= 400 AND url_path = '/robots.txt' LIMIT 10"
```

```
SELECT url, fetch_status FROM eot2020_url WHERE url_host_tld = 'gov' AND url_host_registered_domain = 'congress.gov' AND fetch_status >= 400 AND url_path = '/robots.txt' LIMIT 10
┌─────────────────────────────────────┬──────────────┐
│                 url                 │ fetch_status │
│               varchar               │    int16     │
├─────────────────────────────────────┼──────────────┤
│ https://www.congress.gov/robots.txt │          400 │
│ https://www.congress.gov/robots.txt │          400 │
│ https://www.congress.gov/robots.txt │          400 │
│ https://www.congress.gov/robots.txt │          400 │
│ https://www.congress.gov/robots.txt │          400 │
│ https://www.congress.gov/robots.txt │          400 │
│ https://www.congress.gov/robots.txt │          400 │
│ https://www.congress.gov/robots.txt │          400 │
│ https://www.congress.gov/robots.txt │          400 │
│ https://www.congress.gov/robots.txt │          400 │
├─────────────────────────────────────┴──────────────┤
│ 10 rows                                  2 columns │
└────────────────────────────────────────────────────┘
```

Hm, and are there non-400s?

```bash
python ./url-select.py "url, fetch_status" "url_host_tld = 'gov' AND url_host_registered_domain = 'congress.gov' AND fetch_status > 400 AND url_path = '/robots.txt' LIMIT 10"
```

```
SELECT url, fetch_status FROM eot2020_url WHERE url_host_tld = 'gov' AND url_host_registered_domain = 'congress.gov' AND fetch_status > 400 AND url_path = '/robots.txt' LIMIT 10
┌─────────────────────────────────────────┬──────────────┐
│                   url                   │ fetch_status │
│                 varchar                 │    int16     │
├─────────────────────────────────────────┼──────────────┤
│ http://bioguide.congress.gov/robots.txt │          404 │
│ http://bioguide.congress.gov/robots.txt │          404 │
│ http://bioguide.congress.gov/robots.txt │          404 │
│ http://bioguide.congress.gov/robots.txt │          404 │
│ http://bioguide.congress.gov/robots.txt │          404 │
│ http://bioguide.congress.gov/robots.txt │          404 │
│ http://bioguide.congress.gov/robots.txt │          404 │
│ http://bioguide.congress.gov/robots.txt │          404 │
│ http://bioguide.congress.gov/robots.txt │          404 │
│ http://bioguide.congress.gov/robots.txt │          404 │
├─────────────────────────────────────────┴──────────────┤
│ 10 rows                                      2 columns │
└────────────────────────────────────────────────────────┘
```

Whoops, I meant to only look at the host congress.gov! Which has 2 host names, congress.gov and www.congress.gov. Having already
noticed that congress.gov is a redirect, let's just look at www.congress.gov:

```
python ./url-select.py "url, fetch_status" "url_host_tld = 'gov' AND url_host_name = 'www.congress.gov' AND fetch_status >= 400 AND url_path = '/robots.txt' LIMIT 10"
SELECT url, fetch_status FROM eot2020_url WHERE url_host_tld = 'gov' AND url_host_name = 'www.congress.gov' AND fetch_status >= 400 AND url_path = '/robots.txt' LIMIT 10
┌─────────────────────────────────────┬──────────────┐
│                 url                 │ fetch_status │
│               varchar               │    int16     │
├─────────────────────────────────────┼──────────────┤
│ https://www.congress.gov/robots.txt │          400 │
│ https://www.congress.gov/robots.txt │          400 │
│ https://www.congress.gov/robots.txt │          400 │
│ https://www.congress.gov/robots.txt │          400 │
│ https://www.congress.gov/robots.txt │          400 │
│ https://www.congress.gov/robots.txt │          400 │
│ https://www.congress.gov/robots.txt │          400 │
│ https://www.congress.gov/robots.txt │          400 │
│ https://www.congress.gov/robots.txt │          400 │
│ https://www.congress.gov/robots.txt │          400 │
├─────────────────────────────────────┴──────────────┤
│ 10 rows                                  2 columns │
└────────────────────────────────────────────────────┘
```

Are they all 400s? Let's try a GROUP BY:

```
python ./url-select.py "fetch_status, COUNT(*)" "url_host_tld = 'gov' AND url_host_name = 'www.congress.gov' AND fetch_status >= 400 AND url_path = '/robots.txt' GROUP BY fetch_status"
SELECT fetch_status, COUNT(*) FROM eot2020_url WHERE url_host_tld = 'gov' AND url_host_name = 'www.congress.gov' AND fetch_status >= 400 AND url_path = '/robots.txt' GROUP BY fetch_status
┌──────────────┬──────────────┐
│ fetch_status │ count_star() │
│    int16     │    int64     │
├──────────────┼──────────────┤
│          400 │          300 │
└──────────────┴──────────────┘
```

### What are some of the LOTE urls, for example on irs.gov?

```
python ./url-select.py "url, content_languages" "url_host_registered_domain = 'irs.gov' AND content_languages NOT LIKE 'eng%' LIMIT 10"
SELECT url, content_languages FROM eot2020_url WHERE url_host_registered_domain = 'irs.gov' AND content_languages NOT LIKE 'eng%' LIMIT 10
┌────────────────────────┬───────────────────┐
│          url           │ content_languages │
│        varchar         │      varchar      │
├────────────────────────┼───────────────────┤
│ https://www.irs.gov/es │ spa,eng,kor       │
│ https://www.irs.gov/es │ spa,eng,kor       │
│ https://www.irs.gov/es │ spa,eng,kor       │
│ https://www.irs.gov/es │ spa,eng,kor       │
│ https://www.irs.gov/es │ spa,eng,kor       │
│ https://www.irs.gov/es │ spa,eng,kor       │
│ https://www.irs.gov/es │ spa,eng,kor       │
│ https://www.irs.gov/es │ spa,eng,kor       │
│ https://www.irs.gov/es │ spa,eng,kor       │
│ https://www.irs.gov/es │ spa,eng,kor       │
├────────────────────────┴───────────────────┤
│ 10 rows                          2 columns │
└────────────────────────────────────────────┘
```
Boring. Let's look at non-'/es' paths:

```
python ./url-select.py "url, content_languages" "url_host_registered_domain = 'irs.gov' AND url_path <> '/es' AND content_languages NOT LIKE 'eng%' LIMIT 10"
SELECT url, content_languages FROM eot2020_url WHERE url_host_registered_domain = 'irs.gov' AND url_path <> '/es' AND content_languages NOT LIKE 'eng%' LIMIT 10
┌─────────────────────────────────────────────────────────────────────────────────────────────────────┬───────────────────┐
│                                                 url                                                 │ content_languages │
│                                               varchar                                               │      varchar      │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────┤
│ https://www.irs.gov/es/'https://www.irs.gov/es'                                                     │ spa,eng,kor       │
│ https://www.irs.gov/es/'https://www.irs.gov/es'                                                     │ spa,eng,kor       │
│ https://www.irs.gov/es/'https://www.irs.gov/es'                                                     │ spa,eng,kor       │
│ https://www.irs.gov/es/'https://www.irs.gov/es'                                                     │ spa,eng,kor       │
│ https://www.irs.gov/es/'https://www.irs.gov/es'                                                     │ spa,eng,kor       │
│ https://www.irs.gov/es/'https://www.irs.gov/es'                                                     │ spa,eng,kor       │
│ https://www.irs.gov/es/'https://www.irs.gov/es/charities-and-nonprofits'                            │ spa,eng,kor       │
│ https://www.irs.gov/es/'https://www.irs.gov/es/coronavirus-tax-relief-and-economic-impact-payments' │ spa,eng,kor       │
│ https://www.irs.gov/es/'https://www.irs.gov/es/coronavirus-tax-relief-and-economic-impact-payments' │ spa,eng,kor       │
│ https://www.irs.gov/es/'https://www.irs.gov/es/coronavirus-tax-relief-and-economic-impact-payments' │ spa,eng,kor       │
├─────────────────────────────────────────────────────────────────────────────────────────────────────┴───────────────────┤
│ 10 rows                                                                                                       2 columns │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
Those are all mangled. Let's try excluding '/es%':

```
python ./url-select.py "url, content_languages" "url_host_registered_domain = 'irs.gov' AND url_path NOT LIKE '/es%' AND content_languages NOT LIKE 'eng%' LIMIT 10" 
SELECT url, content_languages FROM eot2020_url WHERE url_host_registered_domain = 'irs.gov' AND url_path NOT LIKE '/es%' AND content_languages NOT LIKE 'eng%' LIMIT 10
┌──────────────────────────────────────────────────────────────────────────────┬───────────────────┐
│                                     url                                      │ content_languages │
│                                   varchar                                    │      varchar      │
├──────────────────────────────────────────────────────────────────────────────┼───────────────────┤
│ https://www.irs.gov/help/information-about-federal-taxes-arabic              │ ara,eng,xho       │
│ https://www.irs.gov/help/information-about-federal-taxes-arabic              │ ara,eng,xho       │
│ https://www.irs.gov/help/information-about-federal-taxes-bengali             │ ben,eng,xho       │
│ https://www.irs.gov/help/information-about-federal-taxes-bengali             │ ben,eng,xho       │
│ https://www.irs.gov/help/information-about-federal-taxes-chinese-traditional │ zho,eng,ind       │
│ https://www.irs.gov/help/information-about-federal-taxes-chinese-traditional │ zho,eng,ind       │
│ https://www.irs.gov/help/information-about-federal-taxes-farsi               │ fas,eng,urd       │
│ https://www.irs.gov/help/information-about-federal-taxes-farsi               │ fas,eng,urd       │
│ https://www.irs.gov/help/information-about-federal-taxes-french              │ fra,eng,kor       │
│ https://www.irs.gov/help/information-about-federal-taxes-french              │ fra,eng,kor       │
├──────────────────────────────────────────────────────────────────────────────┴───────────────────┤
│ 10 rows                                                                                2 columns │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```
Jackpot!
