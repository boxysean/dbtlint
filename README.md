dbtlint
=======

Lint your dbt

Currently works for dbt targeting PostgreSQL.

How to install
--------------

Requires python3 and [sqlint](https://github.com/purcell/sqlint/tree/master/lib/sqlint).

1. `git clone` this repo
2. `pip install -r requirements.txt`
3. `gem install sqlint`

Then use `python -m dbtlint cli.py <targets>`. An exit code of 0 means a successful test; 1 means there was an error.

How it works
------------

It uses Jinja to render your dbt files into SQL, then runs [sqlint](https://github.com/purcell/sqlint/tree/master/lib/sqlint) on the output.
