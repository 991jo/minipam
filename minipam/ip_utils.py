def network_address_to_int(net):
    return int.from_bytes(net.network_address.packed, byteorder='big')

def network_broadcast_to_int(net):
    return int.from_bytes(net.broadcast_address.packed, byteorder='big')
