{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "from aiida.orm.querytool2 import Attribute"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "from aiida.orm.querytool2 import Attribute"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "from aiida.orm.querytool2 import Attribute"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [],
   "source": [
    "from itertools import starmap"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "list(starmap(Attribute, [(1, 2, 3), (4, 5, 6)]))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "from aiida.djsite.db.models import DbAttribute, DbLink, DbNode, DbGroup"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [],
   "source": [
    "Node = DbNode.sa; Attr = DbAttr.sa; Group = DbGroup.sa"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [],
   "source": [
    "Node = DbNode.sa; Attr = DbAttribute.sa; Group = DbGroup.sa"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "metadata": {},
   "outputs": [],
   "source": [
    "from sqlalchemy import and_, or_, not_, func"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [],
   "source": [
    "from sqlalchemy import exists"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "metadata": {},
   "outputs": [],
   "source": [
    "Node.query(Node.id, Attr.key).join(Attr)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "metadata": {},
   "outputs": [],
   "source": [
    "Node.query(Node.id, Attr.key).join(Attr).filter(exists(1))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "metadata": {},
   "outputs": [],
   "source": [
    "from sqlalchemy.sql.expression import select, exists"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "metadata": {},
   "outputs": [],
   "source": [
    "Node.query(Node.id, Attr.key).join(Attr).filter(exists(1))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "metadata": {},
   "outputs": [],
   "source": [
    "exists"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "metadata": {},
   "outputs": [],
   "source": [
    "a1 = select([Attr.dbnode_id]).where(and_(Attr.key == \"ELECTRONS.mixing_beta\", Attr.fval > 0)).exists()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "metadata": {},
   "outputs": [],
   "source": [
    "a1 = Attr.query(Attr.key).filter(and_(Attr.key == \"ELECTRONS.mixing_beta\", Attr.fval > 0)).exists()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "metadata": {},
   "outputs": [],
   "source": [
    "a1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "metadata": {},
   "outputs": [],
   "source": [
    "print a1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "metadata": {},
   "outputs": [],
   "source": [
    "Node.query(Node.id, Attr.key).join(Attr).filter(a1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "metadata": {},
   "outputs": [],
   "source": [
    "print Node.query(Node.id, Attr.key).join(Attr).filter(a1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "metadata": {},
   "outputs": [],
   "source": [
    "Node.query(Node.id, Attr.key).join(Attr).filter(exists([1]))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "metadata": {},
   "outputs": [],
   "source": [
    "Node.query(Node.id, Attr.key).join(Attr).filter(exists([1]).where(and_(Attr.key == \"ELECTRONS.mixing_beta\", Attr.fval > 0)))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 24,
   "metadata": {},
   "outputs": [],
   "source": [
    "print Node.query(Node.id, Attr.key).join(Attr).filter(exists([1]).where(and_(Attr.key == \"ELECTRONS.mixing_beta\", Attr.fval > 0)))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 25,
   "metadata": {},
   "outputs": [],
   "source": [
    "print Node.query(Node.id, Attr.key).join(Attr).filter(exists([1]).where(and_(Attr.key == \"ELECTRONS.mixing_beta\", Attr.fval > 0, Attr.dbnode_id == Node.id)))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 26,
   "metadata": {},
   "outputs": [],
   "source": [
    "from sqlalchemy import aliased"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 27,
   "metadata": {},
   "outputs": [],
   "source": [
    "from sqlalchemy import alias"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 28,
   "metadata": {},
   "outputs": [],
   "source": [
    "print Node.query(Node.id, Attr.key).join(Attr).filter(exists([1]).where(and_(Attr.key == \"ELECTRONS.mixing_beta\", Attr.fval > 0, Attr.dbnode_id == Node.id)).as_scalar())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 29,
   "metadata": {},
   "outputs": [],
   "source": [
    "a1 = select([Attr.dbnode_id]).where(and_(Attr.key == \"ELECTRONS.mixing_beta\", Attr.fval > 0)).exists().as_scalar()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 30,
   "metadata": {},
   "outputs": [],
   "source": [
    "a1 = select([Attr.dbnode_id]).where(and_(Attr.key == \"ELECTRONS.mixing_beta\", Attr.fval > 0)).as_scalar()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "metadata": {},
   "outputs": [],
   "source": [
    "a1 = select([1]).where(and_(Attr.key == \"ELECTRONS.mixing_beta\", Attr.fval > 0)).as_scalar()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 32,
   "metadata": {},
   "outputs": [],
   "source": [
    "a1 = select([1]).where(and_(Attr.key == \"ELECTRONS.mixing_beta\", Attr.fval > 0, Node.id == Attr.dbnode_id)).as_scalar()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 33,
   "metadata": {},
   "outputs": [],
   "source": [
    "print Node.query(Node.id, Attr.key).join(Attr).filter(exists(a1))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 34,
   "metadata": {},
   "outputs": [],
   "source": [
    "a1 = select([exists().where(and_(Attr.key == \"ELECTRONS.mixing_beta\", Attr.fval > 0, Node.id == Attr.dbnode_id))])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 35,
   "metadata": {},
   "outputs": [],
   "source": [
    "print a1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 36,
   "metadata": {},
   "outputs": [],
   "source": [
    "print Node.query(Node.id, Attr.key).join(Attr).filter(exists(a1))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 37,
   "metadata": {},
   "outputs": [],
   "source": [
    "print Node.query(Node.id, Attr.key).join(Attr).filter(a1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 38,
   "metadata": {},
   "outputs": [],
   "source": [
    "print Node.query(Node.id, Attr.key).join(Attr).filter(a1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 39,
   "metadata": {},
   "outputs": [],
   "source": [
    "a1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 40,
   "metadata": {},
   "outputs": [],
   "source": [
    "print a1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 41,
   "metadata": {},
   "outputs": [],
   "source": [
    "a1 = exists().where(and_(Attr.key == \"ELECTRONS.mixing_beta\", Attr.fval > 0, Node.id == Attr.dbnode_id))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 42,
   "metadata": {},
   "outputs": [],
   "source": [
    "a1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 43,
   "metadata": {},
   "outputs": [],
   "source": [
    "print a1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 44,
   "metadata": {},
   "outputs": [],
   "source": [
    "print Node.query(Node.id, Attr.key).join(Attr).filter(a1)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 45,
   "metadata": {},
   "outputs": [],
   "source": [
    "print Node.query(Node.id, Attr.key).join(Attr).filter(a1.correlate(Node))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 46,
   "metadata": {},
   "outputs": [],
   "source": [
    "a2 = exists().where(and_(Attr.key == \"CONTROL.max_seconds\", Attr.ival > 0, Node.id == Attr.dbnode_id))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 47,
   "metadata": {},
   "outputs": [],
   "source": [
    "print Node.query(Node.id, Attr.key).join(Attr).filter(a1.correlate(Node), a2.correlate(Node))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 48,
   "metadata": {},
   "outputs": [],
   "source": [
    "a1 = Attr.query().filter(Attr.key == \"ELECTRONS.mixing_beta\", Attr.fval > 0, Node.id == Attr.dbnode_id))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 49,
   "metadata": {},
   "outputs": [],
   "source": [
    "a1 = Attr.query().filter(Attr.key == \"ELECTRONS.mixing_beta\", Attr.fval > 0, Node.id == Attr.dbnode_id)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 50,
   "metadata": {},
   "outputs": [],
   "source": [
    "a1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 51,
   "metadata": {},
   "outputs": [],
   "source": [
    "print a1"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 52,
   "metadata": {},
   "outputs": [],
   "source": [
    "print a1.exists()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 53,
   "metadata": {},
   "outputs": [],
   "source": [
    "a2 = Attr.query().filter(Attr.key == \"CONTROL.max_seconds\", Attr.ival > 0, Node.id == Attr.dbnode_id)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 54,
   "metadata": {},
   "outputs": [],
   "source": [
    "a1 = Attr.query().filter(Attr.key == \"ELECTRONS.mixing_beta\", Attr.fval > 0, Node.id == Attr.dbnode_id).exists()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 55,
   "metadata": {},
   "outputs": [],
   "source": [
    "a2 = Attr.query().filter(Attr.key == \"CONTROL.max_seconds\", Attr.ival > 0, Node.id == Attr.dbnode_id).exists()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 56,
   "metadata": {},
   "outputs": [],
   "source": [
    "print Node.query(Node.id, Attr.key).join(Attr).filter(a1.correlate(Node), a2.correlate(Node))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 57,
   "metadata": {},
   "outputs": [],
   "source": [
    "print Node.query(Node.id, Attr.key).join(Attr).filter(a1.correlate(Node), a2.correlate(Node)).all()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 58,
   "metadata": {},
   "outputs": [],
   "source": [
    "Node.query(Node.id, Attr.key).join(Attr).filter(a1.correlate(Node), a2.correlate(Node)).all()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 59,
   "metadata": {},
   "outputs": [],
   "source": [
    "Node.query(Node, Attr.key).join(Attr).filter(a1.correlate(Node), a2.correlate(Node)).all()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 60,
   "metadata": {},
   "outputs": [],
   "source": [
    "%notebook"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 61,
   "metadata": {},
   "outputs": [],
   "source": [
    "%pastebin"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 62,
   "metadata": {},
   "outputs": [],
   "source": [
    "%history"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 63,
   "metadata": {},
   "outputs": [],
   "source": [
    "%notebook sql.ipynb"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 64,
   "metadata": {},
   "outputs": [],
   "source": [
    "%notebook -e sql.ipynb"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 65,
   "metadata": {},
   "outputs": [],
   "source": [
    "a1 = Attr.query().filter(Attr.key == \"ELECTRONS.mixing_beta\", Attr.fval > 0, Node.id == Attr.dbnode_id).exists()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 66,
   "metadata": {},
   "outputs": [],
   "source": [
    "a2 = Attr.query().filter(Attr.key == \"CONTROL.max_seconds\", Attr.ival > 0, Node.id == Attr.dbnode_id).exists()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 67,
   "metadata": {},
   "outputs": [],
   "source": [
    "%save sql_filter.py"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 68,
   "metadata": {},
   "outputs": [],
   "source": [
    "%notebook -e sql.ipynb"
   ]
  }
 ],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 0
}
