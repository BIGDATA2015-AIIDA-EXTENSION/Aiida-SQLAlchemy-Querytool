# -*- coding: utf-8 -*-
#/usr/bin/env pythyn


import sys


# This script has to be launched as a package.
# python -m benchmarks.query {version} {number}

from aiida import load_dbenv
load_dbenv()
import time
from aiida.orm.querytool2 import QueryTool
from aiida.orm.querytool import QueryTool as QueryTool_old

from aiida.orm.node import Node

def query_old_1():
    qt = QueryTool_old()
    qt.set_class(Node)
    qt.add_attr_filter("ELECTRONS.mixing_beta", ">", 0.)
    qt.add_attr_filter("CONTROL.max_seconds", ">", 0)
    return qt.run_query

def query_old_2():
    qt = QueryTool_old()
    qt.set_class(Node)
    qt.add_attr_filter("ELECTRONS.mixing_beta", ">", 0.)
    qt.add_attr_filter("CONTROL.max_seconds", ">", 0)
    qt.with_attr("ELECTRONS.mixing_beta")
    qt.with_attr("CONTROL.max_seconds")
    return qt.run_prefetch_query

def query_old_3():
    qt = QueryTool_old()
    qt.set_class(Node)
    qt.add_attr_filter("energy", "<=", 0., relnode="res")
    return qt.run_query

def query_old_4():
    qt = QueryTool_old()
    qt.set_class(Node)
    qt.add_attr_filter("energy", "<=", 0., relnode="res")
    qt.with_attr("res.energy")
    return qt.run_prefetch_query

def query_new_1():
    qt = QueryTool(Node)
    qt.filter_attr("ELECTRONS.mixing_beta", ">", 0.)
    qt.filter_attr("CONTROL.max_seconds", ">", 0)
    return qt.run_query

def query_new_2():
    qt = QueryTool(Node)
    qt.filter_attr("ELECTRONS.mixing_beta", ">", 0., prefetch=True)
    qt.filter_attr("CONTROL.max_seconds", ">", 0, prefetch=True)
    return qt.run_query

def query_new_3():
    qt = QueryTool(Node)
    qt.filter_output_attr("energy", "<=", 0.)
    return qt.run_query

def query_new_4():
    qt = QueryTool(Node)
    qt.filter_output_attr("energy", "<=", 0., prefetch=True)
    return qt.run_query

def timeit(f):
    start = time.time()
    res = [_ for _ in f()]
    end = time.time()
    return end - start

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise ValueError("Not enough or too much argument. Sorry :/")

    version = sys.argv[1]
    number = sys.argv[2]

    f = globals()["query_{}_{}".format(version, number)]()
    timed = timeit(f)

    print("{}".format(timed))

