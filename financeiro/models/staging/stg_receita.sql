-- Staging layer: clean and standardize raw revenue data
-- Source: seed data (receita_bruta.csv)

with source as (

    select * from {{ ref('receita_bruta') }}

),

renamed as (

    select
        ticker                          as ticker,
        empresa                         as company_name,
        ano                             as year,
        trimestre                       as quarter,
        receita_milhoes                 as revenue_millions

    from source

)

select * from renamed
