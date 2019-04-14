import pytest

import functools

import dbtlint.dialects.postgres
import dbtlint.exceptions
import dbtlint.lint


def test_fake_render():
    assert dbtlint.lint._fake_render_dbt(
        template_text='{{ my_empty_macro() }}',
        macros=[dbtlint.lint.Macro('my_empty_macro()', '')],
    ) == ""


class TestPostgres:
    def setup(self):
        self.lint_text = functools.partial(
            dbtlint.lint.lint_text,
            sql_lint_fn=dbtlint.dialects.postgres.lint,
        )

    def test_valid_sql(self):
        self.lint_text("SELECT 1")

    def test_invalid_sql(self):
        with pytest.raises(dbtlint.exceptions.SqlLintError):
            self.lint_text("Not a real SQL statement")

    def test_valid_dbt_ref(self):
        self.lint_text("SELECT * FROM {{ ref('my_ref') }}")

    def test_valid_dbt_config(self):
        self.lint_text('{{ config(materialized="ephemeral") }} SELECT * FROM my_table')

    def test_undefined_macro(self):
        with pytest.raises(dbtlint.exceptions.JinjaTemplateError):
            self.lint_text("SELECT * FROM {{ my_undefined_macro('my_ref') }}")

    def test_valid_custom_macros(self):
        self.lint_text(
            text="{{ my_no_return_macro('my_arg') }} SELECT * FROM {{ my_return_macro('my_arg') }}",
            macros=[
                dbtlint.lint.Macro('my_return_macro(arg1)', 'some_value'),
                dbtlint.lint.Macro('my_no_return_macro(arg1)', ''),
            ],
        )
