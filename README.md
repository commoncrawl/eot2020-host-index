# eot2020-host-index

PRELIMINARY VERSION

This readme describes an host index database that aggregates
information about the contents in the End of Term Archive.

https://eotarchive.org/

It only has the year 2020 for now. The parquet file is stored on S3.

## Install the duckdb cli

https://duckdb.org/install/

and the python client library

```
pip install duckdb
```

## Schema

```
duckdb -c "DESCRIBE FROM 'https://data.commoncrawl.org/projects/eot2020-host-testing/EOT-2020-with-ranks-v2.parquet'"
```

<details><summary>click to see output</summary>

```
┌────────────────────────────┬─────────────┬─────────┬─────────┬─────────┬─────────┐
│        column_name         │ column_type │  null   │   key   │ default │  extra  │
│          varchar           │   varchar   │ varchar │ varchar │ varchar │ varchar │
├────────────────────────────┼─────────────┼─────────┼─────────┼─────────┼─────────┤
│ surt_host_name             │ VARCHAR     │ YES     │ NULL    │ NULL    │ NULL    │
│ url_host_name_reversed     │ VARCHAR     │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_200                  │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ url_host_tld               │ VARCHAR     │ YES     │ NULL    │ NULL    │ NULL    │
│ url_host_registered_domain │ VARCHAR     │ YES     │ NULL    │ NULL    │ NULL    │
│ warc_record_length_av      │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ warc_record_length_median  │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_200_lote             │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_200_lote_pct         │ INTEGER     │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_3xx                  │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_4xx                  │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_5xx                  │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_gone                 │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_notModified          │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_other                │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_redirPerm            │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ fetch_redirTemp            │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ robots_200                 │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ robots_3xx                 │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ robots_4xx                 │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ robots_5xx                 │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ robots_gone                │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ robots_notModified         │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ robots_other               │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ robots_redirPerm           │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
│ robots_redirTemp           │ DOUBLE      │ YES     │ NULL    │ NULL    │ NULL    │
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
│ 35 rows                                                                6 columns │
└──────────────────────────────────────────────────────────────────────────────────┘
```
</details>

The schema has multiple parts:

### Hostnames

- surt_host_name and url_host_name_reversed are what they say they are
- url_host_tld and urL_host_registered_domain are useful for wider queries
- is_us_federal is true for hosts that are actual US federal government websites

BUG: is_us_federal is too broad in the v2 testing database. It's probably correct
for the .gov tld.

### Crawl Summary

- fetch_* shows the count of status codes for this host. fetch_200, for example, is the number of successful fetches.
- robots_* does the same for robots.txt.
- "lote" is "Languages Other Than English." fetch_200_lote_pct is the percentage of fetch_200 that has a primary language other than English.

BUG: all of the fetch_ and robots_ should be integers.

### Ranking information

We use a web graph to compute search engine-style ranks. We have 2
different algorithms (harmonic centrality and pagerank) and
(currently) 2 different ways of normalizing these ranks to the range
0-100. (Eventually we'll choose one of the two.)

- hcrank_raw, prank_raw, hcrank_pos, prank_pos are unnormalized, so you should probably ignore them
- hcrank100s and hcrank100p are two different 0-100 normalizations of the harmonic centrality rank
- ditto for prank100s and prank100p

### Other

- warc_record_length_av and _median are the average and median size of all of the warc records for this host

## Examples

Let's look at an entire row for congress.gov. We'll do it in python because the python library
is more willing to interact directly with s3 than the duckdb cli client. The script is `select.py`
and it takes 2 arguments, the SELECT and WHERE clauses. We'll use some shell variables to reduce typing.

Since the parquet file is only 80 megabytes, we'll download it

```
wget https://data.commoncrawl.org/projects/eot2020-host-testing/EOT-2020-with-ranks-v2.parquet'
```

And to save typing:
```
WHERE="surt_host_name = 'gov,congress'"
```

### Names

```
python select.py "surt_host_name, url_host_name_reversed, url_host_tld, url_host_registered_domain, is_us_federal" "$WHERE"

┌────────────────┬────────────────────────┬──────────────┬────────────────────────────┬───────────────┐
│ surt_host_name │ url_host_name_reversed │ url_host_tld │ url_host_registered_domain │ is_us_federal │
│    varchar     │        varchar         │   varchar    │          varchar           │    boolean    │
├────────────────┼────────────────────────┼──────────────┼────────────────────────────┼───────────────┤
│ gov,congress   │ gov.congress.www       │ gov          │ congress.gov               │ true          │
└────────────────┴────────────────────────┴──────────────┴────────────────────────────┴───────────────┘
```
### Crawl

```
python ./select.py "fetch_200, fetch_200_lote, fetch_200_lote_pct, fetch_gone, fetch_notModified"

┌───────────┬────────────────┬────────────────────┬────────────┬───────────────────┐
│ fetch_200 │ fetch_200_lote │ fetch_200_lote_pct │ fetch_gone │ fetch_notModified │
│  double   │     double     │       int32        │   double   │      double       │
├───────────┼────────────────┼────────────────────┼────────────┼───────────────────┤
│ 2819681.0 │          812.0 │                  0 │    46765.0 │               0.0 │
└───────────┴────────────────┴────────────────────┴────────────┴───────────────────┘
```

```
python ./select.py "fetch_3xx, fetch_4xx, fetch_5xx"

┌───────────┬───────────┬───────────┐
│ fetch_3xx │ fetch_4xx │ fetch_5xx │
│  double   │  double   │  double   │
├───────────┼───────────┼───────────┤
│       0.0 │ 1933097.0 │    2414.0 │
└───────────┴───────────┴───────────┘
```

NOTE: that's an alarming 4xx result -- 404 and 410 are gone, these 4xxs might be bot defenses? Spoiler: they're all 400s.

### Robots

```
python ./select.py "robots_200, robots_gone, robots_notModified"

┌────────────┬─────────────┬────────────────────┐
│ robots_200 │ robots_gone │ robots_notModified │
│   double   │   double    │       double       │
├────────────┼─────────────┼────────────────────┤
│   771803.0 │     46765.0 │                0.0 │
└────────────┴─────────────┴────────────────────┘
```

```
python ./select.py "robots_3xx, robots_4xx, robots_5xx"

┌────────────┬────────────┬────────────┐
│ robots_3xx │ robots_4xx │ robots_5xx │
│   double   │   double   │   double   │
├────────────┼────────────┼────────────┤
│        0.0 │  1933097.0 │     2414.0 │
└────────────┴────────────┴────────────┘
```

### Ranks

```
python ./select.py "hcrank100s, hcrank100p, prank100s, prank100p"

┌────────────┬────────────┬───────────┬───────────┐
│ hcrank100s │ hcrank100p │ prank100s │ prank100p │
│   int32    │   int32    │   int32   │   int32   │
├────────────┼────────────┼───────────┼───────────┤
│       NULL │       NULL │      NULL │      NULL │
└────────────┴────────────┴───────────┴───────────┘
```

BUG: yeah these shouldn't be nulls. SPOILER: it's a www/not-www issue on my side.

```
python ./select.py "hcrank_raw, hcrank_pos, prank_raw, prank_pos"

┌────────────┬────────────┬───────────┬───────────┐
│ hcrank_raw │ hcrank_pos │ prank_raw │ prank_pos │
│   double   │   int64    │  double   │   int64   │
├────────────┼────────────┼───────────┼───────────┤
│       NULL │       NULL │      NULL │      NULL │
└────────────┴────────────┴───────────┴───────────┘
```

BUG: ditto

### Subdomains

This needs a different WHERE clause:

```
python ./select.py "url_host_name_reversed, is_us_federal, hcrank100s, hcrank100p, prank100s, prank100p" "url_host_registered_domain = 'congress.gov'"
SELECT url_host_name_reversed, is_us_federal, hcrank100s, hcrank100p, prank100s, prank100p FROM eot2020_host WHERE url_host_registered_domain = 'congress.gov'
┌────────────────────────────┬───────────────┬────────────┬────────────┬───────────┬───────────┐
│   url_host_name_reversed   │ is_us_federal │ hcrank100s │ hcrank100p │ prank100s │ prank100p │
│          varchar           │    boolean    │   int32    │   int32    │   int32   │   int32   │
├────────────────────────────┼───────────────┼────────────┼────────────┼───────────┼───────────┤
│ gov.congress.test          │ true          │         62 │         69 │       -22 │        -7 │
│ gov.congress.lda           │ true          │         73 │         83 │        96 │       100 │
│ gov.congress.beta          │ true          │         98 │        100 │        98 │       100 │
│ gov.congress.bioguide      │ true          │         98 │        100 │        98 │       100 │
│ gov.congress.crsreports    │ true          │         98 │        100 │        98 │       100 │
│ gov.congress.constitution  │ true          │         97 │        100 │        97 │       100 │
│ gov.congress.bioguideretro │ true          │         97 │        100 │        97 │       100 │
│ gov.congress.smon          │ true          │         33 │         28 │       -90 │       -11 │
│ gov.congress.www           │ true          │       NULL │       NULL │      NULL │      NULL │
└────────────────────────────┴───────────────┴────────────┴────────────┴───────────┴───────────┘
```

BUG: well there's the ranking bug cause, it's www vs. non-www.

## Let's ask some questions

### What are the highest ranked federal .gov hosts that we have nothing for?

```
python ./select.py "url_host_name_reversed, hcrank100s" "url_host_tld = 'gov' AND is_us_federal AND fetch_200 = 0 ORDER BY hcrank100s DESC LIMIT 10"
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

```
python ./select.py "hcrank100s, url_host_name_reversed, fetch_200, fetch_200_lote_pct" "fetch_200_lote_pct > 10 AND url_host_tld = 'gov' AND is_us_federal ORDER BY hcrank100s DESC LIMIT 20"
SELECT hcrank100s, url_host_name_reversed, fetch_200, fetch_200_lote_pct FROM eot2020_host WHERE fetch_200_lote_pct > 10 AND url_host_tld = 'gov' AND is_us_federal ORDER BY hcrank100s DESC LIMIT 20
┌────────────┬────────────────────────────┬───────────┬────────────────────┐
│ hcrank100s │   url_host_name_reversed   │ fetch_200 │ fetch_200_lote_pct │
│   int32    │          varchar           │  double   │       int32        │
├────────────┼────────────────────────────┼───────────┼────────────────────┤
│        100 │ gov.irs                    │  285880.0 │                 33 │
│        100 │ gov.fema                   │   90320.0 │                 21 │
│        100 │ gov.medlineplus            │   80914.0 │                 22 │
│         99 │ gov.uscis                  │   30177.0 │                 13 │
│         99 │ gov.womenshealth           │   10399.0 │                 14 │
│         98 │ gov.loc.cdn                │   67138.0 │                 17 │
│         98 │ gov.nasa.nascom.sohowww    │  258690.0 │                 15 │
│         98 │ gov.fec.transition         │   21291.0 │                 13 │
│         98 │ gov.usembassy.mx           │   12447.0 │                 26 │
│         98 │ gov.hhs.acf.ohs.eclkc      │   93908.0 │                 21 │
│         98 │ gov.nasa.gsfc.lambda       │   42493.0 │                 25 │
│         98 │ gov.nasa.nascom.soho       │  228403.0 │                 14 │
│         97 │ gov.usembassy.kr           │    8177.0 │                 11 │
│         97 │ gov.usgs.wr.planetarynames │    9058.0 │                 21 │
│         97 │ gov.nasa.gsfc.asd          │   37567.0 │                 13 │
│         97 │ gov.eeoc.www1              │   51786.0 │                 12 │
│         97 │ gov.usembassy.de           │   17002.0 │                 38 │
│         97 │ gov.cdc.espanol            │   16039.0 │                 20 │
│         97 │ gov.nasa.llis              │     621.0 │                 63 │
│         97 │ gov.loc.international      │     991.0 │                 19 │
├────────────┴────────────────────────────┴───────────┴────────────────────┤
│ 20 rows                                                        4 columns │
└──────────────────────────────────────────────────────────────────────────┘
```

## Let's also look at the url index

The url index schema is described elsewhere. We won't download the entire
index like we did before -- the helper program `url-select.py` tells
duckdb to directly access the parquet files from s3.

### What are those 4xxs for congress.gov?

First let's look at all non-200s:

```
python ./url-select.py "url, fetch_status" "url_host_tld = 'gov' AND url_host_registered_domain = 'congress.gov' AND fetch_status <> 200 LIMIT 10"
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

```
python ./url-select.py "url, fetch_status" "url_host_tld = 'gov' AND url_host_registered_domain = 'congress.gov' AND fetch_status >= 400 LIMIT 10"
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

How about for robots?

```
python ./url-select.py "url, fetch_status" "url_host_tld = 'gov' AND url_host_registered_domain = 'congress.gov' AND fetch_status >= 400 AND url_path = '/robots.txt' LIMIT 10"
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
```
python ./url-select.py "url, fetch_status" "url_host_tld = 'gov' AND url_host_registered_domain = 'congress.gov' AND fetch_status > 400 AND url_path = '/robots.txt' LIMIT 10"
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
Boring.
