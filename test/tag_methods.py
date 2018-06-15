import unittest

from os import remove
from xmlrpc.server import Fault
from minipam.server import *

class TestAddGetTagMethods(unittest.TestCase):
    def setUp(self):
        try:
            remove("test.db")
        except FileNotFoundError:
            pass
        config.database_file = "test.db"
        start_database_connection()
        add_net("127.0.0.0/8")
        add_net("127.0.0.0/16")

    def tearDown(self):
        close_database_connection()
        remove("test.db")

    def test_add_tag_normal(self):
        add_tag("127.0.0.0/8", "name", "localhost")
        add_tag("127.0.0.0/8", "type", "server")
        self.assertEqual(get_tag("127.0.0.0/8", "name"), "localhost")
        self.assertEqual(get_tag("127.0.0.0/8", "type"), "server")

    def test_add_tag_duplicate(self):
        add_tag("127.0.0.0/8", "name", "localhost")
        with self.assertRaises(Fault) as cm:
            add_tag("127.0.0.0/8", "name", "localhost2")
        self.assertEqual(cm.exception.faultString, "TagExists")

    def test_add_tag_host_bits_set(self):
        with self.assertRaises(Fault) as cm:
            add_tag("127.0.0.1/8","name","localhost")
        self.assertEqual(cm.exception.faultString, "InvalidNetworkDescription")

class TestGetTagsMethods(unittest.TestCase):
    def setUp(self):
        try:
            remove("test.db")
        except FileNotFoundError:
            pass
        config.database_file = "test.db"
        start_database_connection()
        add_net("127.0.0.0/8")
        add_net("127.0.0.0/16")

    def tearDown(self):
        close_database_connection()
        remove("test.db")

    def test_get_tags_normal(self):
        add_tag("127.0.0.0/8", "name", "localhost")
        add_tag("127.0.0.0/8", "type", "server")
        add_tag("127.0.0.0/16", "type", "server")
        result = get_tags("127.0.0.0/8")
        self.assertEqual(result, {"name" : "localhost", "type" : "server"})

    def test_get_tags_empty(self):
        add_tag("127.0.0.0/8", "name", "localhost")
        add_tag("127.0.0.0/8", "type", "server")
        result = get_tags("127.0.0.0/16")
        self.assertEqual(result, {})

    def test_add_tag_host_bits_set(self):
        with self.assertRaises(Fault) as cm:
            get_tags("127.0.0.1/8")
        self.assertEqual(cm.exception.faultString, "InvalidNetworkDescription")

class TestDeleteTagsMethods(unittest.TestCase):
    def setUp(self):
        try:
            remove("test.db")
        except FileNotFoundError:
            pass
        config.database_file = "test.db"
        start_database_connection()
        add_net("127.0.0.0/8")
        add_net("127.0.0.0/16")

    def tearDown(self):
        close_database_connection()
        remove("test.db")

    def test_delete_tag_normal(self):
        add_tag("127.0.0.0/8", "name", "localhost")
        add_tag("127.0.0.0/8", "type", "server")
        result = get_tags("127.0.0.0/8")
        self.assertEqual(result, {"name" : "localhost", "type" : "server"})
        delete_tag("127.0.0.0/8","name")
        result = get_tags("127.0.0.0/8")
        self.assertEqual(result, {"type" : "server"})
        delete_tag("127.0.0.0/8","type")
        result = get_tags("127.0.0.0/8")
        self.assertEqual(result, {})

    def test_delete_tag_non_existing(self):
        add_tag("127.0.0.0/8", "name", "localhost")
        add_tag("127.0.0.0/8", "type", "server")
        delete_tag("127.0.0.0/8","vlan")
        result = get_tags("127.0.0.0/8")
        self.assertEqual(result, {"name" : "localhost", "type" : "server"})
        delete_tag("127.0.0.0/8","name")

    def test_delete_tag_host_bits_set(self):
        add_tag("127.0.0.0/8", "name", "localhost")
        with self.assertRaises(Fault) as cm:
            delete_tag("127.0.0.1/8","name")
        self.assertEqual(cm.exception.faultString, "InvalidNetworkDescription")

class TestModifyTagsMethods(unittest.TestCase):
    def setUp(self):
        try:
            remove("test.db")
        except FileNotFoundError:
            pass
        config.database_file = "test.db"
        start_database_connection()
        add_net("127.0.0.0/8")
        add_net("127.0.0.0/16")

    def tearDown(self):
        close_database_connection()
        remove("test.db")

    def test_modify_normal(self):
        add_tag("127.0.0.0/8", "name", "localhost")
        modify_tag("127.0.0.0/8", "name", "localhost2")
        result = get_tags("127.0.0.0/8")
        self.assertEqual(result, {"name" : "localhost2"})

    def test_modify_non_existing(self):
        with self.assertRaises(Fault) as cm:
            modify_tag("127.0.0.0/8", "name", "localhost")
        self.assertEqual(cm.exception.faultString, "TagDoesNotExist")
        result = get_tags("127.0.0.0/8")
        self.assertEqual(result, {})

    def test_modify_tag_host_bits_set(self):
        add_tag("127.0.0.0/8", "name", "localhost")
        with self.assertRaises(Fault) as cm:
            modify_tag("127.0.0.1/8","name", "localhost2")
        self.assertEqual(cm.exception.faultString, "InvalidNetworkDescription")
