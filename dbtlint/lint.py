import jinja2.environment
import jinja2.ext
import jinja2.nodes
import tempfile

import logging
import collections

import dbtlint.exceptions


Macro = collections.namedtuple("Macro", "signature return_value")


DEFAULT_MACROS = [
    Macro('ref(r)', 'some_value'),
    Macro('config(materialized)', ''),
]


def _fake_dbt_jinja_macros(macros):
    return ''.join([
        f"{{% macro { macro.signature } -%}}{ macro.return_value }{{%- endmacro %}}"
        for macro in macros
    ])


def _fake_render_dbt(template_text, macros=None):
    if macros is None:
        macros = []

    macros = macros + DEFAULT_MACROS

    try:
        env = jinja2.environment.Environment()
        template = env.from_string(
            _fake_dbt_jinja_macros(macros) + template_text
        )
        return template.render()
    except jinja2.exceptions.TemplateError as e:
        raise dbtlint.exceptions.JinjaTemplateError(str(e))


def lint_text(text, sql_lint_fn, macros=None):
    logging.debug("=====================")
    logging.debug("PRE-RENDERED TEMPLATE")
    logging.debug("=====================")
    logging.debug(text)
    logging.debug("- macros: %s", macros)

    rendered_template = _fake_render_dbt(text, macros)

    logging.debug("=================")
    logging.debug("RENDERED TEMPLATE")
    logging.debug("=================")
    logging.debug(rendered_template)

    with tempfile.NamedTemporaryFile() as rendered_file:
        rendered_file.write(rendered_template.encode('utf-8'))
        rendered_file.flush()
        sql_lint_fn(rendered_file.name)


def lint_files(file_paths, sql_lint_fn, macros=None):
    linting_errors = []

    for file_path in file_paths:
        with open(file_path) as f:
            try:
                logging.debug("FILE: %s", file_path)
                lint_text(
                    text=f.read(),
                    sql_lint_fn=sql_lint_fn,
                    macros=macros,
                )
            except dbtlint.exceptions.RuntimeException as e:
                linting_errors.append((file_path, e))

    return linting_errors
