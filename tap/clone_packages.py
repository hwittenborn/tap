def clone_packages(**args):
    import subprocess
    import time
    import os

    from concurrent.futures import ThreadPoolExecutor

    packages = args["packages"]
    mpr_url = args["mpr_url"]
    
    with ThreadPoolExecutor() as executor:
        package_threads = {}

        for i in packages:
            package_threads[i] = executor.submit(subprocess.run,
                                                 ["git", "clone", "--", f"https://{mpr_url}/{i}"],
                                                 stdout=subprocess.PIPE,
                                                 stderr=subprocess.PIPE)

        running_threads = True

        while running_threads:
            running_threads = False

            for i in packages:
                if package_threads[i].running() is True:
                    running_threads = True

    failed_clones = []

    for i in packages:
        if package_threads[i].result().returncode != 0:
            failed_clones += [i]

    return failed_clones
