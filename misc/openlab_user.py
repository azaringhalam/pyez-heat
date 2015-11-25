'''
Created on Jun 19, 2015

@author: azaringh
'''
from heat.engine import constraints
from heat.engine import properties
from heat.engine import resource

import keystoneclient.v2_0.client
import sys, traceback


class OpenLabUser(resource.Resource):
    """Heat Template Resource for OpenLab Keystone user and role."""

    PROPERTIES = (
        USER, PASSWORD, KEYSTONE_NAME, AUTH_URL, TENANT_NAME, USER_NAME, USER_ROLE,
    ) = (
        'user', 'password', 'keystone_name', 'auth_url', 'tenant_name', 'user_name', 'user_role',
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
            required=True,
            default=None,
            update_allowed=False
        ),
        USER_NAME: properties.Schema(
            properties.Schema.STRING,
            _('Name of user to add to project.'),
            required=True,
            default=None,
            update_allowed=False
        ),
        USER_ROLE: properties.Schema(
            properties.Schema.STRING,
            _('Role of USER_NAME.'),
            required=True,
            default=None,
            update_allowed=False
        )
    }

    def handle_create(self):
        keystone = keystoneclient.v2_0.client.Client(
                                 username = self.properties[self.USER], 
                                 password = self.properties[self.PASSWORD],
                                 project_name = self.properties[self.KEYSTONE_NAME],
                                 auth_url = self.properties[self.AUTH_URL])
        keystone.roles.add_user_role(
                           user = keystone.users.find(name = self.properties[self.USER_NAME]),
                           role = keystone.roles.find(name = self.properties[self.USER_ROLE]),
                           tenant = keystone.tenants.find(name = self.properties[self.TENANT_NAME])
                           )

    def handle_update(self, json_snippet=None, tmpl_diff=None, prop_diff=None): 
        pass

    def handle_delete(self):
        keystone = keystoneclient.v2_0.client.Client(
                                 username = self.properties[self.USER], 
                                 password = self.properties[self.PASSWORD],
                                 project_name = self.properties[self.KEYSTONE_NAME],
                                 auth_url = self.properties[self.AUTH_URL])
        keystone.roles.remove_user_role(
                           user = keystone.users.find(name = self.properties[self.USER_NAME]),
                           role = keystone.roles.find(name = self.properties[self.USER_ROLE]),
                           tenant = keystone.tenants.find(name = self.properties[self.TENANT_NAME])
                           )


def resource_mapping():
    return {
        'OS::OpenLab::User': OpenLabUser
    }