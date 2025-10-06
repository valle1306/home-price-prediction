# ---- Packages ----
if (!requireNamespace("duckdb", quietly = TRUE)) install.packages("duckdb")
if (!requireNamespace("DBI", quietly = TRUE)) install.packages("DBI")
if (!requireNamespace("janitor", quietly = TRUE)) install.packages("janitor")
if (!requireNamespace("stringr", quietly = TRUE)) install.packages("stringr")

library(DBI)
library(duckdb)
library(janitor)
library(stringr)

cols <- DBI::dbGetQuery(con, "PRAGMA table_info('mls_raw')")$name
has  <- function(x) x %in% cols
quote_ident <- function(x) DBI::dbQuoteIdentifier(con, x)

# Helpers
first_existing <- function(candidates) {
  cands <- candidates[candidates %in% cols]
  if (length(cands) == 0) return(NA_character_)
  cands[[1]]
}
coalesce_trycast <- function(candidates, cast = "DOUBLE") {
  cands <- candidates[candidates %in% cols]
  if (!length(cands)) return("NULL")
  paste0(
    "COALESCE(",
    paste0("TRY_CAST(", sapply(cands, function(c) as.character(quote_ident(c))), " AS ", cast, ")",
           collapse = ", "),
    ")"
  )
}

# Common variant names
price_close_vars <- c("close_price","closeprice","soldprice","closingprice")
price_list_vars  <- c("list_price","listprice","askingprice","lp")
price_orig_vars  <- c("original_list_price","originallistprice","originalprice")

area_vars        <- c("living_area","livingarea","building_area_total","buildingareatotal","totallivingsqft","totallivingarea")
state_vars       <- c("state_or_province","stateorprovince","state","province")
ptype_vars       <- c("property_type","propertytype","type")
city_vars        <- c("city","municipality","locality")

date_list_vars   <- c("listing_contract_date","listingcontractdate","listdate","listeddate")
date_stat_vars   <- c("contract_status_change_date","contractstatuschangedate","statuschangedate")
date_close_vars  <- c("close_date","closedate","saledate","closingdate")

beds_vars        <- c("bedrooms_total","bedroomstotal","beds","bedrooms")
baths_vars       <- c("bathrooms_total_integer","bathroomstotalinteger","bathstotal","bathrooms")

pool_vars        <- c("pool_private_yn","poolprivateyn","poolyn")

# Build SELECT
price_expr <- coalesce_trycast(c(price_close_vars, price_list_vars, price_orig_vars), cast = "DOUBLE")
area_expr  <- coalesce_trycast(area_vars, cast = "DOUBLE")

# event_date: coalesce a few date candidates; CAST to DATE at the end
date_coalesce <- function(vars) {
  v <- vars[vars %in% cols]
  if (!length(v)) return(character())
  # Direct TRY_CAST to DATE first; also try a couple string formats
  sapply(v, function(cn) {
    ci <- as.character(quote_ident(cn))
    paste0(
      "TRY_CAST(", ci, " AS DATE),",
      "CAST(TRY_STRPTIME(CAST(", ci, " AS VARCHAR), '%Y-%m-%d') AS DATE),",
      "CAST(TRY_STRPTIME(CAST(", ci, " AS VARCHAR), '%m/%d/%Y') AS DATE)"
    )
  })
}
date_bits <- c(
  date_coalesce(date_list_vars),
  date_coalesce(date_stat_vars),
  date_coalesce(date_close_vars)
)
event_date_expr <- if (length(date_bits)) {
  paste0("COALESCE(", paste(date_bits, collapse = ", "), ")")
} else {
  "NULL"
}

# Concrete identifiers for GROUP BYs that need a column name
state_col <- first_existing(state_vars)
ptype_col <- first_existing(ptype_vars)
city_col  <- first_existing(city_vars)
beds_col  <- first_existing(beds_vars)
baths_col <- first_existing(baths_vars)
pool_col  <- first_existing(pool_vars)

sql_view <- sprintf("
  CREATE OR REPLACE VIEW mls_enhanced AS
  SELECT
    mr.*,
    %s AS price,
    %s AS area_sqft,
    %s AS event_date
  FROM mls_raw mr
", price_expr, area_expr, event_date_expr)
DBI::dbExecute(con, sql_view)

# Sanity check
DBI::dbGetQuery(con, "SHOW TABLES")

# Summary

# 1) Overall counts and price stats
overall <- DBI::dbGetQuery(con, "
  SELECT
    COUNT(*) AS n_rows,
    COUNT(price) AS n_with_price,
    AVG(price) AS avg_price,
    MEDIAN(price) AS median_price,
    MIN(price) AS min_price,
    MAX(price) AS max_price
  FROM mls_enhanced
")
print(overall)

# 2) By property type (if present)
if (!is.na(ptype_col)) {
  q <- sprintf("
    SELECT
      %s AS property_type,
      COUNT(*) AS n,
      MEDIAN(price) AS median_price,
      AVG(price) AS avg_price
    FROM mls_enhanced
    GROUP BY %s
    ORDER BY n DESC
    LIMIT 20
  ", as.character(quote_ident(ptype_col)), as.character(quote_ident(ptype_col)))
  print(DBI::dbGetQuery(con, q))
}

# 3) By state with price/sqft when area available
if (!is.na(state_col)) {
  q <- sprintf("
    SELECT
      %s AS state_or_province,
      COUNT(*) AS n,
      MEDIAN(price) AS median_price,
      AVG(price) AS avg_price,
      AVG(CASE WHEN area_sqft > 0 THEN price/area_sqft END) AS avg_price_per_sqft
    FROM mls_enhanced
    GROUP BY %s
    ORDER BY n DESC
    LIMIT 50
  ", as.character(quote_ident(state_col)), as.character(quote_ident(state_col)))
  print(DBI::dbGetQuery(con, q))
}

# 4) Monthly trend
trend <- DBI::dbGetQuery(con, "
  SELECT
    DATE_TRUNC('month', event_date) AS month,
    COUNT(*) AS n,
    MEDIAN(price) AS median_price
  FROM mls_enhanced
  WHERE event_date IS NOT NULL
  GROUP BY month
  ORDER BY month
")
print(trend)

# 5) Bedrooms / Bathrooms breakdowns
if (!is.na(beds_col)) {
  q <- sprintf("
    SELECT %s AS bedrooms, COUNT(*) AS n, MEDIAN(price) AS median_price
    FROM mls_enhanced
    GROUP BY %s
    ORDER BY bedrooms
  ", as.character(quote_ident(beds_col)), as.character(quote_ident(beds_col)))
  print(DBI::dbGetQuery(con, q))
}
if (!is.na(baths_col)) {
  q <- sprintf("
    SELECT %s AS bathrooms, COUNT(*) AS n, MEDIAN(price) AS median_price
    FROM mls_enhanced
    GROUP BY %s
    ORDER BY bathrooms
  ", as.character(quote_ident(baths_col)), as.character(quote_ident(baths_col)))
  print(DBI::dbGetQuery(con, q))
}

# 6) Pool effect (if a pool flag exists)
if (!is.na(pool_col)) {
  q <- sprintf("
    SELECT %s AS pool_private_yn, COUNT(*) AS n, MEDIAN(price) AS median_price
    FROM mls_enhanced
    GROUP BY %s
    ORDER BY n DESC
  ", as.character(quote_ident(pool_col)), as.character(quote_ident(pool_col)))
  print(DBI::dbGetQuery(con, q))
}
