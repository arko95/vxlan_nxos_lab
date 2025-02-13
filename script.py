import json
import os
import ipaddress
from jinja2 import Environment, FileSystemLoader

def generate_ansible_files(input_json_path, template_dir, output_dir):
    # Load the JSON data
    with open(input_json_path, 'r') as json_file:
        data = json.load(json_file)

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)

    # Generate individual device YAML files (host.j2)
    generate_device_files(data, env, output_dir)

    # Generate leafs.yml and spines.yml
    generate_aggregate_files(data, env, output_dir)

    print(f"Generated YAML files in {output_dir}")

def generate_device_files(data, env, output_dir):
    template = env.get_template('host.j2')

    # Collect devices from spines and leafs
    spines_devices = data['bgp']['spines']['devices']['device']
    leafs_devices = data['bgp']['leafs']['devices']['device']
    all_devices = spines_devices + leafs_devices

    # Prepare global data
    interfaces = data.get('interfaces', [])
    l2_service = data.get('l2_service', [])
    bgp = data.get('bgp', {})

    # Generate YAML files for each device
    for device in all_devices:
        device_name = device['name']

        # Initialize var_ref counter for each device
        var_ref_counter = {}
        var_ref_mapping = {}

        # Process vrfs_services and networks_services from l2_service
        vrfs_services = []
        networks_services = []
        for l2_serv in l2_service:
            for l2ser in l2_serv['devices']:
                if l2ser['name'] == device_name:
                    vrf_name = l2ser['vrf']
                    # Update counter for this vrf_name
                    count = var_ref_counter.get(vrf_name, 0)
                    var_ref_counter[vrf_name] = count + 1
                    var_ref_suffix = '' if count == 0 else str(count)
                    var_ref = f"refvrf_ansiblevrf{var_ref_suffix}"
                    # Add to vrfs_services if vrf_name and vlan_id combination not already added
                    if not any(vrf['vrf'] == vrf_name and vrf['vlan_id'] == l2ser['vlan_id'] for vrf in vrfs_services):
                        vrf_entry = {
                            'var_ref': var_ref,
                            'vrf': vrf_name,
                            'vlan_id': l2ser['vlan_id'],
                            'vni_id': l2ser['vni_id']
                        }
                        vrfs_services.append(vrf_entry)
                    # Add to networks_services
                    l2ser['var_ref'] = var_ref
                    # Parse the 'ip' field to get 'ip_network' and 'ip_mask'
                    if 'ip' in l2ser and l2ser['ip']:
                        try:
                            interface = ipaddress.ip_interface(l2ser['ip'])
                            l2ser['ip_network'] = str(interface.ip)
                            l2ser['ip_mask'] = str(interface.netmask)
                        except ValueError as e:
                            print(f"Error parsing IP for device {device_name}: {e}")
                            l2ser['ip_network'] = ''
                            l2ser['ip_mask'] = ''
                    else:
                        l2ser['ip_network'] = ''
                        l2ser['ip_mask'] = ''
                    networks_services.append(l2ser)

        # Prepare the context for template rendering
        context = {
            'device': device_name,
            'interfaces': [iface for iface in interfaces if iface['name'] == device_name],
            'vrfs_services': vrfs_services,
            'networks_services': networks_services,
            'bgp': bgp,
            'device_id': device.get('id', ''),
        }

        # Render the template with the context data
        rendered_content = template.render(**context)

        # Write the rendered content to the YAML file
        output_file_path = os.path.join(output_dir, f"{device_name}.yml")
        with open(output_file_path, 'w') as output_file:
            output_file.write(rendered_content)

def generate_aggregate_files(data, env, output_dir):
    # Generate spines.yml
    generate_spines_file(data, env, output_dir)

    # Generate leafs.yml
    generate_leafs_file(data, env, output_dir)

def generate_spines_file(data, env, output_dir):
    template = env.get_template('spines.j2')

    # Get spines data
    spines_devices = data['bgp']['spines']['devices']['device']
    spines_asn = data['bgp']['spines']['asn']
    spines_neighbors = data['bgp']['spines'].get('neighbors', [])

    # Prepare the context
    context = {
        'devices': spines_devices,
        'asn': spines_asn,
        'neighbors': spines_neighbors,
        'bgp': data['bgp'],
        'interfaces': data.get('interfaces', []),
    }

    # Render the template
    rendered_content = template.render(**context)

    # Write the rendered content to spines.yml
    output_file_path = os.path.join(output_dir, 'spines.yml')
    with open(output_file_path, 'w') as output_file:
        output_file.write(rendered_content)

def generate_leafs_file(data, env, output_dir):
    template = env.get_template('leafs.j2')

    # Get leafs data
    leafs_devices = data['bgp']['leafs']['devices']['device']
    leafs_asn = data['bgp']['leafs']['asn']
    leafs_neighbors = data['bgp']['leafs'].get('neighbors', [])

    # Initialize var_ref mapping
    var_ref_mapping = {}

    # Process vrfs and networks from l3_service
    vrfs = []
    networks = []
    unique_vlans = set()

    for l3_serv in data.get('l3_service', []):
        for dev in l3_serv['devices']:
            vrf_name = dev['vrf']
            vlan_id = dev['vlan_id']
            vni_id = dev['vni_id']

            # Assign var_ref to vrf_name if not already assigned
            if vrf_name not in var_ref_mapping:
                count = len(var_ref_mapping)
                var_ref_suffix = '' if count == 0 else str(count)
                var_ref = f"refvrf_ansiblevrf{var_ref_suffix}"
                var_ref_mapping[vrf_name] = var_ref
            else:
                var_ref = var_ref_mapping[vrf_name]

            # Add to vrfs if vrf_name not already added
            if not any(vrf['vrf'] == vrf_name for vrf in vrfs):
                vrf_entry = {
                    'var_ref': var_ref,
                    'vrf': vrf_name,
                    'vlan_id': vlan_id,
                    'vni_id': vni_id
                }
                vrfs.append(vrf_entry)

            # Add to networks if vlan_id not already added
            if vlan_id not in unique_vlans:
                unique_vlans.add(vlan_id)
                net_entry = {
                    'var_ref': var_ref,
                    'vrf': vrf_name,
                    'vlan_id': vlan_id,
                    'vni_id': vni_id
                }
                networks.append(net_entry)

    # Prepare the context
    context = {
        'devices': leafs_devices,
        'asn': leafs_asn,
        'neighbors': leafs_neighbors,
        'bgp': data['bgp'],
        'interfaces': data.get('interfaces', []),
        'vrfs': vrfs,
        'networks': networks,
    }

    # Render the template
    rendered_content = template.render(**context)

    # Write the rendered content to leafs.yml
    output_file_path = os.path.join(output_dir, 'leafs.yml')
    with open(output_file_path, 'w') as output_file:
        output_file.write(rendered_content)

# Paths configuration
input_json_path = 'input.json'  # Adjust the path if necessary
template_dir = 'ansible_directory/templates_ans'  # Directory containing templates
output_dir = 'ansible_directory/ansible_generated'  # Directory to save generated YAML files

# Generate the Ansible files
generate_ansible_files(input_json_path, template_dir, output_dir)