import sqlite3
import sys
from xmlrpc.server import SimpleXMLRPCServer
from ipaddress import ip_network, ip_address

#from minipam import config
from minipam import config
from minipam.fault_handling import raise_fault
from minipam.ip_utils import *

db_conn = None;

def start_database_connection():
    global db_conn
    """
    Sets up the database connection and makes sure that the required tables exist.
    """
    if db_conn is None:
        db_conn = sqlite3.connect(config.database_file)
        db_conn.row_factory = sqlite3.Row

    c = db_conn.cursor()

    # enable foreign key support in sqlite
    c.execute("PRAGMA foreign_keys = ON");

    # set up the tables if they do not exist yet
    c.execute("CREATE TABLE IF NOT EXISTS networks"
            "(id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "net TEXT UNIQUE," # the net field is redundant to the address and netmask fields,
                        # the first is for human readable data
                        # the later is for working with queries.
            "address INTEGER,"
            "netmask INTEGER)")

    c.execute("CREATE TABLE IF NOT EXISTS tags"
            "(network_id INTEGER NOT NULL,"
            "tag_name TEXT NOT NULL,"
            "tag_value TEXT,"
            "PRIMARY KEY (network_id, tag_name)"
            "FOREIGN KEY (network_id) REFERENCES networks(id)"
            "ON UPDATE CASCADE " #space is needed to prevent the parser from reading CASCADEON
            "ON DELETE CASCADE"
            ")")


    # save possible changes
    db_conn.commit()

def close_database_connection():
    """
    closes the database connection
    """

    global db_conn
    db_conn.close()
    db_conn = None

def get_net(net, depth=-1):
    """
    returns networks within the given network.
    This network does not have to exist in the database
    if the network does not exist in the database the "network_in_database"
    variable in the returned dict is False. It is true otherwise.
    :param net: the network (ip/subnet maks) which should be returned
    :param depth: how many levels of children should be added. Default is -1 (return everything)
    means add all children.
    :returns: net_dict dictionary, might by empty
    """
    try:
        network = ip_network(net)
        c = db_conn.cursor()
        c.execute("SELECT net, address, netmask FROM networks "
                "WHERE netmask >= ? AND address >= ? AND "
                "address <= ? ORDER BY address ASC, netmask ASC",
                (network.prefixlen,
                    network_address_to_int(network),
                    network_broadcast_to_int(network)))
        results = c.fetchall()
        #if len(results) == 0:
        #    raise_fault("NetworkNotInDatabase")

        if len(results) == 0 or results[0]["net"] != str(network):
            ret = { "address": str(network.network_address),
                    "cidr" : str(network),
                    "netmask": network.prefixlen,
                    "children": list(),
                    "network_in_database": False}
            start = 0
            if len(results) == 0:
                return ret
        else:
            ret = { "address" : results[0]["net"].split("/")[0],
                    "cidr" : results[0]["net"],
                    "netmask" : results[0]["netmask"],
                    "children" : list(),
                    "network_in_database": True}
            start = 1

        def insert_in_netlist(ip_net, netlist, remaining_depth):
            """
            This function creates a network dictionary and appends it recursive
            in one of the network dictionaries in the netlist or appends it to
            the netlist if it does not fit into the dicts already in the list.
            If the remaining_depth reaches 0 it aborts.
            """
            for c in netlist:
                c_net = ip_network(c["cidr"])
                if c_net.overlaps(ip_net):
                    if remaining_depth != 0:
                        insert_in_netlist(ip_net, c["children"], remaining_depth-1)
                    return
            netlist.append({"address" : n["net"].split("/")[0],
                "cidr": n["net"],
                "netmask" : n["netmask"],
                "children" : list(),
                "network_in_database" : True})

        if depth != 0:
            for n in results[start:]:
                n_net = ip_network(n["net"])
                insert_in_netlist(n_net, ret["children"], depth-1)

        return ret

    except ValueError:
        raise_fault("InvalidNetworkDescription");

def add_net(net):
    """
    adds a network to the database.
    you can add a network of which some subnets are already used.
    Those will then be children of the new network.
    If the network already existed nothing will be changed.
    :param net: a network in cidr notation
    :raises Fault: raises a xmlrpc.server.Fault with an error code and message
    """
    try:
        network = ip_network(net)
        c = db_conn.cursor()
        c.execute("INSERT OR IGNORE INTO networks (net, address, netmask) VALUES (?,?,?)", (str(network), network_address_to_int(network), network.prefixlen))
        db_conn.commit()

    except ValueError:
        raise_fault("InvalidNetworkDescription");

def delete_net(net, recursive=False):
    """
    deletes the given network.
    :param net: a network in cidr notation
    :param recursive: whether to delete all children or not
    """
    try:
        network = ip_network(net)
        c = db_conn.cursor()
        if recursive:
            c.execute("DELETE FROM networks WHERE netmask >= ? AND address >= ? and address <= ?",
                    (network.prefixlen, network_address_to_int(network), network_broadcast_to_int(network)))
        else:
            c.execute("DELETE FROM networks WHERE net = ?" , (str(network),))
        db_conn.commit()
        return None
    except ValueError:
        raise_fault("InvalidNetworkDescription")

def claim_net(net, size):
    """
    claims a network of size directly in the given network.
    :param net: the network in which the new network should be added
    :param size: the subnet mask, for example 8 or 27
    :returns: the net_dict dictionary of the newly created network
    :raises NoMatchingGapAvailable: raised if there is no space for a subnet of
    this size in this network.
    """
    try:

        network = ip_network(net)
        required_gap = 2**(network.max_prefixlen - size)

        if size < network.prefixlen:
            raise_fault("NoMatchingGapAvailable")

        nets = get_net(net, depth=1)

        if len(nets["children"]) == 0:
            network_string = str(network.network_address) + "/" + str(size)
            add_net(network_string)
            return get_net(network_string, depth=0)
        else: #at least one child exists.

            def next_start_address(net, size):
                if size >= net.prefixlen:
                    start_addr = network_broadcast_to_int(net) + 1
                else:
                    size_diff = net.prefixlen - size
                    supernet = net.supernet(size_diff)
                    start_addr = int(supernet.network_address) + 2**(supernet.max_prefixlen-supernet.prefixlen)
                return start_addr

            smallest_gap = None

            # start and end gaps
            first_block = ip_network(nets["children"][0]["cidr"])
            first_gap = network_address_to_int(first_block) - network_address_to_int(network)

            if first_gap >= required_gap:
                smallest_gap = { "address" : network.network_address,
                        "length" : first_gap }

            # add all gaps between blocks
            for i, n in enumerate(nets["children"][:-1]):
                net1 = ip_network(n["cidr"])
                net2 = ip_network(nets["children"][i+1]["cidr"])
                start_addr = next_start_address(net1, size)
                gap = network_address_to_int(net2) - start_addr
                if gap >= required_gap and (smallest_gap is None or gap < smallest_gap["length"]):
                    smallest_gap = {"address" : ip_address(start_addr),
                            "length": gap}

            # the last gap
            last_block = ip_network(nets["children"][-1]["cidr"])
            last_gap_start = next_start_address(last_block, size)
            last_gap =  network_broadcast_to_int(network) - last_gap_start + 1
            if last_gap >= required_gap and (smallest_gap is None or last_gap < smallest_gap["length"]):
                smallest_gap = { "address" : ip_address(last_gap_start),
                        "length" :last_gap}

            if smallest_gap is None:
                raise_fault("NoMatchingGapAvailable")

            network_string = str(smallest_gap["address"]) + "/" + str(size)
            add_net(network_string)
            return get_net(network_string)

    except ValueError:
        raise_fault("InvalidNetworkDescription")


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
    try:
        network = ip_network(net)
        c = db_conn.cursor()
        c.execute("INSERT INTO tags (network_id, tag_name, tag_value) "
        "VALUES ((SELECT id FROM networks WHERE net = ?), ?, ?)",
        (net, tag_name, tag_value));
    except ValueError:
        raise_fault("InvalidNetworkDescription")
    except sqlite3.IntegrityError:
        raise_fault("TagExists")
    db_conn.commit()

def delete_tag(net, tag_name):
    """
    deletes a given tag from that network.

    :param net: the network from which the tag should be deleted.
    :param tag_name: the name of the tag to delete.
    :returns: name and value of the deleted tag.
    """
    try:
        network = ip_network(net)
        c = db_conn.cursor()
        c.execute("DELETE FROM tags WHERE network_id IN "
                "(SELECT id AS network_id FROM networks WHERE net = ?) AND "
                "tag_name = ?",
                (str(network), tag_name))
    except ValueError:
        raise_fault("InvalidNetworkDescription")
    db_conn.commit()

def modify_tag(net, tag_name, tag_value):
    """
    changes the tag for the given network to the new value.

    :param net: the network in cidr notation.
    :param tag_name: the name of the tag
    :param tag_value: the new value of the tag
    :raises TagDoesNotExist: raises a TagDoesNotExist error if the tag does not
    exist.
    """
    try:
        network = ip_network(net)
        c = db_conn.cursor()
        c.execute("UPDATE tags SET tag_value = ? "
                "WHERE network_id = (SELECT id FROM networks WHERE net = ?) "
                "AND tag_name=?",
                (tag_value, str(network), tag_name))
        db_conn.commit()
        if c.rowcount == 0:
            raise_fault("TagDoesNotExist")
    except ValueError:
        raise_fault("InvalidNetworkDescription")

def get_tag(net, tag_name):
    """
    returns the value of a tag for the given network.

    :param net: the network in cidr notation
    :param tag_name: the name of the tag
    :returns: the tag value.
    :raises TagDoesNotExist: raises a TagDoesNotExist error if the tag does not
    exist.
    """
    try:
        network = ip_network(net)
        c = db_conn.cursor()
        c.execute("SELECT tag_value FROM tags WHERE "
                "network_id = (SELECT id FROM networks WHERE net = ?) AND "
                "tag_name = ?",
                (str(network), tag_name))
        result = c.fetchone()
        if result is None:
            raise_fault("TagDoesNotExist")
        db_conn.commit()
        return result["tag_value"];

    except ValueError:
        raise_fault("InvalidNetworkDescription")

def get_tags(net):
    """
    returns a dict of all tags for the given network.

    :param net: the network in cidr notation
    :returns: a dict containing all tags and values.
    :raises NetDoesNotExist: raises a NetDoesNotExist error if the tag does not
    exist.
    """
    try:
        network = ip_network(net)
        c = db_conn.cursor()
        c.execute("SELECT tag_name, tag_value FROM tags WHERE "
                "network_id = (SELECT id FROM networks WHERE net = ?)",
                (str(network),))
        result = { r["tag_name"]:r["tag_value"] for r in c.fetchall() }
        return result;

    except ValueError:
        raise_fault("InvalidNetworkDescription")

def setup_xmlrpc_server():
    server = SimpleXMLRPCServer((config.xmlrpc_address, config.xmlrpc_port), allow_none=True)
    server.register_introspection_functions()
    server.register_multicall_functions()
    server.register_function(get_net, "get_net")
    server.register_function(add_net, "add_net")
    server.register_function(delete_net, "delete_net")
    server.register_function(claim_net, "claim_net")
    server.register_function(get_tag, "get_tag")
    server.register_function(add_tag, "add_tag")
    server.register_function(delete_tag, "delete_tag")
    server.register_function(modify_tag, "modify_tag")
    server.register_function(get_tags, "get_tags")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        close_database_connection()
        print("exiting")

if __name__ == "__main__":
    start_database_connection()
    print(get_net("192.168.0.0/16", 1))
    add_tag("192.168.0.0/16", "name", "lan network")
    add_tag("192.168.0.0/16", "name", "lan network2")
    setup_xmlrpc_server()




