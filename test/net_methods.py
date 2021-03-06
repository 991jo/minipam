import unittest

from os import remove
from xmlrpc.server import Fault
from minipam.server import *

class TestAddNetMethods(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        try:
            remove("test.db")
        except FileNotFoundError:
            pass
        config.database_file = "test.db"
        start_database_connection()

    @classmethod
    def tearDownClass(self):
        close_database_connection()
        remove("test.db")

    def test_add_net_normal(self):
        add_net("127.0.0.0/8")

    def test_add_net_duplicate(self):
        add_net("127.0.0.0/8")

    def test_add_net_host_bits_set(self):
        with self.assertRaises(Fault) as cm:
            add_net("127.0.0.1/8")
        self.assertEqual(cm.exception.faultString, "InvalidNetworkDescription")

class TestGetNetMethods(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        try:
            remove("test.db")
        except FileNotFoundError:
            pass
        config.database_file = "test.db"
        start_database_connection()

        add_net("127.0.0.0/8")
        add_net("127.0.0.0/16")

    @classmethod
    def tearDownClass(self):
        close_database_connection()
        remove("test.db")

    def test_get_net_normal(self):
        result = get_net("127.0.0.0/8")
        self.assertEqual(result["cidr"] , "127.0.0.0/8")
        self.assertEqual(len(result["children"]), 1)
        self.assertEqual(result["children"][0]["address"], "127.0.0.0")
        self.assertEqual(result["children"][0]["netmask"], 16)

    def test_get_net_depth_0(self):
        result = get_net("127.0.0.0/8", depth=0)
        self.assertEqual(result["cidr"] , "127.0.0.0/8")
        self.assertEqual(len(result["children"]), 0)
        self.assertEqual(type(result["children"]), list)

    def test_get_net_limited_depth(self):
        add_net("127.0.0.0/24")
        result = get_net("127.0.0.0/8", depth=1)
        self.assertEqual(result["cidr"] , "127.0.0.0/8")
        self.assertEqual(len(result["children"]), 1)
        self.assertEqual(result["children"][0]["address"], "127.0.0.0")
        self.assertEqual(result["children"][0]["netmask"], 16)
        self.assertEqual(len(result["children"][0]["children"]), 0)

    def test_get_net_host_bits_set(self):
        with self.assertRaises(Fault) as cm:
            get_net("127.0.0.1/8")
        self.assertEqual(cm.exception.faultString, "InvalidNetworkDescription")

    def test_get_net_not_in_db(self):
        result = get_net("0.0.0.0/0")
        self.assertEqual(result["cidr"] , "0.0.0.0/0")
        self.assertEqual(result["network_in_database"] , False)
        self.assertEqual(len(result["children"]), 1)
        self.assertEqual(result["children"][0]["address"], "127.0.0.0")
        self.assertEqual(result["children"][0]["netmask"], 8)
        self.assertEqual(len(result["children"][0]["children"]), 1)

    def test_get_net_not_in_db_and_empty(self):
        result = get_net("128.0.0.0/8")
        self.assertEqual(result["cidr"], "128.0.0.0/8")
        self.assertEqual(result["network_in_database"], False)
        self.assertEqual(len(result["children"]), 0)



class TestDeleteNetMethods(unittest.TestCase):
    def setUp(self):
        try:
            remove("test.db")
        except FileNotFoundError:
            pass
        config.database_file = "test.db"
        start_database_connection()

        add_net("127.0.0.0/8")
        add_net("127.0.0.0/16")
        add_net("127.0.0.0/24")

    def tearDown(self):
        close_database_connection()
        remove("test.db")

    def test_delete_net_normal(self):
        delete_net("127.0.0.0/8")
        result = get_net("127.0.0.0/16")
        self.assertEqual(result["cidr"] , "127.0.0.0/16")
        self.assertEqual(len(result["children"]), 1)
        self.assertEqual(result["children"][0]["address"], "127.0.0.0")
        self.assertEqual(result["children"][0]["netmask"], 24)

    def test_delete_net_recursive(self):
        delete_net("127.0.0.0/8", recursive=True)
        result = get_net("127.0.0.0/8")
        self.assertFalse(result["network_in_database"])

    def test_delete_net_inner(self):
        delete_net("127.0.0.0/16")
        result = get_net("127.0.0.0/8")
        self.assertEqual(result["cidr"] , "127.0.0.0/8")
        self.assertEqual(len(result["children"]), 1)
        self.assertEqual(result["children"][0]["address"], "127.0.0.0")
        self.assertEqual(result["children"][0]["netmask"], 24)

    def test_delete_net_inner_recursive(self):
        delete_net("127.0.0.0/16", recursive=True)
        result = get_net("127.0.0.0/8")
        self.assertEqual(result["cidr"] , "127.0.0.0/8")
        self.assertEqual(len(result["children"]), 0)

    def test_get_net_host_bits_set(self):
        with self.assertRaises(Fault) as cm:
            delete_net("127.0.0.1/8")
        self.assertEqual(cm.exception.faultString, "InvalidNetworkDescription")

    def test_get_net_not_in_db(self):
        delete_net("10.0.0.0/8")

class TestClaimNetMethods(unittest.TestCase):
    def setUp(self):
        try:
            remove("test.db")
        except FileNotFoundError:
            pass
        config.database_file = "test.db"
        start_database_connection()

        add_net("127.0.0.0/8")

    def tearDown(self):
        close_database_connection()
        remove("test.db")

    #@unittest.skip("")
    def test_claim_normal_empty_subnet(self):
        claimed = claim_net("127.0.0.0/8", 16)
        result = get_net("127.0.0.0/8")
        self.assertEqual(claimed["cidr"], "127.0.0.0/16")
        self.assertEqual(len(result["children"]), 1)
        self.assertEqual(result["children"][0]["cidr"], "127.0.0.0/16")

    #@unittest.skip("")
    def test_claim_normal(self):
        add_net("127.0.0.0/16")
        add_net("127.2.0.0/16")

        claim_net("127.0.0.0/8", 16)
        result = get_net("127.0.0.0/8")
        self.assertEqual(result["cidr"] , "127.0.0.0/8")
        self.assertEqual(len(result["children"]), 3)
        for i in range(3):
            self.assertEqual(result["children"][i]["address"], "127.%d.0.0" % i)

    #@unittest.skip("")
    def test_claim_first_gap(self):
        add_net("127.1.0.0/16")
        add_net("127.2.0.0/16")
        claim_net("127.0.0.0/8", 16)
        result = get_net("127.0.0.0/8")
        self.assertEqual(result["cidr"] , "127.0.0.0/8")
        self.assertEqual(len(result["children"]), 3)
        for i in range(3):
            self.assertEqual(result["children"][i]["address"], "127.%d.0.0" % i)

    #@unittest.skip("")
    def test_claim_last_gap(self):
        add_net("127.0.0.0/16")
        add_net("127.1.0.0/16")
        claim_net("127.0.0.0/8", 16)
        result = get_net("127.0.0.0/8")
        self.assertEqual(result["cidr"] , "127.0.0.0/8")
        self.assertEqual(len(result["children"]), 3)
        for i in range(3):
            self.assertEqual(result["children"][i]["address"], "127.%d.0.0" % i)

    #@unittest.skip("")
    def test_claim_only_last_gap_remaining(self):
        add_net("127.0.0.0/16")
        add_net("127.0.0.0/18")
        add_net("127.0.64.0/18")
        add_net("127.0.128.0/18")
        claim_net("127.0.0.0/16", 18)
        result = get_net("127.0.0.0/16")
        self.assertEqual(result["cidr"] , "127.0.0.0/16")
        self.assertEqual(len(result["children"]), 4)
        for i in range(4):
            self.assertEqual(result["children"][i]["address"], "127.0.%s.0" % str(i*64))

    def test_claim_last_gap_with_offset(self):
        add_net("1.0.0.0/8")
        add_net("1.2.3.0/24")
        result = claim_net("1.0.0.0/8", 9)
        self.assertEqual(result["cidr"], "1.128.0.0/9")

    def test_claim_no_matching_gap(self):
        add_net("127.0.0.0/9")
        add_net("127.128.0.0/9")
        with self.assertRaises(Fault) as cm:
            claim_net("127.0.0.0/8", 16)
        self.assertEqual(cm.exception.faultString, "NoMatchingGapAvailable")

    def test_claim_host_bits_set(self):
        with self.assertRaises(Fault) as cm:
            claim_net("127.0.0.1/8", 16)
        self.assertEqual(cm.exception.faultString, "InvalidNetworkDescription")

    def test_claim_no_matching_gap_at_start(self):
        add_net("1.0.0.0/8")
        add_net("1.2.3.0/24")
        add_net("1.128.0.0/9")
        with self.assertRaises(Fault) as cm:
            claim_net("1.0.0.0/8", 9)
        self.assertEqual(cm.exception.faultString, "NoMatchingGapAvailable")
