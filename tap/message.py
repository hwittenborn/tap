from tap.colors import colors
from sys import stdout, stderr


def _return_message(message, file, **kwargs):
    message = message.rstrip("\n")

    value_return = kwargs.get("value_return", False)
    newline = kwargs.get("newline", True)

    if newline:
        message = message + "\n"

    if value_return:
        return message
    else:
        file.write(message)


class message:
    def info(message, **kwargs):
        return _return_message(
            f"{colors.bold_cyan}>>{colors.bold_white} {message}{colors.white}",
            stdout,
            **kwargs,
        )

    def info2(message, **kwargs):
        return _return_message(
            f"  {colors.bold_blue}->{colors.bold_white} {message}{colors.white}",
            stdout,
            **kwargs,
        )

    def warning(message, **kwargs):
        return _return_message(
            f"{colors.bold_yellow}>>{colors.bold_white} {message}{colors.white}",
            stderr,
            **kwargs,
        )

    def warning2(message, **kwargs):
        return _return_message(
            f"  {colors.bold_yellow}->{colors.bold_white} {message}{colors.white}",
            stderr,
            **kwargs,
        )

    def error(message, **kwargs):
        return _return_message(
            f"{colors.bold_red}>>{colors.bold_white} {message}{colors.white}",
            stderr,
            **kwargs,
        )

    def error2(message, **kwargs):
        return _return_message(
            f"  {colors.bold_red}->{colors.bold_white} {message}{colors.white}",
            stderr,
            **kwargs,
        )

    def question(message, **kwargs):
        return _return_message(
            f"{colors.bold_magenta}>>{colors.bold_white} {message}{colors.white}",
            stdout,
            **kwargs,
        )
