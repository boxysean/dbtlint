import subprocess

import dbtlint.exceptions


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


def lint(file_path):
    return _run_sqlint(file_path)
