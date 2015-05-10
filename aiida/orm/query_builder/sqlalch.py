# -*- coding: utf-8 -*-

__all__ = ['QueryBuilder']


from aiida.djsite.db.models import DbNode, DbAttribute, DbUser, DbExtra, \
    DbGroup, DbPath
from sqlalchemy import and_, or_, select
from sqlalchemy.orm.query import aliased
from functools import partial

# This means you shouldn't import this module if Sql alchemy + aldjemy aren't
# install, nor should you import * it.
Node = DbNode.sa
Attribute = DbAttribute.sa
User = DbUser.sa
Extra = DbExtra.sa
Group = DbGroup.sa
Path = DbPath.sa

string_to_op = {
    "==": lambda e: e.__eq__,
    "=": lambda e: e.__eq__,
    ">=": lambda e: e.__ge__,
    "<=": lambda e: e.__le__,
    ">": lambda e: e.__gt__,
    "<": lambda e: e.__lt__,
    "!=": lambda e: e.__ne__
}

column_to_type = {
    "ival": "int",
    "fval": "float",
    "bval": "bool",
    "tval": "txt"
}

# Notes:
#   * Possible optimisation: when filtering on simple relationship. Instead of
#   joining the output node, and then the attribute, join the link, and then
#   directly the attribute. In fact, it might be an optimization to focus on
#   querying attribute, and then joining the node as we want.
#   * TODO: handle Extra table.


class QueryBuilder(object):

    def __init__(self):
        self.alias = {"input": aliased(Node, name="input"),
                      "output": aliased(Node, name="output"),
                      }

        self.filters = []
        self.group_filters = []
        self.attr_filters = []
        self.extra_filters = []
        self.attr_to_prefetch = []
        self.extra_to_prefetch = []

        self.input_filters = []
        self.output_filters = []

        self.input_attr_filters = []
        self.output_attr_filters = []

        self.input_attr_to_prefetch = []
        self.output_attr_to_prefetch = []

        # Tuple of the form: ([filters], min_depth, max_depth)
        self.children_attr_filters = []
        self.parents_attr_filters = []

        # Column we need to select in our query.
        self.columns_names = []

    def run_query(self):
        q = self._build_query()
        return q.all()

    def _build_relation_stmt(self, relation, filters):
        table = self.alias[relation]
        attr_filter = map(
            lambda a: Attribute.query()
            .filter(a, table.id == Attribute.dbnode_id).exists()
            .correlate(table),
            filters)

        sub_query = table.query(table.id).filter(*attr_filter).subquery()

        return table.id.in_(sub_query)

    def _build_depth_filter(self, relation,  filters):
        # Unpack (filters, min_depth, max_depth)
        filters, min_depth, max_depth = filters

        path_join, attr_join = (None, None)

        if relation == "children":
            path_join = Path.child_id == Node.id
            attr_join = Attribute.dbnode_id = Path.parent_id
        elif relation == "parents":
            path_join = Path.parent_id == Node.id
            attr_join = Attribute.dbnode_id = Path.child_id
        else:
            raise ValueError('Relation has to be either "children" or "parents"'
                             + 'but it was {}.'.format(relation))

        filter = Node.query(Node.id).join(Path, path_join)
        if min_depth:
            filter = filter.filter(Path.depth >= min_depth)
        if max_depth:
            filter = filter.filter(Path.depth <= max_depth)

        filter = filter.join(Attribute, attr_join).filter(*filters).subquery()

        return filter

    def _build_prefetch(self, attrs, relation=None):
        alias, join = (Attribute, Attribute)

        if relation:
            alias = aliased(Attribute)
            table = self.alias[relation]
            join = (alias, alias.dbnode_id == table.id)

        prefetch_keys = alias.key.in_(map(lambda a: a.key, attrs))
        prefetch_columns = (alias.key,) + tuple(
            set(
                map(lambda a: getattr(alias, a.column),
                    attrs)
            ))
        if relation:
            prefetch_columns = map(lambda c: c.label(relation + "_" + c.key),
                                   prefetch_columns)
            self.columns_names += map(lambda c: relation + "_" + c.key,
                                      prefetch_columns)
        else:
            self.columns_names += map(lambda c: c.key, prefetch_columns)

        return (join, prefetch_keys, prefetch_columns)

    def _build_query(self):

        q = Node.query()

        # TODO: better than a triple length check.
        if len(self.input_attr_filters) > 0 or len(self.input_filters) > 0 or \
                len(self.input_attr_to_prefetch) > 0:
            # needed to form a right join at the beginning, because you can't
            # do
            # select_form on an already filtered/join query.
            input = self.alias["input"]
            q = q.select_from(input).join(input.outputs)

        if len(self.group_filters) > 0:
            q = q.join(Group).filters(Group.name.in_(self.group_filters))

        q = q.filter(*self.filters)

        if len(self.attr_filters) > 0:
            filters = map(
                lambda a:
                Attribute.query(Attribute.dbnode_id).filter(a).as_scalar(),
                self.attr_filters
            )
            attr_filters = and_(*map(lambda a: Node.id.in_(a), filters))
            q = q.filter(attr_filters)

        if len(self.attr_to_prefetch) > 0:
            join, prefetch_keys, prefetch_columns = self._build_prefetch(
                self.attr_to_prefetch)
            q = q.join(join)

            q = q.filter(prefetch_keys)
            q = q.add_columns(*prefetch_columns)

        if len(self.input_filters) > 0:
            q = q.filter(*self.input_filters)

        if len(self.input_attr_filters) > 0:
            stmt = self._build_relation_stmt("input",
                                             self.input_attr_filters)
            q = q.filter(stmt)

        if len(self.output_attr_filters) > 0 or len(self.output_filters) > 0 or \
            len(self.output_attr_to_prefetch) > 0:
            q = q.join(self.alias["output"], Node.outputs)

        if len(self.output_filters) > 0:
            q = q.filter(*self.output_filters)

        if len(self.output_attr_filters) > 0:
            stmt = self._build_relation_stmt("output",
                                             self.output_attr_filters)
            q = q.filter(stmt)

        if len(self.children_attr_filters) > 0:
            stmt = self._build_depth_filter("children", self.children_attr_filters)
            q = q.filter(Node.id.in_(stmt))

        if len(self.parents_attr_filters) > 0:
            stmt = self._build_depth_filter("parents", self.parents_attr_filters)
            q = q.filter(Node.id.in_(stmt))

        # Prefetch using a left outer join. If an attribute doesn't exist, then
        # ¯\_(ツ)_/¯

        if len(self.input_attr_to_prefetch) > 0:
            join, prefetch_keys, prefetch_columns = self._build_prefetch(
                self.input_attr_to_prefetch, relation="input")
            q = q.join(join)
            q = q.filter(prefetch_keys)
            q = q.add_columns(*prefetch_columns)

        if len(self.output_attr_to_prefetch) > 0:
            join, prefetch_keys, prefetch_columns = self._build_prefetch(
                self.output_attr_to_prefetch, relation="output")
            q = q.join(join)
            q = q.filter(prefetch_keys)
            q = q.add_columns(*prefetch_columns)

        return q

    def get_query(self):
        return self._build_query()

    def filter_class(self, classes):
        stmt = or_(*map(lambda c: Node.type.like(c + "%"), classes))
        self.filters.append(stmt)

    def filter_group(self, groups):
        # self.q = self.q.join(Group.dbnodes).filter(Group.name.in_(groups))
        # TODO: add a way to joinafter after the input join.
        self.group_filters += list(groups)

    def filter_id(self, ids):
        self.filters.append(Node.id.in_(ids))

    def filter_uuid(self, uuids):
        self.filters.append(Node.uuid.in_(uuids))

    def filter_label(self, labels):
        self.filters.append(Node.label.in_(labels))

    def filter_description(self, descs):
        self.filters.append(Node.description.in_(descs))

    def filter_time(self, times):
        raise NotImplementedError("filter_time is not implemented yet.")

    def filter_attr(self, filters, extra=False, prefetch=False):
        _filters_list, _prefetch_list = (self.attr_filters, self.attr_to_prefetch) if \
            not extra else \
            (self.extra_filters, self.extra_to_prefetch)

        _filters_list.append(
            or_(*map(partial(self._attr_filter_stmt, extra=extra), filters))
        )

        if prefetch:
            _prefetch_list += filters

    def filter_input_attr(self, filters, extra=False, link=None,
                          prefetch=False):
        # TODO: support for extra
        _filters_list, _prefetch_list = (self.input_attr_filters,
                                         self.input_attr_to_prefetch) \
            if not extra else \
            (self.input_extra_filters, self.input_extra_to_prefetch)

        _filters_list.append(
            or_(*map(partial(self._attr_filter_stmt), filters))
        )

        if prefetch:
            _prefetch_list += filters

    def filter_output_attr(self, filters, extra=False, link=None,
                           prefetch=False):
        # TODO: support for extra
        _filters_list, _prefetch_list = (self.output_attr_filters,
                                         self.output_attr_to_prefetch) \
            if not extra else \
            (self.output_extra_filters, self.output_extra_to_prefetch)

        _filters_list.append(
            or_(*map(partial(self._attr_filter_stmt, extra=extra), filters))
        )

        if prefetch:
            _prefetch_list += filters

    def filter_parents_attr(self, filters, extra=False, min_depth=None,
                            max_depth=None):
        self.parents_attr_filters.append((
            or_(*map(partial(self._attr_filter_stmt, extra=extra), filters)),
            min_depth, max_depth)
        )

    def filter_children_attr(self, filters, extra=False, min_depth=None,
                             max_depth=None):
        # TODO: handle extra table.
        self.children_attr_filters.append((
            or_(*map(partial(self._attr_filter_stmt, extra=extra), filters)),
            min_depth, max_depth)
        )

    def prefetch_attr(self, *args, **kwargs):
        raise NotImplementedError("prefetch_attr is not implemented yet.")

    def filter_relation(self, relation, query, rename=None, prefetch=False):
        # TODO: proper error message.
        _table = self.alias[relation]
        _filters = None
        if relation == "input":
            _filters = self.input_filters
        elif relation == "output":
            _filters = self.output_filters


        stmt = _table.id.in_(subquery.with_entities(Node.id))
        _filters.append(stmt)

    # TODO: replace extra to use the table arg
    def _attr_filter_stmt(self, _filter, extra=False):
        table = Extra if extra else Attribute
        stmt = table.key == _filter.key

        if _filter.op is not None and _filter.value is not None:
            # TODO: Error handling + refactoring somewhere else
            stmt = and_(stmt,
                        string_to_op[_filter.op]
                        (getattr(table, _filter.column))(_filter.value),
                        # Is this useful ? Performance wise.
                        table.datatype == column_to_type[_filter.column]
                        )

        return stmt
