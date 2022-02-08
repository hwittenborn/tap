import sys
import time
from concurrent.futures import ThreadPoolExecutor

import tap


def run_loading_function(message, function, *args, **kwargs):
    with ThreadPoolExecutor() as executor:
        print(message + "  ", end="", flush=True)
        thread = executor.submit(function, *args, **kwargs)

        while thread.running():
            for i in ["⠏", "⠛", "⠹", "⠼", "⠶", "⠧"]:
                print(f"\b{i}", end="", flush=True)
                time.sleep(0.1)

    print("\b ", end="\n")

    try:
        return thread.result()
    except tap.exceptions.newline_error_exception as e:
        msg = e.args[0].strip()
        print(msg)
        sys.exit(1)
