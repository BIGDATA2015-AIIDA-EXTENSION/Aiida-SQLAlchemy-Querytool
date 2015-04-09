# -*- coding: utf-8 -*-

__all__ = ['QueryBuilder']


from aiida.djsite.db.models import DbNode, DbAttribute, DbUser, DbExtra, \
    DbGroup, DbPath
from sqlalchemy import and_, or_, not_, func
from sqlalchemy.orm.query import aliased
from functools import partial
from operator import is_not

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
#   * Currently, it uses EXIST statement to filter the attributes. This
#   results in a twice slower performance compared to the Django's ORM. This
#   should be investigated, as this could also be applied in others cases (each
#   time we need to filter on several attributes). Django's ORM seems to use IN
#   statement + a filter directly into the join.


class QueryBuilder(object):

    def __init__(self):
        self.q = Node.query(Node)
        self.alias = {"input": aliased(Node),
                      "output": aliased(Node),
                      }

        # TODO: find a better way to store the differents filters and
        # prefetching attributes (other than a dict).

        self.filters = []
        self.group_filters = []
        self.attr_filters = []
        self.extra_filters = []
        self.attr_to_prefetch = []
        self.extra_to_prefetch = []

        # TODO: refactor this.
        self.input_filters = []
        self.output_filters = []

        self.input_attr_filters = []
        self.output_attr_filters = []
        self.input_attr_to_prefetch = []
        self.output_attr_to_prefetch = []

        # Tuple of the form: ([filters], min_depth, max_depth)
        self.children_attr_filters = []
        self.parents_attr_filters = []


    def run_query(self):
        # _build_query is a pure function.
        q = self._build_query(self.q)
        return q.all()

    def _build_query(self, q):
        # Different strat if only one attribute or several. If there is only
        # one, we can do a simple join + filter, it will work. Otherwise, we
        # need to filter using EXIST

        # TODO: better than a triple length check.
        if len(self.input_attr_filters) > 0 or len(self.input_filters) > 0 or \
            len(self.input_attr_to_prefetch) > 0:
            # needed to form a right join at the beginning, because you can't do
            # select_form on an already filtered/join query.
            input = self.alias["input"]
            q = q.select_from(input).join(input.outputs)

        if len(self.input_filters) > 0:
            q = q.filter(*self.input_filters)

        if len(self.input_attr_filters) > 0:
            input = self.alias["input"]
            exists_filter = map(
                lambda a: Attribute.query().filter(a, input.id == Attribute.dbnode_id).exists().
                correlate(input),
                self.input_attr_filters)

            sub_q = input.query(input.id).filter(*exists_filter).subquery()
            q = q.filter(input.id.in_(sub_q))

        if len(self.group_filters) > 0:
            q = q.join(Group).filters(Group.name.in_(self.group_filters))

        q = q.filter(*self.filters)

        if len(self.attr_filters) > 0 or len(self.attr_to_prefetch) > 0:
            q = q.join(Attribute)

        if len(self.attr_filters) > 0:
            # TODO: make a function for it ? the need might arise with
            # attribute on relationship
            exists_filter = map(
                lambda a: Attribute.query().filter(a, Node.id == Attribute.dbnode_id).exists().
                correlate(Node),
                self.attr_filters)
            q = q.filter(*exists_filter)

        if len(self.output_attr_filters) > 0 or len(self.output_filters) > 0 or \
            len(self.output_attr_to_prefetch) > 0:
            q = q.join(self.alias["output"], Node.outputs)

        if len(self.output_filters) > 0:
            q = q.filter(*self.output_filters)

        if len(self.output_attr_filters) > 0:
            output = self.alias["output"]
            exists_filter = map(
                lambda a: Attribute.query().filter(a, output.id == Attribute.dbnode_id).exists().
                correlate(output),
                self.output_attr_filters)

            sub_q = output.query(output.id).filter(*exists_filter).subquery()
            q = q.filter(output.id.in_(sub_q))

        if len(self.children_attr_filters) > 0:
            # TODO: handle multiple filters (correctly).
            # TODO: handle extra table.
            min_filters = map(lambda e: e[1], self.children_attr_filters)
            min_filters = filter(partial(is_not, None), min_filters)
            min_filters = map(lambda e: Path.depth > e, min_filters)

            max_filters = map(lambda e: e[2], self.children_attr_filters)
            max_filters = filter(partial(is_not, None), max_filters)
            max_filters = map(lambda e: Path.depth < e, max_filters)

            filters = map(lambda e:e[0], self.children_attr_filters)

            stmt = Node.query(Node.id).join(Path, Path.parent_id == Node.id).\
                filter(*min_filters).filter(*max_filters).\
                join(Attribute, Attribute.dbnode_id == Path.child_id).\
                filter(*filters).subquery()

            q = q.filter(Node.id.in_(stmt))

        if len(self.parents_attr_filters) > 0:
            min_filters = map(lambda e: e[1], self.parents_attr_filters)
            min_filters = filter(partial(is_not, None), min_filters)
            min_filters = map(lambda e: Path.depth > e, min_filters)

            max_filters = map(lambda e: e[2], self.parents_attr_filters)
            max_filters = filter(partial(is_not, None), max_filters)
            max_filters = map(lambda e: Path.depth < e, max_filters)

            filters = map(lambda e:e[0], self.parents_attr_filters)

            stmt = Node.query(Node.id).join(Path, Path.child_id == Node.id).\
                filter(*min_filters).filter(*max_filters).\
                join(Attribute, Attribute.dbnode_id == Path.parent_id).\
                filter(*filters).subquery()

            q = q.filter(Node.id.in_(stmt))

        # Prefetch using a left outer join. If an attribute doesn't exist, then
        # ¯\_(ツ)_/¯
        if len(self.attr_to_prefetch) > 0:
            prefetch_keys = map(lambda a: a.key, self.attr_to_prefetch)
            prefetch_columns = tuple(
                set(
                    map(lambda a: getattr(Attribute, a.column),
                        self.attr_to_prefetch)
                ))
            q = q.filter(Attribute.key.in_(prefetch_keys))
            q = q.add_columns(
                Attribute.key,
                *prefetch_columns
            )

        # TODO: Right now, input/output prefetching only work if there has
        # already been a filter (hence a join) done.
        if len(self.input_attr_to_prefetch) > 0:
            input_attr = aliased(Attribute)
            q = q.outerjoin(input_attr, input_attr.dbnode_id == self.alias["input"].id)

            prefetch_keys = map(lambda a: a.key, self.input_attr_to_prefetch)
            prefetch_columns = tuple(
                set(
                    map(lambda a: getattr(input_attr, a.column),
                        self.input_attr_to_prefetch)
                ))
            q = q.filter(input_attr.key.in_(prefetch_keys))
            q = q.add_columns(
                input_attr.key,
                *prefetch_columns
            )

        if len(self.output_attr_to_prefetch) > 0:
            output_attr = aliased(Attribute)
            q = q.outerjoin(output_attr, output_attr.dbnode_id == self.alias["output"].id)

            prefetch_keys = map(lambda a: a.key, self.output_attr_to_prefetch)
            prefetch_columns = tuple(
                set(
                    map(lambda a: getattr(output_attr, a.column),
                        self.output_attr_to_prefetch)
                ))
            q = q.filter(output_attr.key.in_(prefetch_keys))
            q = q.add_columns(
                output_attr.key,
                *prefetch_columns
            )

        return q

    def get_query(self):
        return self._build_query(self.q)

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

    def filter_relation(self, relation, subquery, rename=None):
        _filters, _table = None, None
        if relation == "input":
            _filters, _table = self.input_filters, self.alias["input"]
        elif relation == "output":
            _filters, _table = self.output_filters, self.alias["output"]

        if (_filters or _table) is None:
            raise NotImplementedError("We don't support support relation {}.".
                                      format(relation))

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

