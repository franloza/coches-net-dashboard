{{
  config(
    materialized = "table"
  )
}}

with generate_date as (
        select cast(range as date) as date_key
          from range(current_date - interval 1 year, current_date + interval 1 day, interval 1 day)
          )
   select date_key as date_key,
          dayofyear(date_key) as day_of_year,
          yearweek(date_key) as week_key,
          weekofyear(date_key) as week_of_year,
          dayofweek(date_key) as day_of_week,
          isodow(date_key) as iso_day_of_week,
          dayname(date_key) as day_name,
          date_trunc('week', date_key) as first_day_of_week,
          date_trunc('week', date_key) + 6 as last_day_of_week,
          year(date_key) || right('0' || month(date_key), 2) as month_key,
          month(date_key) as month_of_year,
          dayofmonth(date_key) as day_of_month,
          left(monthname(date_key), 3) as month_name_short,
          monthname(date_key) as month_name,
          date_trunc('month', date_key) as first_day_of_month,
          last_day(date_key) as last_day_of_month,
          cast(year(date_key) || quarter(date_key) as int) as quarter_key,
          quarter(date_key) as quarter_of_year,
          cast(date_key - date_trunc('quarter', date_key) + 1 as int) as day_of_quarter,
          ('q' || quarter(date_key)) as quarter_desc_short,
          ('quarter ' || quarter(date_key)) as quarter_desc,
          date_trunc('quarter', date_key) as first_day_of_quarter,
          last_day(date_trunc('quarter', date_key) + interval 2 month) as last_day_of_quarter,
          cast(year(date_key) as int) as year_key,
          date_trunc('year', date_key) as first_day_of_year,
          date_trunc('year', date_key) - 1 + interval 1 year as last_day_of_year,
          row_number() over (partition by year(date_key), month(date_key), dayofweek(date_key) order by date_key) as ordinal_weekday_of_month
     from generate_date
