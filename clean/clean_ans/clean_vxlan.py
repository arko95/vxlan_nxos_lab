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

        for device in self.devices:
            #if not device.name == 'LEAF-3':
            with steps.start(
                "Cleaning on '{d}'".format(d=device.name)):
                bgp_info = device.configure('''
                    no interface nve1
                    no vlan 3
                    no vlan 4
                    no vlan 5
                    no vlan 6
                    no vlan 2000
                    no vlan 14
                    no vlan 10
                    no vlan 20
                    no vlan 500                        
                    no interface vlan 3
                    no interface vlan 10
                    no interface vlan 20
                    no interface vlan 4
                    no interface vlan 5
                    no interface vlan 6
                    no interface vlan 2000
                    no interface vlan 500
                    no router bgp 65000
                    no evpn
                    no vrf context MYVRF           
                    ''')

if __name__ == '__main__':
    aetest.main()
