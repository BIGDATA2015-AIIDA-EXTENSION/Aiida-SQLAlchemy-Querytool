# -*- coding: utf-8 -*-
import sys, os
from aiida.orm import Code, DataFactory, Group, Calculation
from aiida.djsite.db.models import DbAttribute, DbNode, DbExtra
from django.db.models.query import Prefetch

from itertools import chain
from collections import defaultdict


__copyright__ = u"Copyright (c), 2015, ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE (Theory and Simulation of Materials (THEOS) and National Centre for Computational Design and Discovery of Novel Materials (NCCR MARVEL)), Switzerland and ROBERT BOSCH LLC, USA. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file"
__version__ = "0.4.0"
__contributors__ = "Andrea Cepellotti, Giovanni Pizzi"

class QueryTool(object):
    """
    Class to make easy queries without extensive knowledge of SQL, Django and/or
    the internal storage mechanism of AiiDA.

    .. note:: This feature is under constant development, so the name of the
      methods may change in future versions to allow for increased querying
      capabilities.

    .. todo:: missing features:

      * add __in filter
      * allow __in filter to accept other querytool objects to perform a single
        query
      * implement searches through the TC table
      * document the methods
      * allow to get attributes of queried data via a single query with suitable
        methods
      * add checks to verify whether filters as <=, ==, etc are valid for the
        specified data type (e.g., __gt only with numbers and dates, ...)
      * probably many other things...
    """
    def __init__(self):
        self._class_string = None
        self._group_queries = []
        self._attr_queries = []
        self._attrs = {}
        self._extra_queries = []
        self._extras = {}
        self._pks_in = None

        self._prefetch_attr = []
        self._prefetch_extras = []

        self._queryobject = None

    def set_class(self, the_class):
        """
        Pass a class to filter results only of a specific Node (sub)class, and
        its subclasses.
        """
        from aiida.orm import Node
        # We are changing the query, clear the cache
        if not issubclass(the_class, Node):
            raise TypeError("You can only call this method on subclasses of Node, you are passing instead".format(the_class.__name__))
        self._queryobject = None
        self._class_string = the_class._query_type_string

    def set_group(self, group, exclude=False):
        """
        Filter calculations only within a given node.
        This can be called multiple times for an AND query.

        .. todo:: Add the possibility of specifying the group as an object
          rather than with its name, so that one can also query special groups,
          etc.

        .. todo:: Add the possibility of specifying "OR" type queries on
          multiple groups, and any combination of AND, OR, NOT.

        :param group: the name of the group
        :param exclude: if True, excude results
        """
        from django.db.models import Q

#        # We are changing the query, clear the cache
#        self._queryobject = None

        if isinstance(group, basestring):
            # BE CAREFUL! WE ALL TAKING ALL GROUPS,
            # IRREGARDLESS OF THE TYPE AND THE OWNER
            if exclude:
                self._group_queries.append(~Q(dbgroups__name=group))
            else:
                self._group_queries.append(Q(dbgroups__name=group))
        else:
            raise NotImplementedError("Still to implement passing a real group rather than its name")

    def limit_pks(self, pk_list):
        """
        Limit the query to a given list of pks.

        :param pk_list: the list of pks you want to limit your query to.
        """
        from django.db.models import Q
        self._pks_in = [int(_) for _ in pk_list]

    def _get_query_object(self, prefetch=False):
        """
        Internal method that returns the Django query object that
        has been generated.
        """
        from aiida.djsite.db import models

        if self._class_string is None:
            raise ValueError("You have to call set_class first.")

        if self._queryobject is None:
            res = models.DbNode.objects.filter(
                type__startswith=self._class_string)

            for group_qobj in self._group_queries:
                res = res.filter(group_qobj)

            if self._pks_in is not None:
                res = res.filter(pk__in=self._pks_in)

            for attr_qobj, reldata in self._attr_queries:
                if reldata:
                    if reldata['relation'] == '__input':
                        relationlink = "input_links"
                    elif reldata['relation'] == '__output':
                        relationlink = "output_links"
                    else:
                        raise ValueError("relation {} not implemented!".format(
                            reldata['relation']))
                    classinfo = {}
                    if reldata['nodeclass'] is not None:
                        classinfo['type__startswith'] = reldata['nodeclass']
                    linkedres = models.DbNode.objects.filter(
                        dbattributes__in=attr_qobj, **classinfo)
                    res = res.filter(**{
                        "{}{}__in".format(relationlink, reldata['relation']):
                            linkedres
                        # , "{}__label".format(relationlink): reldata['linkname']
                    })

                    # if prefetch:
                    #     res = self._prefetch(res, reldata["attrname"], reldata["relname"])

                else:
                    res = res.filter(dbattributes__in=attr_qobj)

            if prefetch:
                # res = self._prefetch_all(res)
                for attr in self._prefetch_attr:
                    rel = None
                    if '.' in attr:
                        rel, attr = attr.split(".")
                    res = self._prefetch(res, attr, rel)

            for extra_qobj, reldata in self._extra_queries:
                if reldata:
                    if reldata['relation'] == '__input':
                        relationlink = "input_links"
                    elif reldata['relation'] == '__output':
                        relationlink = "output_links"
                    else:
                        raise ValueError("relation {} not implemented!".format(
                            reldata['relation']))
                    linkedres = models.DbNode.objects.filter(
                        dbextras__in=extra_qobj)
                    res = res.filter(**{
                        "{}{}__in".format(relationlink, reldata['relation']):
                            linkedres
                        # , "{}__label".format(relationlink): reldata['linkname']
                    })

                    if prefetch:
                        res = self._prefetch(res, reldata["attrname"],
                                             relationlink, extra=True)

                else:
                    res = res.filter(dbextras__in=extra_qobj)


            if prefetch:
                for extra in self._prefetch_extras:
                    rel = None
                    if '.' in extra:
                        rel, extra = extra.split(".")
                    res = self._prefetch(res, attr, rel, extra= True)

            self._queryobject = res.distinct()

        return self._queryobject

    def get_attributes(self):
        """
        Get the raw values of all the attributes of the queried nodes.
        """
        from aiida.djsite.db import models
        res = self._get_query_object()
        attrs = models.DbAttribute.objects.filter(
            dbnode__in=res).filter(key__in=self._attrs.keys()).values(
            'dbnode__pk', 'key', 'tval', 'dval',
            'ival', 'bval', 'fval', 'datatype')
        return attrs

    def _get_extras_raw(self):
        """
        Internal method to get the raw values of all the extras
        of the queried nodes.
        """
        from aiida.djsite.db import models
        res = self._get_query_object()
        extras = models.DbExtra.objects.filter(
            dbnode__in=res).filter(key__in=self._extras.keys()).values(
            'dbnode__pk', 'key', 'tval', 'dval',
            'ival', 'bval', 'fval', 'datatype')
        return extras

    def _get_attrs_raw(self):
        """
        Internal method to get the raw values of all the attributes
        of the queried nodes.
        """
        from aiida.djsite.db import models
        res = self._get_query_object()
        attrs = models.DbAttribute.objects.filter(
            dbnode__in=res).filter(key__in=self._attrs.keys()).values(
            'dbnode__pk', 'key', 'tval', 'dval',
            'ival', 'bval', 'fval', 'datatype')
        return attrs

    def run_query(self, with_data=False):
        """
        Run the query using the filters that have been pre-set on this
        class, and return a generator of the obtained Node (sub)classes.
        """
        if with_data:
            attrs = self.create_attrs_dict()
            extras = self.create_extras_dict()

        for r in self._get_query_object():
            # if with_data:
            #     yield r.get_aiida_class(), {'attrs': attrs.get(r.pk, {}),
            #                                 'extras': extras.get(r.pk, {})}
            # else:
            #     yield r.get_aiida_class()
            yield r

    def run_prefetch_query(self):
        """
        Run the query and prefetch the attributes. This means it returns
        everything at once, and not an iterator like `run_query`.
        For now it only handles the attrs you've applied a filter to (like:
            q.add_attr_filter("energy", "<=", 0., relnode="res"))
        """
        qs = self._get_query_object(prefetch=True)
        return map(self._extract_attributes, qs.all())

    def with_attr(self, *attrs):
        self._prefetch_attr = self._prefetch_attr + list(attrs)

    def with_extra(self, *attrs):
        self._prefetch_extras = self._prefetch_extras + list(attrs)

    def _prefetch(self, query, attr, relation=None, extra=False):
        """
        Add to the query `query` prefetching for attribut `attr`. It supports
        relation using `relation` arg (should be the same as the one passed to
        relnode's add_attr_filter argument).
        """
        _db = DbExtra if extra else DbAttribute
        _to_attr = "_extra_{}" if extra else "_attr_{}"
        _filter = "dbextras" if extra else "dbattributes"

        attr_queryset = _db.objects.filter(key=attr)

        if relation:
            _rel_attr = "outputs" if relation == "res" or \
                relation.startswith('out') else "inputs"
            _to_attr = _to_attr.format(relation) + "_{}".format(attr)

            qs = DbNode.objects.filter(**{_filter + "__key": attr})\
                .prefetch_related(Prefetch(_filter,
                                           queryset=attr_queryset,
                                           to_attr=_to_attr))

            query = query.prefetch_related(
                Prefetch(_rel_attr, queryset=qs,
                         to_attr="_" + _rel_attr + "_{}_{}".format(relation, attr)))

        else:
            _to_attr = _to_attr.format(attr)
            query = query.prefetch_related(Prefetch(_filter,
                                                    queryset=attr_queryset,
                                                    to_attr=_to_attr))

        return query


    def _prefetch_all(self, query):
        output_attr = []
        input_attr = []
        attrs = []

        for attr in self._prefetch_attr:
            if "." in attr:
                rel, attr = attr.split(".")
                if rel == "res" or rel.startswith('ou'):
                    output_attr.append(attr)
                else:
                    input_attr.append(attr)
            else:
                attrs.append(attr)

        attr_queryset = DbAttribute.objects.filter(key__in=output_attr)

        qs = DbNode.objects.filter(dbattributes__key__in=output_attr)\
            .prefetch_related(Prefetch("dbattributes",
                              queryset=attr_queryset,
                              to_attr="_prefetch_attrs"))

        query = query.prefetch_related(Prefetch("outputs",
                                                queryset=qs,
                                                to_attr="_prefetch_outputs"))

        return query

    def _extract_attributes(self, node):
        """
        Extract the prefetched attributs for a given node, and return a tuple
        with the node and a dictionnary of dictionnary of the attributs.
        This relies on the current state of the query.

        TODO: * the conversion_attr dictionnary shouldn't be there. A function to
            get the correct typed value of a DbAttribute object should be
            available.
              * change attr_dict to be accessible via attribute (attr_dict.attr)
              * support for list/dict attributes (implies changes in
            _get_query_object too)
        """
        attrs = []

        for attr in self._prefetch_attr:
            rel = None
            full_output = None
            full_attr = "_attr_{}".format(attr)

            if '.' in attr:
                rel, attr = attr.split(".")
                _rel_attr = "outputs" if rel == "res" or \
                    rel.startswith('out') else "inputs"
                full_output = "_{}_{}_{}".format(_rel_attr, rel, attr)
                full_attr = "_attr_{}_{}".format(rel, attr)

            attrs.append((attr, rel, full_output, full_attr))

        # Could be made compatible with attributes by subclassing defaultdict
        # and setting self.__dict__ = self.
        attr_dict = defaultdict(dict)

        conversion_attr = {
            'bool': 'bval',
            'int': 'ival',
            'float': 'fval',
            'txt': 'tval',
            'date': 'dval'
        }

        flatten = lambda e: filter(lambda e: e is not None, list(chain.from_iterable(e)))

        # There seems to be no way for Django to assign the result of a
        # prefetch to something else than an attribute, so we have to use
        # hasattr/getattr to access the prefetched result.
        # node._outputs_[]._attr_[]
        for attr, rel, out_str, att_str in attrs:
            _attr = None

            if out_str and hasattr(node, out_str):
                _attr = flatten(
                    map(lambda n: getattr(n, att_str) if hasattr(n, att_str) else None,
                        getattr(node, out_str))
                )
            elif hasattr(node, att_str):
                _attr = getattr(node, att_str)
            else:
                continue

            _attr = filter(lambda e: e is not None,
                           map(lambda a: getattr(a, conversion_attr[a.datatype])
                               if a.datatype in conversion_attr else None,
                               _attr)
                           )

            if rel:
                attr_dict[rel][attr] = _attr
            else:
                attr_dict[attr] = _attr

        return (node, attr_dict)

#This can be useful, but risky
#.prefetch_related('dbextras').prefetch_related('dbattributes'):
#
#            # Do we really want to do this?
#        for r in res.distinct():
#            yield r.get_aiida_class(), {
#                'extras': self._create_extra_dict(r.dbextras.all()),
#                'attrs': self._create_attr_dict(r.dbattributes.all())}
        #return res.distinct()

    def create_extras_dict(self):
        """
        Return a dictionary of the raw data from the
        extras associated to the queried nodes.
        """
        from collections import defaultdict

        # TODO: implement lists and dicts
        field = {'txt': 'tval', 'float': 'fval', 'bool': 'bval',
                 'int': 'ival', 'date': 'dval', 'none': lambda x: None}
        relevant_extras = self._extras.keys()

        extrasdict = defaultdict(dict)

        for e in self._get_extras_raw():
            f = field[e['datatype']]
            if callable(f):
                extrasdict[e['dbnode__pk']][e['key']] = f(e)
            else:
                extrasdict[e['dbnode__pk']][e['key']] = e[f]

        return dict(extrasdict)

    def create_attrs_dict(self):
        """
        Return a dictionary of the raw data from the
        attributes associated to the queried nodes.
        """
        from collections import defaultdict

        # TODO: implement lists and dicts
        field = {'txt': 'tval', 'float': 'fval', 'bool': 'bval',
                 'int': 'ival', 'date': 'dval', 'none': lambda x: None}
        relevant_attrs = self._attrs.keys()

        attrsdict = defaultdict(dict)

        raw_attrs = self._get_attrs_raw()
        for e in raw_attrs:
            f = field[e['datatype']]
            if callable(f):
                attrsdict[e['dbnode__pk']][e['key']] = f(e)
            else:
                attrsdict[e['dbnode__pk']][e['key']] = e[f]

        return dict(attrsdict)

    def add_attr_filter(self, key, filtername, value,
                        negate=False, relnode=None, relnodeclass=None):
        """
        Add a new filter on the value of attributes of the nodes you
        want to query.

        :param key: the value of the key
        :param filtername: the type of filter to apply. Multiple
          filters are supported (depending on the type of value),
          like '<=', '<', '>', '>=', '=', 'contains', 'iexact',
          'startswith', 'endswith', 'istartswith', 'iendswith', ...
          (the prefix 'i' means "case-insensitive", in the
          case of strings).
        :param value: the value of the attribute
        :param negate: if True, add the negation of the current filter
        :param relnode: if specified, asks to apply the filter not on
          the node that is currently being queried, but rather
          on a node linked to it.
          Can be "res" for output results, "inp.LINKNAME" for input nodes
          with a given link name, "out.LINKNAME" for output nodes
          with a given link name.
        :param relnodeclass: if relnode is specified, you can here add
          a further filter on the type of linked node for which you are
          executing the query (e.g., if you want to filter for outputs
          whose 'energy' value is lower than zero, but only if 'energy'
          is in a ParameterData node).
        """
        from aiida.djsite.db import models

        return self._add_filter(key, filtername, value,
                                dbtable=models.DbAttribute,
                                negate=negate,
                                querieslist=self._attr_queries,
                                attrdict=self._attrs,
                                relnode=relnode,relnodeclass=relnodeclass)

    def add_extra_filter(self, key, filtername, value, negate=False, relnode=None, relnodeclass=None):
        """
        Add a new filter on the value of extras of the nodes you
        want to query.

        :param key: the value of the key
        :param filtername: the type of filter to apply. Multiple
          filters are supported (depending on the type of value),
          like '<=', '<', '>', '>=', '=', 'contains', 'iexact',
          'startswith', 'endswith', 'istartswith', 'iendswith', ...
          (the prefix 'i' means "case-insensitive", in the
          case of strings).
        :param value: the value of the extra
        :param negate: if True, add the negation of the current filter
        :param relnode: if specified, asks to apply the filter not on
          the node that is currently being queried, but rather
          on a node linked to it.
          Can be "res" for output results, "inp.LINKNAME" for input nodes
          with a given link name, "out.LINKNAME" for output nodes
          with a given link name.
        :param relnodeclass: if relnode is specified, you can here add
          a further filter on the type of linked node for which you are
          executing the query (e.g., if you want to filter for outputs
          whose 'energy' value is lower than zero, but only if 'energy'
          is in a ParameterData node).
        """
        from aiida.djsite.db import models

        return self._add_filter(key, filtername, value,
                                dbtable=models.DbExtra,
                                negate=negate,
                                querieslist=self._extra_queries,
                                attrdict=self._extras,
                                relnode=relnode,relnodeclass=relnodeclass)

    def _add_filter(self, key, filtername, value, negate,
                    dbtable, querieslist, attrdict, relnode,relnodeclass):
        """
        Internal method to apply a filter either on Extras or Attributes,
        to avoid to repeat the same code in a DRY spirit.
        """
        from django.utils.timezone import is_naive, make_aware, get_current_timezone
        from django.db.models import Q
        from aiida.orm import Node

        valid_filters = {
            '': '',
            None: '',
            '=': '__exact',
            'exact': '__exact',
            'iexact': '__iexact',
            'contains': '__contains',
            'icontains': '__icontains',
            'startswith': '__startswith',
            'istartswith': '__istartswith',
            'endswith': '__endswith',
            'iendsswith': '__iendswith',
            '<': '__lt',
            'lt': '__lt',
            'lte': '__lte',
            'le': '__lte',
            '<=': '__lte',
            '>': '__gt',
            'gt': '__gt',
            'gte': '__gte',
            'ge': '__gte',
            '>=': '__gte',
            }

        querylist = []
        querydict = {}
        querydict['key'] = key

        try:
            internalfilter = valid_filters[filtername]
        except KeyError:
            raise ValueError("Filter '{}' is not a supported filter".format(
                    filtername))

        if value is None:
            querydict['datatype'] = 'none'
        elif isinstance(value,bool):
            querydict['datatype'] = 'bool'
            if negate:
                querylist.append(~Q(**{
                            'bval{}'.format(internalfilter): value}))
            else:
                querydict['bval{}'.format(internalfilter)] = value
        elif isinstance(value,(int,long)):
            querydict['datatype'] = 'int'
            querydict['ival{}'.format(internalfilter)] = value
        elif isinstance(value,float):
            querydict['datatype'] = 'float'
            querydict['fval{}'.format(internalfilter)] = value
        elif isinstance(value,basestring):
            querydict['datatype'] = 'txt'
            if negate:
                querylist.append(~Q(**{
                            'tval{}'.format(internalfilter): value}))
            else:
                querydict['tval{}'.format(internalfilter)] = value
        elif isinstance(value, datetime.datetime):
            # current timezone is taken from the settings file of django
            if is_naive(value):
                value_aware = make_aware(value,get_current_timezone())
            else:
                value_aware = value
            querydict['datatype'] = 'date'
            querydict['dval{}'.format(internalfilter)] = value_aware
        #elif isinstance(value, list):
        #
        #    new_entry.datatype = 'list'
        #    new_entry.ival = length
        #elif isinstance(value, dict):
        #    new_entry.datatype = 'dict'
        #    new_entry.ival = len(value)
        else:
            raise TypeError("Only basic datatypes are supported in queries!")

        reldata = {}
        if relnode is not None:
            if (relnodeclass is not None and
                not isinstance(relnodeclass, Node) and
                not issubclass(relnodeclass, Node)):
                raise TypeError("relnodeclass must be an AiiDA node")
            if relnodeclass is None:
                reldata['nodeclass'] = None
            else:
                reldata['nodeclass'] = relnodeclass._query_type_string
            if relnode == 'res':
                reldata['relation'] = "__output"
                # reldata['linkname'] = "output_parameters"
            elif relnode.startswith('out.'):
                reldata['relation'] = "__output"
                # reldata['linkname'] = relnode[4:]
            elif relnode.startswith('inp.'):
                reldata['relation'] = "__input"
                # reldata['linkname'] = relnode[4:]
            else:
                raise NotImplementedError("Implemented only for 'out.' and 'inp.' for the time being!")
            reldata['attrname'] = key
            reldata['relname'] = relnode
        else:
            if relnodeclass is not None:
                raise ValueError("cannot pass relnodeclass if no relnode is specified")
        # We are changing the query, clear the cache
        self._queryobject = None
        querieslist.append((dbtable.objects.filter(
                *querylist, **querydict), reldata))

        if reldata:
            pass
        else:
            attrdict[key] =  reldata

