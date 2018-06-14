# minipam
An IPAM software that tries to work and suck less than everything else that exists.

# Design Goals

- no dependencies besides python3 standard library.
- just a simple sqlite3 database
- keep things simple and minimal
- currently only IPv4 support because for my use case (LAN Party setups) there
  is no huge benefit in IPv6 because there is no lack of addresses nor do many
  games support it anyways.
- seperation between backend and frontend.
- communication with xmlrpc to be directly scriptable.
- no seperation between networks and IPs (IPs are /32 networks)
- be flexible by adding tags (key-value-pairs) to networks.

# current status

Work in progress, no functioning backend right now.
