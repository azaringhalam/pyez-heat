'''
Created on Jul 13, 2015

@author: azaringh
'''

from heat.engine import properties
from heat.engine import resource
from vnc_api import vnc_api


class OpenLabFipPool(resource.Resource):
    """Heat Template Resource for OpenLab floating IP pool."""

    PROPERTIES = (
        USER, PASSWORD, KEYSTONE_NAME, DOMAIN, TENANT_NAME, PUBLIC_NETWORK, API_SERVER, POOL_NAME,
    ) = (
        'user', 'password', 'keystone_name', 'domain', 'tenant_name', 'public_network', 'api_server', 'pool_name',
    )

    properties_schema = {
        USER: properties.Schema(
            properties.Schema.STRING,
            _('user name.'),
            default='admin',
            update_allowed=False,
        ),
        PASSWORD: properties.Schema(
            properties.Schema.STRING,
            _('password.'),
            default='contrail123',
            update_allowed=False,
        ),
        KEYSTONE_NAME: properties.Schema(
            properties.Schema.STRING,
            _('Keystone name.'),
            default='admin',
            update_allowed=False,
        ),
        DOMAIN: properties.Schema(
            properties.Schema.STRING,
            _('domain.'),
            default='default-domain',
            update_allowed=False,
        ),
        TENANT_NAME: properties.Schema(
            properties.Schema.STRING,
            _('Name of keystone tenant/project.'),
            required=True,
            default=None,
            update_allowed=False
        ),
        PUBLIC_NETWORK: properties.Schema(
            properties.Schema.STRING,
            _('Name of public network for floating IP pool.'),
            required=True,
            default=None,
            update_allowed=False
        ),
        API_SERVER: properties.Schema(
            properties.Schema.STRING,
            _('API server host IP.'),
            required=True,
            default=None,
            update_allowed=False
        ),
        POOL_NAME: properties.Schema(
            properties.Schema.STRING,
            _('Floating IP pool name.'),
            required=True,
            default=None,
            update_allowed=False
        ),
    }

    def handle_create(self):
        vnc = vnc_api.VncApi(username = self.properties[self.USER], password = self.properties[self.PASSWORD], 
                             tenant_name = self.properties[self.KEYSTONE_NAME], api_server_host = self.properties[self.API_SERVER])
        tenant = vnc.project_read(fq_name = [self.properties[self.DOMAIN], self.properties[self.TENANT_NAME]])
        vn_public = vnc.virtual_network_read(fq_name = [self.properties[self.DOMAIN], self.properties[self.TENANT_NAME], 
                                                        self.properties[self.PUBLIC_NETWORK]])
        pool = vnc_api.FloatingIpPool(name = self.properties[self.POOL_NAME], parent_obj = vn_public)

        vnc.floating_ip_pool_create(pool)
        tenant.add_floating_ip_pool(pool)
        vnc.project_update(tenant)
        
    def handle_update(self, json_snippet=None, tmpl_diff=None, prop_diff=None): 
        pass

    def handle_delete(self):
        vnc = vnc_api.VncApi(username = self.properties[self.USER], password = self.properties[self.PASSWORD], 
                             tenant_name = self.properties[self.KEYSTONE_NAME], api_server_host = self.properties[self.API_SERVER])
        tenant = vnc.project_read(fq_name = [self.properties[self.DOMAIN], self.properties[self.TENANT_NAME]])
        vn_public = vnc.virtual_network_read(fq_name = [self.properties[self.DOMAIN], self.properties[self.TENANT_NAME], 
                                                        self.properties[self.PUBLIC_NETWORK]])
        pool = vnc_api.FloatingIpPool(name = self.properties[self.POOL_NAME], parent_obj = vn_public)
        tenant.del_floating_ip_pool(pool)
        vnc.floating_ip_pool_delete(pool.uuid)
        vnc.project_update(tenant)

def resource_mapping():
    return {
        'OS::OpenLab::FipPool': OpenLabFipPool
    }