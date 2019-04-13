import pytest

import dbtlint.exceptions
import dbtlint.lint


def test_valid_sql():
    dbtlint.lint.lint_text("SELECT 1")


def test_invalid_sql():
    with pytest.raises(dbtlint.exceptions.SqlLintError):
        dbtlint.lint.lint_text("Not a real SQL statement")


def test_valid_dbt_ref():
    dbtlint.lint.lint_text("SELECT * FROM {{ ref('my_ref') }}")


def test_valid_dbt_config():
    dbtlint.lint.lint_text('{{ config(materialized="ephemeral") }} SELECT * FROM my_table')


def test_undefined_macro():
    with pytest.raises(dbtlint.exceptions.JinjaTemplateError):
        dbtlint.lint.lint_text("SELECT * FROM {{ my_undefined_macro('my_ref') }}")


def test_valid_custom_macros():
    dbtlint.lint.lint_text(
        text="{{ my_no_return_macro('my_arg') }} SELECT * FROM {{ my_return_macro('my_arg') }}",
        macros=[
            dbtlint.lint.Macro('my_return_macro(arg1)', 'some_value'),
            dbtlint.lint.Macro('my_no_return_macro(arg1)', ''),
        ],
    )
