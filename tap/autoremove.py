from tap import cfg
from tap.run_transaction import run_transaction


def autoremove():
    for i in cfg.apt_cache.packages:
        if cfg.apt_depcache.is_garbage(i):
            cfg.apt_depcache.mark_delete(i)
            cfg.apt_resolver.protect(i)

    cfg.apt_resolver.resolve()

    run_transaction()
