from operator import eq, ge, gt, le, lt

from apt_pkg import (
    CURSTATE_CONFIG_FILES,
    CURSTATE_INSTALLED,
    CURSTATE_NOT_INSTALLED,
    version_compare,
)


def find_apt_package_version(package_object, operator, specified_version):
    version_state = "UNFINDABLE_VERSION"
    versions = []

    # Get package installation state.
    inst_state = package_object.inst_state
    installed_version = None

    if inst_state == CURSTATE_INSTALLED:
        package_installed = True
        installed_version = package_object.current_ver.ver_str

    elif inst_state in [CURSTATE_NOT_INSTALLED, CURSTATE_CONFIG_FILES]:
        package_installed = False

    # Just send back installed state if a version operator wasn't supplied.
    if None in [operator, specified_version]:
        if package_installed:
            return "INSTALLED"
        else:
            return "INSTALLABLE"

    # Get package versions.
    for i in package_object.version_list:
        versions += [i.ver_str]

    # Parse version operator.
    if operator == ">=":
        compare_function = ge
    elif operator == "<=":
        compare_function = le
    elif operator == ">":
        compare_function = gt
    elif operator == "<":
        compare_function = lt
    elif operator == "=":
        compare_function = eq

    # Check if specified version is available.
    for db_version in versions:
        version_result = version_compare(db_version, specified_version)

        if compare_function(version_result, 0) is True:
            version_state = "INSTALLABLE"
            break

    # If so, check if specified version is already installed.
    if version_state == "INSTALLABLE" and package_installed is True:
        version_result = version_compare(installed_version, specified_version)

        if compare_function(version_result, 0) is True:
            version_state = "INSTALLED"

    return version_state
