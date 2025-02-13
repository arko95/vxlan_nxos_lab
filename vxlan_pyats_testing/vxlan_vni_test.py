#!/usr/bin/env python
from ats.log.utils import banner
from genie.conf import Genie
from pyats import aetest
import logging
import os
import json


# Get your logger for your script
log = logging.getLogger(__name__)

################################################################
###                   COMMON SETUP SECTION                   ###
################################################################

class device_setup(aetest.CommonSetup):
    """ Common Setup section """

    # Connect to each device in the testbed
    @aetest.subsection
    def connect(self, testbed, steps):
        genie_testbed = Genie.init(testbed)
        devices = []
        for device in genie_testbed.devices.values():
            with steps.start("Connecting to device '{d}'".format(d=device.name)):
                log.info(banner(
                    "Connecting to device '{d}'".format(d=device.name)))
                try:
                    device.connect()
                except Exception as e:
                    self.failed("Failed to establish connection to '{}'".format(device.name)
                    )

                devices.append(device)
                self.devices = devices

    @aetest.subsection
    def gather_vxlan_vnis(self,steps):
        file_name = os.environ.get('VNIS_IPS')  # Get filename from environment variable
        with open(file_name, 'r') as f:
            data = json.load(f)

        bgp_evpns = {}
        for device in self.devices:
            with steps.start(
                "Gathering interface details on '{d}'".format(d=device.name)):
                bgp_info = device.parse("show bgp l2vpn evpn")
                bgp_evpns.setdefault(device.name, bgp_info)
        self.parent.parameters.update(bgp_evpns=bgp_evpns)
        import pprint
        pprint.pprint(self.parent.parameters['bgp_evpns'])
        self.parent.parameters.update(vnis_ips=data)


################################################################
###                    TESTCASES SECTION                     ###
################################################################


class workstations_find(aetest.Testcase):
    """ This is user Testcases section """
    @aetest.test
    def check_vnis(self, steps):
        """ Checking for VNIs """
        for tech_layer, networks in self.parent.parameters['vnis_ips'].items():
            if tech_layer == 'l2':
                layer = 'l2'
            elif tech_layer == 'l3':
                layer = 'l3'
            for device, bgp_evpn in self.parent.parameters['bgp_evpns'].items():
                if device in self.parent.parameters['vnis_ips'][layer]:
                    
                    for vni, ips in self.parent.parameters['vnis_ips'][layer][device].items():
                        with steps.start(
                                f"Device {device}: vni {vni} analising", continue_=True
                            ) as vnis_step:
                            for edge, edge_info in bgp_evpn['instance']['default']['vrf']['default']['address_family']['l2vpn evpn']['rd'].items():

                                flag = False        
                                if 'rd_vrf' in edge_info:
                                    if edge_info['rd_vrf'] == vni:
                                        flag = True
                                        for ip in ips:
                                            for prefix,info_prefix in edge_info['prefix'].items(): 
                                                if ip in prefix: 
                                                    vnis_step.passed(
                                                        f"The ip {ip} is in the vni {vni} on the {device}"
                                                        )
                                            else:
                                                vnis_step.failed(f"This ip {ip} is not on the vni {vni} on the device {device}")
                            else:
                                if flag == False:
                                    vnis_step.failed(f"The vni {vni} is not on the device {device}")

if __name__ == '__main__':
    aetest.main()
