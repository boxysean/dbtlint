dbtlint
=======

Lint your dbt

Currently works for dbt targeting PostgreSQL.

How to install
--------------

Requires python3.

1. `git clone` this repo
2. `pip install -r requirements.txt`
3. `gem install sqlint`

Then use `python -m dbtlint cli.py <targets>`. An exit code of 0 means a successful test; 1 means there was an error.

How it works
------------

Consider this dbt file:

    {{
      config(
        materialized="ephemeral"
      )
    }}
    
    SELECT
      name,
      breed,
      age
    FROM {{ ref("cats") }}
    
First, it gets rendered with Jinja to

    SELECT
      name,
      breed,
      age
    FROM placeholder

Then the SQL linter checks this file for syntax errors. (Postgres uses [sqlint](https://github.com/purcell/sqlint/tree/master/lib/sqlint).) This should catch

TODO
----

[ ] Add more SQL dialects (Snowflake, Redshift, BigQuery)
[ ] Add common lint hooks (vim, emacs, Sublime, Atom, PyCharm)
[ ] Read from a file configuration rather than entirely from CLI flags
[ ] Package so that it can be run from command-line after a `pip install dbtlint` 
[ ] Add code grammar rules
