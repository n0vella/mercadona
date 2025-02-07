Simple spanish inflation historical data taking Mercadona as reference.

This repo has two funcionalities:
  - Once a week, a Github action will collect pricing data from Mercadona, and update [data.json](data.json) acordingly.
  - Also, a barebones flask server it's provided to be used as an API for this data, Vercel configuration is provided, so it can be deploy for free.
    - An example is in https://mercadona-prices.vercel.app/
    - Data could be requested using id ( https://mercadona-prices.vercel.app/product/4240 ) or product name ( https://mercadona-prices.vercel.app/query/Naranjas )

This repo has data since October 23.
A simple application for this data is drafted in https://github.com/n0vella/merca-track
