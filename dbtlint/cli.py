import os.path
import logging
import sys

import argparse

import dbtlint.dialects.postgres
import dbtlint.lint
import dbtlint.exceptions


logging.basicConfig(
    level=logging.INFO,
    format='%s',
)


def _parse_target(targets, dbt_suffix):
    file_paths = []

    for target in targets:
        if os.path.isfile(target):
            file_paths.append(target)
        elif os.path.isdir(target):
            return [
                os.path.join(file_path, file_name)
                for file_path, _, file_names in os.walk(target)
                for file_name in file_names
                if file_name.endswith(dbt_suffix)
            ]
        else:
            raise dbtlint.exceptions.RuntimeException(f"Unexpected target: {target}. Specify a valid file or a folder.")

    return sorted(file_paths)


def _parse_macros(macros):
    if macros is None:
        return []

    return [
        dbtlint.lint.Macro(*macro_str.split("=>"))
        for macro_str in macros
    ]


def main():
    parser = argparse.ArgumentParser(
        description="A linter for your dbt files",
    )
    parser.add_argument(
        'targets',
        nargs='+',
        help='File(s) or folder(s) containing dbt files to lint',
    )
    parser.add_argument(
        '--dbt-file-extension',
        default='.sql',
        help='File extension for dbt files to lint',
    )
    parser.add_argument(
        '--sql-dialect',
        choices=['postgres'],
        default='postgres',
        help='SQL dialect, to indicate which linter to use',
    )
    parser.add_argument(
        '--macros',
        action='append',
        default=None,
        help="""Extra macros defined in target dbt files. Multiple flags allowed. Examples:
--macros='my_custom_macro(arg1, arg2)=>placeholder_result'
--macros='my_empty_macro(arg1)=>'
--macros='my_boring_macro()=>some_result'""",
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Shows extra linter debug information'
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Verbose Logging Enabled")

    sql_lint_map = dict(
        postgres=dbtlint.dialects.postgres.lint,
    )

    errors = dbtlint.lint.lint_files(
        file_paths=_parse_target(args.targets, args.dbt_file_extension),
        sql_lint_fn=sql_lint_map[args.sql_dialect],
        macros=_parse_macros(args.macros),
    )

    def pretty_format_error(error, file_path):
        if isinstance(error, dbtlint.exceptions.SqlLintError):
            error_message = str(error).replace(error.temp_file_path, file_path)
        else:
            error_message = str(error)

        return f"{file_path} {error_message}"

    for file_path, error in errors:
        print(pretty_format_error(error, file_path))

    if errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
