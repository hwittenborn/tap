def build_dependency_tree(**args):
    from tap.get_srcinfo_data import get_srcinfo_data

    packages = args["packages"]
    os_codename = args["os_codename"]
    os_architecture = args["os_architecture"]

    package_data = {}

    for i in packages:
        pkginfo = get_srcinfo_data(path=f"/var/tmp/tap/{i}/.SRCINFO", os_codename=os_codename, os_architecture=os_architecture)
        package_data[i] = pkginfo
