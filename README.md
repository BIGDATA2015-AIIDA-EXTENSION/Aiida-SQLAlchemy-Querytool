AiiDA
=====

This is a repo containing part of the work done during the AiiDA project of the
Big Data course. Specificaly, the focus here was on improving the Query Tool.

A description of the work for the whole project can be found
[here](http://wiki.epfl.ch/bigdata2015-aiida-extension/).

The version of the repository is based on a version of AiiDA from April 2015.
It includes a new abstraction of the Query Tool to be able to switch the
implementation of the query builder. It also implements prefetching to original
Query Tool. More importantly, a rewrite of the query tool has been done using
SQL Alchemy + Aldjemy to allow more optimisation and precision when building
queries. It implements class, id, uuid, label, description, attribute filter
for nodes and the relation (input/output), with prefetching. In addition, it
also adds the possibility to filter on children and parents, using the
transitive closure table (DbPath), as well as chaining queries together,
according to the relationship.

A (incomplete) description of the query tool can be found
[here](https://gist.github.com/Kazy/43cad4e2ae5e777e4404).

TODO
----

* Continue implementing functionality from the defined API.
* Fix the various TODOs in the code: handling the extra table, refactoring a
    bit the way the query is built in the SQL Alchemy query builder, fix the
    performance regression from commit 5ddf378.
* Correctly return the result of the query tool. In particular, cast the node
    to its correct class, and return the prefetched attributes in a
    dictionnary.
* Add attribute prefetching outside of fitlering. This should not filter nodes
    without the corresponding attribute.
