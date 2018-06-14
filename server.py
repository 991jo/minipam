import sqlite3
from xmlrpc import server

import config


def get_net(net, depth=0):
    """
    returns networks within the given network.
    This network does not have to exist in the database, but with depth=0 no children
    will be returned and the output is empty if it is not in the database.
    :param net: the network (ip/subnet maks) which should be returned
    :param depth: how many levels of children should be added. Default is 0, -1
    means add all children.
    :returns: net_dict dictionary, might by empty
    """
    #TODO
    return None

def add_net(net):
    """
    adds a network to the database.
    you can add a network of which some subnets are already used.
    Those will then be children of the new network.
    If the network already existed nothing will be changed.
    :param net: a network in cidr notation
    """
    #TODO
    return None

def del_net(net, recursive=False):
    """
    deletes the given network.
    :param net: a network in cidr notation
    :param recursive: whether to delete all children or not
    """
    #TODO
    return None

def claim_net(net, size):
    """
    claims a network of size directly in the given network.
    :param net: the network in which the new network should be added
    :param size: the subnet mask, for example 8 or 27
    :returns: the net_dict dictionary of the newly created network
    """
    #TODO
    return None

def add_tag(net, tag_name, tag_value):
    """
    adds a tag to the network
    :param net: the network to which the tag should be added
    :param tag_name: the name of the tag
    :param tag_value: the value of the tag
    :returns:
    :raises TagExists: raises a TagExists error if the tag already exists
    """
    #TODO
    return None

def delete_tag(net, tag_name):
    """
    deletes a given tag from that network.

    :param net: the network from which the tag should be deleted.
    :param tag_name: the name of the tag to delete.
    :returns: name and value of the deleted tag.
    :raises TagDoesNotExist: raises a TagDoesNotExist error if the tag does not
    exist.
    """
    #TODO
    return None

def modify_tag(net, tag_name, tag_value):
    """
    changes the tag for the given network to the new value.

    :param net: the network in cidr notation.
    :param tag_name: the name of the tag
    :param tag_value: the new value of the tag
    :raises TagDoesNotExist: raises a TagDoesNotExist error if the tag does not
    exist.
    """
    #TODO
    return None

def get_tag(net, tag_name):
    """
    returns the value of a tag for the given network.

    :param net: the network in cidr notation
    :param tag_name: the name of the tag
    :returns: the tag value.
    :raises TagDoesNotExist: raises a TagDoesNotExist error if the tag does not
    exist.
    """
    #TODO
    return None

def get_tags(net):
    """
    returns a dict of all tags for the given network.

    :param net: the network in cidr notation
    :returns: a dict containing all tags and values.
    :raises NetDoesNotExist: raises a NetDoesNotExist error if the tag does not
    exist.
    """
    #TODO
    return None
