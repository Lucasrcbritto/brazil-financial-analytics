-- Marts layer: final analytical table with financial KPIs
-- Ready for dashboard consumption

with intermediate as (

    select * from {{ ref('int_receita_crescimento') }}

),

annual_revenue as (

    -- Calculate full year revenue for YoY comparison
    select
        ticker,
        year,
        sum(revenue_millions) as annual_revenue_millions
    from intermediate
    group by ticker, year

),

with_yoy as (

    select
        a.ticker,
        a.year,
        a.annual_revenue_millions,
        lag(a.annual_revenue_millions) over (
            partition by a.ticker
            order by a.year
        ) as prev_year_revenue

    from annual_revenue a

)

select
    i.ticker,
    i.company_name,
    i.year,
    i.quarter,
    i.revenue_millions,
    i.prev_quarter_revenue,
    i.qoq_growth_pct,
    i.revenue_ytd,

    -- YoY growth (annual)
    case
        when y.prev_year_revenue is not null
        then round(
            (y.annual_revenue_millions - y.prev_year_revenue) / y.prev_year_revenue * 100, 1
        )
        else null
    end as yoy_growth_pct,

    y.annual_revenue_millions

from intermediate i
left join with_yoy y
    on i.ticker = y.ticker
    and i.year = y.year

order by i.ticker, i.year, i.quarter
