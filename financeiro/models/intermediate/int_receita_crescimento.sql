-- Intermediate layer: calculate quarter-over-quarter revenue growth
-- Uses staging model as source

with base as (

    select * from {{ ref('stg_receita') }}

),

with_growth as (

    select
        ticker,
        company_name,
        year,
        quarter,
        revenue_millions,

        -- Previous quarter revenue (QoQ)
        lag(revenue_millions) over (
            partition by ticker
            order by year, quarter
        ) as prev_quarter_revenue,

        -- Year-to-date cumulative revenue
        round(sum(revenue_millions) over (
            partition by ticker, year
            order by quarter
            rows between unbounded preceding and current row
        ), 1) as revenue_ytd

    from base

)

select
    ticker,
    company_name,
    year,
    quarter,
    revenue_millions,
    prev_quarter_revenue,
    revenue_ytd,

    -- QoQ growth percentage
    case
        when prev_quarter_revenue is not null
        then round(
            (revenue_millions - prev_quarter_revenue) / prev_quarter_revenue * 100, 1
        )
        else null
    end as qoq_growth_pct

from with_growth
