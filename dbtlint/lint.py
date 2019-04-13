import jinja2.environment
import jinja2.ext
import jinja2.nodes
import tempfile

import logging
import subprocess
import collections

import dbtlint.exceptions


Macro = collections.namedtuple("Macro", "signature return_value")


DEFAULT_MACROS = [
    Macro('ref(r)', 'some_value'),
    Macro('config(materialized)', ''),
]


def _fake_dbt_jinja_macros(macros):
    return '\n'.join([
        f"{{% macro { macro.signature } -%}}{ macro.return_value }{{%- endmacro %}}"
        for macro in macros
    ])


def _fake_render_dbt(template_text, macros):
    try:
        env = jinja2.environment.Environment()
        template = env.from_string(
            _fake_dbt_jinja_macros(macros) + "\n" + template_text
        )
        return template.render()
    except jinja2.exceptions.TemplateError as e:
        raise dbtlint.exceptions.JinjaTemplateError(str(e))


def _run_sqlint(file_path):
    with subprocess.Popen(
        args=['sqlint', file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    ) as proc:
        line_buffer = [line for line in proc.stdout]
        proc.wait()
        if proc.returncode != 0:
            raise dbtlint.exceptions.SqlLintError(
                message='\n'.join(line_buffer),
                temp_file_path=file_path,
            )


def lint_text(text, macros=None):
    if macros is None:
        macros = []

    macros = macros + DEFAULT_MACROS

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
        _run_sqlint(rendered_file.name)


def lint_files(file_paths, macros=None):
    linting_errors = []

    for file_path in file_paths:
        with open(file_path) as f:
            try:
                logging.debug("FILE: %s", file_path)
                lint_text(
                    text=f.read(),
                    macros=macros,
                )
            except dbtlint.exceptions.RuntimeException as e:
                linting_errors.append((file_path, e))

    return linting_errors
