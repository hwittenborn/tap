from operator import eq, ge, gt, le, lt

from apt_pkg import version_compare


def check_version(ver1, comparison_operator, ver2):
    operator_mappings = {"<": lt, "<=": le, "=": eq, ">": gt, ">=": ge}

    if comparison_operator not in operator_mappings:
        raise TypeError(f"Invalid operator '{comparison_operator}'.")

    version_result = version_compare(ver1, ver2)

    return operator_mappings[comparison_operator](version_result, 0)
