# minipam
An IPAM software that tries to work and suck less than everything else that exists.

# Design Goals

- no dependencies besides python3 standard library and sqlite3 (version >= 3.6.19 for foreign key support which should come with the standard library)
- just a simple sqlite3 database
- keep things simple and minimal
- currently only IPv4 support because for my use case (LAN Party setups) there
  is no huge benefit in IPv6 because there is no lack of addresses nor do many
  games support it anyways.
- seperation between backend and frontend.
- communication with xmlrpc to be directly scriptable.
- no seperation between networks and IPs (IPs are /32 networks)
- no special fixed data fields like hostnames, vlans, customer ids and the like
- instead it is possibly to tag networks with key-value pairs

# Current status

Work in progress. Backend is working. Some issues exist (see the Github issue page).

# Tests

To execute the test run `run_tests.py`. You do not have to fear for your database.
The tests use a temporary database named `test.db`.
As long as you do not name your database `test.db` you are fine.
