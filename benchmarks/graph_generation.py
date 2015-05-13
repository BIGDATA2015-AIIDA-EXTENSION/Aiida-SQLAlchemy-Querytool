#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import string
from itertools import product

from aiida import load_dbenv
load_dbenv()

from aiida.djsite.db.models import DbNode as Node, DbLink as Link, \
    DbAttribute as Attr, DbUser as User
from aiida.orm.data.parameter import ParameterData
from aiida.orm.data.remote import RemoteData
from aiida.orm.data.structure import StructureData
from aiida.orm.data.array.kpoints import KpointsData
from aiida.orm.data.array.trajectory import TrajectoryData
from aiida.orm.code import Code

TOTAL_TO_CREATE = 100

type_choice = map(lambda e: e._query_type_string, [Code, ParameterData,
                                                   RemoteData, StructureData,
                                                   KpointsData, TrajectoryData])
from django import conf
from django.db import transaction
from django.db.models import Max
conf.DEBUG = False

type_to_column = {
    "float": "fval",
    "text": "tval",
    "int": "ival",
    "bool": "bval"
}

fixed_attr = [("energy", "float"), ("number_of_atoms", "int"), ("wall_time",
                                                                "text"),
              ("parser", "text"), ("max_wallclock_seconds", "int"), ("pcb1",
                                                                     "bool"),
              ("pcb2", "bool"), ("pcb3", "bool"), ("SYSTEM.degauss", "float"),
              ("SYSTEM.smearing", "text"), ("SYSTEM.ecutwfc", "float"),
              ("SYSTEM.ecutrho", "float")]


def get_tmp_user():
    u = User.objects.get_or_create(password='', email="tmp@benchmark")[0]
    return u

USER = get_tmp_user()


def get_random_ids(n):
    """
    Query random inputs node. Used to batch query a set of input instead of
    querying one at a time.
    """
    max_ = Node.objects.aggregate(Max('id'))['id__max']
    ids = random.sample(xrange(max_), n)
    return ids
    # No need to query the node: just return the ids.
    # nodes = Node.objects.filter(id__in(ids))


def create_node(inputs=None):
    """Generate a Node with its attributes, and the corresponding link from the
    input"""
    n = Node.objects.create(type=random.choice(type_choice), user=USER)
    attributes = create_attributes(n.id)
    if inputs is not None:
        if isinstance(inputs[0], Node):
            inputs = map(lambda n: n.id, inputs)
        links = create_links(inputs, n.id)

    return n


def generate_val(attr):
    if attr[1] == "text":
        return random.choice(text_val)
    if attr[1] == "int":
        return random.randint(-100000, 100000)
    if attr[1] == "float":
        return random.uniform(-100000.0, 100000.0)
    if attr[1] == "bool":
        return bool(random.randint(0, 1))


def create_attributes(node_id):
    # Node has to be created
    n_fixed_attr = random.randint(3, 7)
    n_random_attr = random.randint(5, 13)
    attrs = random.sample(fixed_attr, n_fixed_attr) + \
        random.sample(random_attr, n_random_attr)
    with_values = map(lambda a: a + tuple([generate_val(a)]), attrs)

    attr_list = map(lambda a: create_attribute(a, node_id), with_values)
    return attr_list

def generate_label():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))

def create_links(inputs, outputs):
    """Does a cross product link between intputs and outputs. Often, you only want
    one input and several outputs or the converse."""
    if not isinstance(inputs, list):
        inputs = [inputs]
    if not isinstance(outputs, list):
        outputs = [outputs]
    cross = product(inputs, outputs)
    links = map(lambda e: Link.objects.create(input_id=e[0], output_id=e[1],
                                              label=generate_label()),
                cross)
    return links


def create_attribute(tup, node_id):
    key, type_, val = tup
    column = type_to_column[type_]

    dict_val = {
        "key": key,
        "datatype": type_,
        column: val,
        "dbnode_id": node_id
    }

    return Attr.objects.create(**dict_val)


text_val = ['5BD2N', '7NL2U', 'Y3Q8R', 'RYK6A', 'SSPT8', 'STE1F', 'LI264',
            'GS2VA', 'FLSUV', '4IFKJ', 'CFE56N', '1SY78B', 'H999JX', 'E24T8M',
            'CG2G7Y', '0N7MCT', 'KSEG62', 'XIAKL2', 'B2IYK7', 'U5KJ26',
            'U2OMXLQ', 'G4EFSKG', 'CMXSLA1', 'Y2FMMH3', 'XLQRR9T', '2EBFKF0',
            'PGGRCXK', 'AFPJFBP', '2Q2X767', '68ICRT4', '5MDORDSM', '399V5K4S',
            '0RIGTQJ7', 'HSEPZRAN', '8PV7B7VO', 'NNVVWG2V', 'D348ZZMB',
            'B7GM5OPU', 'RLD8CRZ8', 'VFX1DX7Y', 'BPGV79AWV', 'CH01ZCBQ2',
            'KG8SK9JXD', '7ATVPKFVH', '2YOP8XKUR', 'BB14KV9DS', '9VFOG759C',
            'NAAQYI5YX', '7IDWTXTY3', 'M6OUUYQED']

random_attr = [('UDPCU', 'float'), ('00VB3', 'float'), ('2PW0U', 'text'),
               ('EZXOV', 'int'), ('HWIVQ', 'text'), ('JAKYY', 'text'),
               ('B5FE1K', 'int'), ('GYWFBL', 'text'), ('N7ZHA0', 'int'),
               ('LI8LP4', 'bool'), ('M9E1T1B', 'bool'), ('2SJBG4I', 'int'),
               ('9939Y59', 'text'), ('37Z5E86', 'float'), ('88K5H1B3', 'int'),
               ('O7T4ZB8K', 'bool'), ('SCS2LBMR', 'int'), ('U6M733X2', 'float'),
               ('3VIV8L2GA', 'bool'), ('SVFC020J4', 'text'), ('6MM8HFKWR',
                                                              'text'),
               ('PB91E5WQC', 'bool'), ('KGRIP5QQM', 'int'), ('ENO868QAJ',
                                                             'float'),
               ('Q7UAXR5YM', 'int'), ('7S9588R9V', 'float'), ('OG7II0VID',
                                                              'float'),
               ('99CNK2RZN', 'int')]


if __name__ == '__main__':
    nodes_number = 0
    print("Begin.")
    while nodes_number < TOTAL_TO_CREATE:
        with transaction.commit_on_success():
            create_components = random.uniform(0,1) > 0.2
            nodes = []
            if create_components:
                print("New components.")
                inputs_number = random.randint(3, 4)
                inputs = [create_node() for _ in range(inputs_number)]
                nodes += inputs
                node = create_node(inputs)
                # We create 7 initials nodes, then randomly append stuff to it.
                for _ in range(6):
                    inputs_number = random.randint(1, 3)
                    inputs = random.sample(nodes, inputs_number)
                    nodes.append(create_node(inputs))
                for _ in range(50):
                    p = random.uniform(0, 1)
                    # This gives us a 50% chances to go up to 10 nodes.
                    if p > 0.98:
                        break
                    inputs_number = random.randint(2, 4)
                    # We use [-6:] to select the input in the last 6.
                    # The goal is to great a bigger depth
                    inputs = random.sample(nodes[-6:], inputs_number)
                    nodes.append(create_node(inputs))

            # Extending already existing components.
            else:
                print("Extending components.")
                input_sets = get_random_ids(50)
                for _ in range(20):
                    p = random.uniform(0,1)
                    if p > 0.93:
                        break
                    inputs_number = random.randint(2, 4)
                    inputs = random.sample(input_sets, inputs_number)
                    nodes.append(create_node(inputs))

            print("{} new nodes added :)".format(len(nodes)))
            nodes_number += len(nodes)
