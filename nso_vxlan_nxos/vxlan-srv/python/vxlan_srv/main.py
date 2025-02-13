# -*- mode: python; python-indent: 4 -*-
import ncs
from ncs.application import Service


# ------------------------
# SERVICE CALLBACK EXAMPLE
# ------------------------
class ServiceCallbacks(Service):

    # The create() callback is invoked inside NCS FASTMAP and
    # must always exist.
    @Service.create
    def cb_create(self, tctx, root, service, proplist):
        self.log.info('Service create(service=', service._path, ')')

        #BGP CONFIG SPINES AND LEAFS
        spines_devices = service.bgp.spines.devices
        for spine in spines_devices.device:
            bgp_vars = ncs.template.Variables()
            bgp_vars.add('HOSTNAME', spine.dev)
            bgp_vars.add('ASN', service.bgp.spines.asn)
            #bgp_vars.add('ROUTER_ID', spine.id)
            for neighbor in service.bgp.spines.neighbors:
                bgp_vars.add('NEIGHBOR_SPINE', neighbor)
                template = ncs.template.Template(service)
                template.apply('vxlan-srv-spine-bgp-template', bgp_vars)

        leafs_devices = service.bgp.leafs.devices
        for leaf in leafs_devices.device:
            bgp_vars_leaf = ncs.template.Variables()
            bgp_vars_leaf.add('HOSTNAME', leaf.dev)
            bgp_vars_leaf.add('ASN', service.bgp.leafs.asn)
            #bgp_vars_leaf.add('ROUTER_ID', leaf.id)
            for neighbor in service.bgp.leafs.neighbors:
                bgp_vars_leaf.add('NEIGHBOR_LEAF', neighbor)
                template = ncs.template.Template(service)
                template.apply('vxlan-srv-leaf-bgp-template', bgp_vars_leaf)
            
    #Services Config L2 services
        l2_servs = service.l2_service
        for l2_serv in l2_servs:

            #l2_serv_vars.add('NAME', l2_serv.name)
            for device in l2_serv.devices:
                l2_serv_vars = ncs.template.Variables()
                l2_serv_vars.add('HOSTNAME', device.name)
                l2_serv_vars.add('VLAN_ID_L2', device.vlan_id)
                l2_serv_vars.add('VNI_L2', device.vni_id)
                l2_serv_vars.add('GP_MCAST_MAC', device.gp_mcast_mac)
                l2_serv_vars.add('NVE_MGROUP_L2', device.nve_mgroup)
                l2_serv_vars.add('GP_MULTICAST', device.gp_mcast_group)
                l2_serv_vars.add('IP_ANYCAST_ADDRESS', device.ip_anycast_address)                
                l2_serv_vars.add('NVE_ID_L2', device.nve_id)
                l2_serv_vars.add('VRF_NAME_L2', device.vrf)
                l2_serv_vars.add('VLAN_NETWORK_ADDRESS_L2', device.ip)
                template = ncs.template.Template(service)
                template.apply('vxlan-srv-l2-services-template', l2_serv_vars)
    #Services Config L3 services
        l3_servs = service.l3_service
        for l3_serv in l3_servs:
            #l3_serv_vars.add('NAME', l3_serv.name)
            for device in l3_serv.devices:
                l3_serv_vars = ncs.template.Variables()
                l3_serv_vars.add('HOSTNAME', device.name)
                l3_serv_vars.add('VLAN_ID_L3', device.vlan_id)
                l3_serv_vars.add('VNI_L3', device.vni_id)
                l3_serv_vars.add('NVE_ID_L3', device.nve_id)
                l3_serv_vars.add('VRF_NAME_L3', device.vrf)
                template = ncs.template.Template(service)
                template.apply('vxlan-srv-l3-services-template', l3_serv_vars)

    #Services Config interface services
        if_servs = service.interfaces
        for if_dev in if_servs:                   
            for ifn in if_dev.interface:
                if_dev_vars = ncs.template.Variables()
                if_dev_vars.add('HOSTNAME', if_dev.name)
                if_dev_vars.add('IF_NAME', ifn.ifn)
                if_dev_vars.add('IF_VLAN_ID', ifn.vlan_id)
                template = ncs.template.Template(service)
                template.apply('vxlan-srv-if-services-template', if_dev_vars)
  

    # The pre_modification() and post_modification() callbacks are optional,
    # and are invoked outside FASTMAP. pre_modification() is invoked before
    # create, update, or delete of the service, as indicated by the enum
    # ncs_service_operation op parameter. Conversely
    # post_modification() is invoked after create, update, or delete
    # of the service. These functions can be useful e.g. for
    # allocations that should be stored and existing also when the
    # service instance is removed.

    # @Service.pre_modification
    # def cb_pre_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service premod(service=', kp, ')')

    # @Service.post_modification
    # def cb_post_modification(self, tctx, op, kp, root, proplist):
    #     self.log.info('Service postmod(service=', kp, ')')


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class Main(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('Main RUNNING')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        self.register_service('vxlan-srv-servicepoint', ServiceCallbacks)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('Main FINISHED')
