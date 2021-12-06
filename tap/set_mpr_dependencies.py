from tap import cfg
from tap.build_dependency_tree import build_dependency_tree
from tap.parse_srcinfo import parse_srcinfo


def set_mpr_dependencies():
    depends_list = []
    conflicts_list = []
    breaks_list = []

    for i in cfg.mpr_packages:
        pkginfo = parse_srcinfo(
            f"/var/tmp/{cfg.application_name}/source_packages/{i}/.SRCINFO"
        )
        if pkginfo.depends is not None:
            depends_list += pkginfo.depends
        if pkginfo.makedepends is not None:
            depends_list += pkginfo.makedepends
        if pkginfo.checkdepends is not None:
            depends_list += pkginfo.checkdepends
        if pkginfo.conflicts is not None:
            conflicts_list += pkginfo.conflicts
        if pkginfo.breaks is not None:
            breaks_list += pkginfo.breaks

    build_dependency_tree(
        depends=depends_list, conflicts=conflicts_list, breaks=breaks_list
    )
