def builddir_del_error(i, path, j):
    from tap.message import message
    message("error", f"Path '{path}' was unable to be deleted.")
    exit(1)
