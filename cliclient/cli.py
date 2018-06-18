import argparse
from xmlrpc.client import ServerProxy
from pprint import PrettyPrinter

parser = argparse.ArgumentParser(description="a CLI client for minipam")
parser.add_argument("server", nargs=1, type=str, metavar="server")
group = parser.add_mutually_exclusive_group()
group.add_argument("--add-net","-an", nargs=1, type=str, metavar="NET")
group.add_argument("--delete-net","-dn", nargs=1, type=str, metavar="NET")
group.add_argument("--get-net","-gn", nargs=1, type=str, metavar="NET")
group.add_argument("--claim-net","-cn", nargs=2, type=str, metavar=("NET", "PREFIXLEN"))
group.add_argument("--add-tag","-at", nargs=3, type=str, metavar=("NET", "TAGNAME", "TAGVALUE"))
group.add_argument("--delete-tag","-dt", nargs=2, type=str, metavar=("NET", "TAGNAME"))
group.add_argument("--modify-tag","-mt", nargs=3, type=str, metavar=("NET", "TAGNAME", "TAGVALUE"))
group.add_argument("--get-tag","-gt", nargs=2, type=str, metavar=("NET", "TAGNAME"))
group.add_argument("--get-tags","-gts", nargs=1, type=str, metavar="NET")
args = parser.parse_args()

with ServerProxy(args.server[0]) as server:
    pp = PrettyPrinter()

    if args.get_net is not None:
        result = server.get_net(args.get_net[0])

        def recursive_print(net, indent=0):
            print(" "*indent, net["cidr"])
            for child in net["children"]:
                recursive_print(child, indent=indent+2)

        recursive_print(result)
    elif args.add_net is not None:
        server.add_net(args.add_net[0])
    elif args.delete_net is not None:
        server.delete_net(args.delete_net[0])
    elif args.claim_net is not None:
        result = server.claim_net(args.claim_net[0], int(args.claim_net[1]))
        pp.pprint(result)

    elif args.add_tag is not None:
        server.add_tag(args.add_tag[0], args.add_tag[1], args.add_tag[2])
    elif args.get_tag is not None:
        result = server.get_tag(args.get_tag[0], args.get_tag[1])
        pp.pprint(result)
    elif args.get_tags is not None:
        result = server.get_tags(args.get_tags[0])
        pp.pprint(result)
    elif args.modify_tag is not None:
        server.modify_tag(args.modify_tag[0], args.modify_tag[1], args.modify_tag[2])
    elif args.delete_tag is not None:
        server.delete_tag(args.delete_tag[0], args.delete_tag[1])
