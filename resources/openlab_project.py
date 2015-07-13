'''
Created on May 29, 2015

@author: azaringh
'''
from heat.engine import constraints
from heat.engine import properties
from heat.engine import resource

import keystoneclient.v2_0.client
import sys, traceback


class OpenLabProject(resource.Resource):
    """Heat Template Resource for OpenLab Keystone Project."""

    PROPERTIES = (
        USER, PASSWORD, KEYSTONE_NAME, AUTH_URL, TENANT_NAME, DOMAIN, DESCRIPTION, ENABLED
    ) = (
        'user', 'password', 'keystone_name', 'auth_url', 'tenant_name', 'domain', 'description', 'enabled'
    )

    properties_schema = {
        USER: properties.Schema(
            properties.Schema.STRING,
            _('Keystone user name.'),
            default='admin',
            update_allowed=False,
        ),
        PASSWORD: properties.Schema(
            properties.Schema.STRING,
            _('Keystone password.'),
            default='contrail123',
            update_allowed=False,
        ),
        KEYSTONE_NAME: properties.Schema(
            properties.Schema.STRING,
            _('Keystone name.'),
            default='admin',
            update_allowed=False,
        ),
        AUTH_URL: properties.Schema(
            properties.Schema.STRING,
            _('Keystone autorization url.'),
            required=True,
            default=None,
            update_allowed=False,
        ),
        TENANT_NAME: properties.Schema(
            properties.Schema.STRING,
            _('Name of keystone tenant/project.'),
            update_allowed=True
        ),
        DOMAIN: properties.Schema(
            properties.Schema.STRING,
            _('Name or id of keystone domain.'),
            default='default',
            update_allowed=True,
        ),
        DESCRIPTION: properties.Schema(
            properties.Schema.STRING,
            _('Description of keystone project.'),
            default='',
            update_allowed=True
        ),
        ENABLED: properties.Schema(
            properties.Schema.INTEGER,
            _('This project is enabled or disabled.'),
            default=1,
            update_allowed=True
        )
    }

    def handle_create(self):
        keystone = keystoneclient.v2_0.client.Client(
                                 username = self.properties[self.USER], 
                                 password = self.properties[self.PASSWORD],
                                 project_name = self.properties[self.KEYSTONE_NAME],
                                 auth_url = self.properties[self.AUTH_URL])
        keystone.tenants.create(tenant_name = self.properties[self.TENANT_NAME], description = self.properties[self.DESCRIPTION], enabled = self.properties[self.ENABLED])

    def handle_update(self, json_snippet=None, tmpl_diff=None, prop_diff=None): 
        pass

    def handle_delete(self):
        keystone = keystoneclient.v2_0.client.Client(
                                 username = self.properties[self.USER], 
                                 password = self.properties[self.PASSWORD],
                                 project_name = self.properties[self.KEYSTONE_NAME],
                                 auth_url = self.properties[self.AUTH_URL])
        keystone.tenants.delete(tenant = keystone.tenants.find(name = self.properties[self.TENANT_NAME]))


def resource_mapping():
    return {
        'OS::OpenLab::Project': OpenLabProject
    }
