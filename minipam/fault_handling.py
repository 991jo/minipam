from xmlrpc.server import Fault

fault_strings = { 1000: "InvalidFaultCode",
        1001: "InvalidNetworkDescription",
        1002: "NoMatchingGapAvailable",
        1003: "NetworkNotInDatabase",
        1004: "TagExists",
        1005: "TagDoesNotExist"}

#inverse mapping of the fault strings
fault_codes = {v : k for k,v in fault_strings.items()}


def raise_fault(fault):
    if isinstance(fault,int):
        if fault in fault_strings:
            raise Fault(fault, fault_strings[fault])
    else:
        if fault in fault_codes:
            raise Fault(fault_codes[fault], fault)
    raise Fault(1000, fault_strings[1000] + ":%d" % fault)
