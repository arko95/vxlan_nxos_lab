#!/usr/bin/env python3
import sys
import json
import re
import ipaddress

def is_valid_ipv4(ip_str: str) -> bool:
    try:
        ipaddress.IPv4Address(ip_str)
        return True
    except Exception:
        return False

def is_valid_ipv4_with_optional_mask(ip_str: str) -> bool:
    if '/' in ip_str:
        try:
            ip_part, mask_str = ip_str.split('/')
            if not is_valid_ipv4(ip_part):
                return False
            mask = int(mask_str)
            return 0 <= mask <= 32
        except Exception:
            return False
    return is_valid_ipv4(ip_str)

def is_valid_multicast_ipv4(ip_str: str) -> bool:
    ip = ip_str.split('/')[0]
    try:
        addr = ipaddress.IPv4Address(ip)
        return 224 <= int(addr.packed[0]) <= 239
    except Exception:
        return False

def is_alphanumeric(s: str) -> bool:
    return bool(re.fullmatch(r'[A-Za-z0-9_]+', s))

def is_valid_ifn(s: str) -> bool:
    return bool(re.fullmatch(r'[A-Za-z0-9/]+', s))

def is_valid_int_in_range(value, min_val: int, max_val: int) -> bool:
    try:
        num = int(value)
        return min_val <= num <= max_val
    except Exception:
        return False

def is_positive_int(value) -> bool:
    try:
        return int(value) > 0
    except Exception:
        return False

def is_valid_mac(mac: str) -> bool:
    """
    Validate MAC address in dotted notation (e.g., "aaaa.aaaa.aaaa").
    """
    return bool(re.fullmatch(r'[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}\.[0-9A-Fa-f]{4}', mac))

def validate_device_common(device: dict, context: str) -> list:
    errors = []
    if 'name' in device and not is_alphanumeric(device['name']):
        errors.append(f"{context} name '{device['name']}' is not alphanumeric.")
    # Validate vlan_id as an integer in the range 0 to 4200.
    if 'vlan_id' in device and not is_valid_int_in_range(device['vlan_id'], 0, 4200):
        errors.append(f"{context} vlan_id '{device['vlan_id']}' is not an integer in the range 0 to 4200.")
    if 'vni_id' in device and not is_positive_int(device['vni_id']):
        errors.append(f"{context} vni_id '{device['vni_id']}' is not a positive integer.")
    if 'nve_id' in device and not is_valid_int_in_range(device['nve_id'], 0, 65500):
        errors.append(f"{context} nve_id '{device['nve_id']}' is not in the range 0 to 65500.")
    if 'vrf' in device and not is_alphanumeric(device['vrf']):
        errors.append(f"{context} vrf '{device['vrf']}' is not alphanumeric.")
    return errors

def validate_device_l2(device: dict, context: str) -> list:
    errors = validate_device_common(device, context)
    if 'ip' in device and not is_valid_ipv4_with_optional_mask(device['ip']):
        errors.append(f"{context} ip '{device['ip']}' is not a valid IPv4 address with optional mask.")
    if 'nve_mgroup' in device and not is_valid_multicast_ipv4(device['nve_mgroup']):
        errors.append(f"{context} nve_mgroup '{device['nve_mgroup']}' is not a valid multicast IPv4 address.")
    if 'gp_mcast_group' in device and not is_valid_multicast_ipv4(device['gp_mcast_group']):
        errors.append(f"{context} gp_mcast_group '{device['gp_mcast_group']}' is not a valid multicast IPv4 address.")
    if 'ip_anycast_address' in device and not is_valid_ipv4(device['ip_anycast_address']):
        errors.append(f"{context} ip_anycast_address '{device['ip_anycast_address']}' is not a valid IPv4 address.")
    if 'gp_mcast_mac' in device and not is_valid_mac(device['gp_mcast_mac']):
        errors.append(f"{context} gp_mcast_mac '{device['gp_mcast_mac']}' is not a valid MAC address.")
    return errors

def validate_bgp(bgp: dict) -> list:
    errors = []
    # Validate spines
    if 'spines' in bgp:
        spines = bgp['spines']
        if 'asn' in spines and not is_valid_int_in_range(spines['asn'], 0, 65500):
            errors.append(f"bgp.spines.asn '{spines['asn']}' is not in the range 0 to 65500.")
        if 'devices' in spines and 'device' in spines['devices']:
            for dev in spines['devices']['device']:
                if 'name' in dev and not is_alphanumeric(dev['name']):
                    errors.append(f"bgp.spines device name '{dev['name']}' is not alphanumeric.")
                if 'dev' in dev and not is_alphanumeric(dev['dev']):
                    errors.append(f"bgp.spines device dev '{dev['dev']}' is not alphanumeric.")
                if 'id' in dev and not is_valid_ipv4(dev['id']):
                    errors.append(f"bgp.spines device id '{dev['id']}' is not a valid IPv4 address.")
        if 'neighbors' in spines:
            for neighbor in spines['neighbors']:
                if not is_valid_ipv4(neighbor):
                    errors.append(f"bgp.spines neighbor '{neighbor}' is not a valid IPv4 address.")
    # Validate leafs
    if 'leafs' in bgp:
        leafs = bgp['leafs']
        if 'asn' in leafs and not is_valid_int_in_range(leafs['asn'], 0, 65500):
            errors.append(f"bgp.leafs.asn '{leafs['asn']}' is not in the range 0 to 65500.")
        if 'devices' in leafs and 'device' in leafs['devices']:
            for dev in leafs['devices']['device']:
                if 'name' in dev and not is_alphanumeric(dev['name']):
                    errors.append(f"bgp.leafs device name '{dev['name']}' is not alphanumeric.")
                if 'dev' in dev and not is_alphanumeric(dev['dev']):
                    errors.append(f"bgp.leafs device dev '{dev['dev']}' is not alphanumeric.")
                if 'id' in dev and not is_valid_ipv4(dev['id']):
                    errors.append(f"bgp.leafs device id '{dev['id']}' is not a valid IPv4 address.")
        if 'neighbors' in leafs:
            for neighbor in leafs['neighbors']:
                if not is_valid_ipv4(neighbor):
                    errors.append(f"bgp.leafs neighbor '{neighbor}' is not a valid IPv4 address.")
    return errors

def validate_interfaces(interfaces: list) -> list:
    errors = []
    for group in interfaces:
        if 'name' in group and not is_alphanumeric(group['name']):
            errors.append(f"Interface group name '{group['name']}' is not alphanumeric.")
        if 'interface' in group:
            for intf in group['interface']:
                if 'ifn' in intf and not is_valid_ifn(intf['ifn']):
                    errors.append(f"Interface ifn '{intf['ifn']}' is not valid (should be alphanumeric and may include '/').")
                # For interfaces, vlan_id must be an integer in the range 0 to 4200.
                if 'vlan_id' in intf and not is_valid_int_in_range(intf['vlan_id'], 0, 4200):
                    errors.append(f"Interface vlan_id '{intf['vlan_id']}' is not an integer in the range 0 to 4200.")
    return errors

def validate_json(data: dict) -> list:
    errors = []
    if 'name' in data and not is_alphanumeric(data['name']):
        errors.append(f"Lab name '{data['name']}' is not alphanumeric.")

    if 'l2_service' in data:
        for service in data['l2_service']:
            if 'name' in service and not is_alphanumeric(service['name']):
                errors.append(f"l2_service name '{service['name']}' is not alphanumeric.")
            if 'devices' in service:
                for device in service['devices']:
                    errors.extend(validate_device_l2(device, "l2_service device"))
    
    if 'l3_service' in data:
        for service in data['l3_service']:
            if 'name' in service and not is_alphanumeric(service['name']):
                errors.append(f"l3_service name '{service['name']}' is not alphanumeric.")
            if 'devices' in service:
                for device in service['devices']:
                    errors.extend(validate_device_common(device, "l3_service device"))
    
    if 'bgp' in data:
        errors.extend(validate_bgp(data['bgp']))
    
    if 'interfaces' in data:
        errors.extend(validate_interfaces(data['interfaces']))
    
    return errors

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <json_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print("Error reading JSON file:", e)
        sys.exit(1)
    
    validation_errors = validate_json(data)
    if validation_errors:
        print("Validation Errors found:")
        for err in validation_errors:
            print(" -", err)
        sys.exit(1)
    else:
        print("JSON file is valid!")
        sys.exit(0)

if __name__ == '__main__':
    main()