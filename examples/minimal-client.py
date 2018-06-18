#!/usr/bin/env python3

# This is the most minimal examle which interacts with minipam via XML RPC.
from xmlrpc.client import ServerProxy
server = ServerProxy("http://localhost:8000")
print(server.get_net("0.0.0.0/0"))
