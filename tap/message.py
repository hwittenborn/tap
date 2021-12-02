from tap.colors import colors


def _return_message(message, **kwargs):
    value_return = kwargs.get("value_return", False)
    newline = kwargs.get("newline", True)

    if newline:
        message = message + "\n"  # noqa: E701

    if value_return:
        return message  # noqa: E701
    else:
        print(message, end="")  # noqa: E701


class message:
    def info(message, **kwargs):
        return _return_message(
            f"{colors.bold_cyan}>>{colors.bold_white} {message}{colors.white}", **kwargs
        )

    def info2(message, **kwargs):
        return _return_message(
            f"  {colors.bold_blue}->{colors.bold_white} {message}{colors.white}",
            **kwargs,
        )

    def warning(message, **kwargs):
        return _return_message(
            f"{colors.bold_yellow}>>{colors.bold_white} {message}{colors.white}",
            **kwargs,
        )

    def warning2(message, **kwargs):
        return _return_message(
            f"  {colors.bold_yellow}->{colors.bold_white} {message}{colors.white}",
            **kwargs,
        )

    def error(message, **kwargs):
        return _return_message(
            f"{colors.bold_red}>>{colors.bold_white} {message}{colors.white}", **kwargs
        )

    def error2(message, **kwargs):
        return _return_message(
            f"  {colors.bold_red}->{colors.bold_white} {message}{colors.white}",
            **kwargs,
        )

    def question(message, **kwargs):
        return _return_message(
            f"{colors.bold_magenta}>>{colors.bold_white} {message}{colors.white}",
            **kwargs,
        )
