from minipam.server import *

if __name__ == "__main__":
    start_database_connection()
    add_net("192.168.0.0/16")
    add_tag("192.168.0.0/16", "name", "lan network")
    add_tag("192.168.0.0/16", "name", "lan network2")
    setup_xmlrpc_server()




