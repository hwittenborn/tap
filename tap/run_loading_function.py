def run_loading_function(message, function, *args, **kwargs):
    import subprocess
    import time
    import tap

    from tap.exceptions import newline_error_exception
    from concurrent.futures import ThreadPoolExecutor

    exception = None

    try:
        with ThreadPoolExecutor() as executor:
            print(message + "  ", end="", flush=True)
            thread = executor.submit(function, *args, **kwargs)

            while thread.running():
                for i in ["⠏", "⠛", "⠹", "⠼", "⠶", "⠧"]:
                    print(f"\b{i}", end="", flush=True)
                    time.sleep(0.1)

        print("\b ")

        return thread.result()
    
    except tap.exceptions.newline_error_exception as e:
        print(e)
        exit(1)

    except Exception as e:
        raise e
