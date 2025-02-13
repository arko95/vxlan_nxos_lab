import os
import json
from utils import (
    load_json_data,
    setup_jinja2_environment,
    render_template,
    write_output_file
)

def generate_device_templates(data, env, output_dir):
    bgp_data = data.get('bgp', {})
    spines = bgp_data.get('spines', {})
    leafs = bgp_data.get('leafs', {})

    context = {
        'bgp_spines_asn': spines.get('asn', ''),
        'bgp_leafs_asn': leafs.get('asn', ''),
        'spine_neighbors': spines.get('neighbors', []),
        'leaf_neighbors': leafs.get('neighbors', [])
    }

    content = render_template(env, 'device_template.j2', context)
    write_output_file(output_dir, 'device_templates.nac.yaml', content)

def generate_interface_templates(data, env, output_dir):
    interfaces_data = data.get('interfaces', [])

    devices = []
    for device in interfaces_data:
        device_name = device.get('name', '')  # Changed 'device' to 'name'
        interfaces_list = []
        for iface in device.get('interface', []):
            # Map 'vlan_id' to 'access_vlan'
            access_vlan = iface.get('vlan_id', '')  # Changed 'VLAN_ID' to 'vlan_id'
            # Set 'native_vlan' to 1 as per your example
            native_vlan = 1
            interface_id = iface.get('ifn', '')  # Changed 'id' to 'ifn'

            interface_info = {
                'id': interface_id,
                'access_vlan': access_vlan,
                'native_vlan': native_vlan
            }
            interfaces_list.append(interface_info)

        device_info = {
            'name': device_name,
            'configuration': {
                'interfaces': {
                    'ethernets': interfaces_list
                }
            }
        }
        devices.append(device_info)

    context = {'devices': devices}
    content = render_template(env, 'interface_template.j2', context)
    write_output_file(output_dir, 'interface_templates.nac.yaml', content)

def generate_l2_service_files(data, env, output_dir):
    l2_services = data.get('l2_service', [])
    for service in l2_services:
        name = service.get('name', '')
        devices = service.get('devices', [])

        # Assuming all devices in the service have the same vlan_id, vni_id, etc.
        # Extracting from the first device
        if devices:
            device_info = devices[0]
            vlan_id = device_info.get('vlan_id', '')
            vni_id = device_info.get('vni_id', '')
            ip_vlan_ser = device_info.get('ip', '')
            name_vrf = device_info.get('vrf', '')
            multicast_group = device_info.get('nve_mgroup', '')
        else:
            vlan_id = ''
            vni_id = ''
            ip_vlan_ser = ''
            name_vrf = ''
            multicast_group = ''

        # Prepare device names list
        device_names = [device.get('name', '') for device in devices]

        # Service name and filename
        identifier = vni_id if vni_id else name
        service_name = f"SERVICE_vni{identifier}"
        filename = f"service_l2_vni{identifier}.nac.yaml"

        variables = {
            'name': name if name else f"vni{identifier}",
            'vlan_id': vlan_id,
            'ip_vlan_ser': ip_vlan_ser,
            'vni_id': vni_id,
            'name_vrf': name_vrf,
            'multicast_group': multicast_group
        }

        context = {
            'service_name': service_name,
            'device_names': device_names,
            'variables': variables
        }
        content = render_template(env, 'service_l2_template.j2', context)
        write_output_file(output_dir, filename, content)

def generate_l3_service_files(data, env, output_dir):
    l3_services = data.get('l3_service', [])
    for service in l3_services:
        name = service.get('name', '')
        devices = service.get('devices', [])

        # Group devices by vni_id
        vni_groups = {}
        for device in devices:
            vni_id = device.get('vni_id', '')
            if vni_id not in vni_groups:
                vni_groups[vni_id] = []
            vni_groups[vni_id].append(device)

        for vni_id, device_group in vni_groups.items():
            device_info = device_group[0]
            l3_vlan_id = device_info.get('vlan_id', '')
            name_vrf = device_info.get('vrf', '')
            device_names = [device.get('name', '') for device in device_group]

            identifier = vni_id if vni_id else name
            service_name = f"SERVICE_vni{identifier}"
            filename = f"service_l3_vni{identifier}.nac.yaml"

            variables = {
                'name': name if name else f"vni{identifier}",
                'l3_vlan_id': l3_vlan_id,
                'l2_vlan_id': l3_vlan_id,
                'vni_id': vni_id,
                'name_vrf': name_vrf
            }

            context = {
                'service_name': service_name,
                'device_names': device_names,
                'variables': variables
            }
            content = render_template(env, 'service_l3_template.j2', context)
            write_output_file(output_dir, filename, content)

def main():
    input_json_path = 'input.json'
    template_dir = 'terraform_directory/templates_tf'
    output_dir = 'terraform_directory/terraform_generated'

    data = load_json_data(input_json_path)
    env = setup_jinja2_environment(template_dir)

    generate_device_templates(data, env, output_dir)
    generate_interface_templates(data, env, output_dir)
    generate_l2_service_files(data, env, output_dir)
    generate_l3_service_files(data, env, output_dir)

if __name__ == '__main__':
    main()