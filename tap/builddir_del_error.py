from tap.exceptions import newline_error_exception


def builddir_del_error(i, path, j):
    from tap.message import message

    msg = message.error(f"Path '{path}' was unable to be deleted.", value_return=True)
    raise newline_error_exception(msg)
    exit(1)
