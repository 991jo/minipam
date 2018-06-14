#!/usr/bin/env python3

# this is a little demo for the xmlrpc capabilities of minipam

from xmlrpc.client import ServerProxy

server = ServerProxy("http://localhost:8000/")

print(server.system.listMethods())
server.add_net("192.168.0.0/16")
server.add_net("192.168.0.0/17")
server.add_net("192.168.0.0/18")
server.add_net("192.168.0.0/19")
print(server.get_net("192.168.0.0/14", 2))
