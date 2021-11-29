def version(**args):
    import apt_pkg

    application_name = args["application_name"]
    application_version = args["application_version"]

    apt_version = apt_pkg.VERSION

    print(f"{application_name} {application_version}")
    print(f"APT {apt_version}")
