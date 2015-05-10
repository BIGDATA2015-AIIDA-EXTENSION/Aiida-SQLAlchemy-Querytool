# -*- coding: utf-8 -*-

from aiida.orm import Node

import imp
from uuid import UUID
from itertools import starmap

from .utils import check_args, Attribute
from .query_builder.sqlalch import QueryBuilder as SQLAlchemyQB


# TODO: EVERYTHING.
#   * refine TypeError messages.
#   * handle or_, and_, not_ in typecheck + tuple size maybe (in the case of
#   time tuple) ?
#   * Issue with filter_attr: when two filter_attr call are made, it should
#   filter the Node which have BOTH attributes. But this is different from a
#   join ! It should be transformed into an EXIST (or NOT EXISTS) statement to
#   filter all the node that don't have both of them, and the join should be
#   made after that.
#   * Maybe refactor input/output attributes filter to avoid the repetition. The
#   only difference between the two being how the link in the DB is followed.
# To think of:
#   * a way to precisely check arguments and to not repeat the check between
#   methods (DRY, ..). It should also check unexpected args, kwargs, type,
#   or/and/not combinaison, etc. . But it does not need to be too generic, only
#   for attr filter accross filter_attr/input/output/parents/children.
#   -> exemple for filter_id, that should support not_ statement.

class QueryTool(object):

    def __new__(cls, *args, **kwargs):
        # TODO: If possible, the query builder list should not be tie to the
        # Query Tool, but external and configurable ?

        inst = super(QueryTool, cls).__new__(cls, *args, **kwargs)

        # TODO: Remplace the None by the correct Query Builder.
        if imp.find_module('sqlalchemy') and imp.find_module('aldjemy'):
            setattr(cls, "query_builder_class", SQLAlchemyQB)
        else:
            raise NotImplementedError("This Query Tool does not implement an "
                                      + "other version than the one with SQL "
                                      + "Alchemy.")
            inst.query_builder = None

        return inst

    def __init__(self, *args, **kwargs):
        self.query_builder = QueryTool.query_builder_class()
        if len(args) > 0:
            self.filter_class(*args)

    def run_query(self):
        return self.query_builder.run_query()

    def filter_class(self, *args):
        check_args(args, subclass=Node, exception=True)
        class_name = map(lambda a: a._query_type_string, args)
        self.query_builder.filter_class(class_name)

    def filter_group(self, *args):
        check_args(args, instance=basestring, exception=True)
        self.query_builder.filter_group(args)

    def filter_id(self, *args):
        check_args(args, instance=int, exception=True)
        self.query_builder.filter_id(args)

    def filter_uuid(self, *args):
        check_args(args, instance=[basestring, UUID])
        self.query_builder.filter_uuid(args)

    def filter_label(self, *args):
        check_args(args, instance=basestring, exception=True)
        self.query_builder.filter_label(args)

    def filter_description(self, *args):
        check_args(args, instance=basestring, exception=True)
        self.query_builder.filter_description(args)

    def filter_time(self, *args):
        check_args(args, instance=tuple, exception=True)

    def filter_attr(self, *args, **kwargs):
        extra = kwargs.pop('extra', False)
        prefetch = kwargs.pop('prefetch', False)

        if len(args) < 1:
            raise ValueError("This methods does not support empty parameters.")

        if isinstance(args[0], tuple):
            # If the first one is a tuple, we assume the rest also is.
            # This also means it should support construct of the form
            # filter_attr("attr", "op", "value", "attr", "op", "value"), without
            # specifying the tuple.
            args = list(starmap(Attribute, args))
        else:
            args = [Attribute(*args)]

        self.query_builder.filter_attr(
            args, extra=extra, prefetch=prefetch)

    def filter_input_attr(self, *args, **kwargs):
        extra = kwargs.pop('extra', False)
        prefetch = kwargs.pop('prefetch', False)
        link = kwargs.pop('link', False)

        if len(args) < 1:
            raise ValueError("This methods does not support empty parameters.")

        filters = self._extract_attr(args)

        self.query_builder.filter_input_attr(
            filters, extra=extra, prefetch=prefetch, link=link)

    def filter_output_attr(self, *args, **kwargs):
        extra = kwargs.pop('extra', False)
        prefetch = kwargs.pop('prefetch', False)
        link = kwargs.pop('link', None)

        if len(args) < 1:
            raise ValueError("This methods does not support empty parameters.")

        filters = self._extract_attr(args)

        self.query_builder.filter_output_attr(
            filters, extra=extra, prefetch=prefetch, link=link)

    def filter_parents_attr(self, *args, **kwargs):
        extra = kwargs.pop('extra', False)
        min_depth = kwargs.pop('min_depth', None)
        max_depth = kwargs.pop('max_depth', None)

        filters = self._extract_attr(args)

        self.query_builder.filter_parents_attr(filters, extra=extra,
                                               min_depth=min_depth,
                                               max_depth=max_depth)

    def filter_children_attr(self, *args, **kwargs):
        extra = kwargs.pop('extra', False)
        min_depth = kwargs.pop('min_depth', None)
        max_depth = kwargs.pop('max_depth', None)

        filters = self._extract_attr(args)

        self.query_builder.filter_children_attr(filters, extra=extra,
                                               min_depth=min_depth,
                                               max_depth=max_depth)

    def prefetch_attr(self, *args, **kwargs):
        check_args(args, instance=basestring, exception=True)
        extra = kwargs.pop('extra', False)

        raise NotImplementedError("Not implemeted yet.")

    def filter_relation(self, relation, in_, rename=None, prefetch=False):
        # Only two relations supported yet.
        valid_relation = ("output", "input", "parents", "children")
        if relation not in valid_relation:
            raise ValueError("The relation must be in {}.".
                             format(" ".join(valid_relation)))
        self.query_builder.filter_relation(relation, in_.query_builder, rename,
                                           prefetch)

    def _get_query(self):
        return self.query_builder.get_query()

    def _extract_attr(self, args):
        attr_filters = None
        if isinstance(args[0], tuple):
            attr_filters = list(starmap(Attribute, args))
        else:
            attr_filters = [Attribute(*args)]
        return attr_filters



