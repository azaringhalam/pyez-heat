
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import string


from heat.db import api as db_api
from heat.engine import properties
from heat.engine import resource
from jnpr.junos import Device
from pprint import pprint


class GetFacts(resource.Resource):
    '''
    JUNOS PyEZ resource for retrieving device facts

    This resource is useful for installation and configuration of JUNOS devices
    '''
    PROPERTIES = (
        TARGET, USER, PASSWORD,
    ) = (
        'target', 'user', 'password',
    )

    properties_schema = {
        TARGET: properties.Schema(
            properties.Schema.STRING,
            _('JUNOS device host name or IP address.'),
            required=True,
            default=None,
            update_allowed=False,
        ),
        USER: properties.Schema(
            properties.Schema.STRING,
            _('User name.'),
            required=True,
            default=None,
            update_allowed=False,
        ),
        PASSWORD: properties.Schema(
            properties.Schema.STRING,
            _('Password.'),
            required=True,
            default=None,
            update_allowed=False,
        ),
    }

    attributes_schema = {
        'hostname': _("target name."),
        'model': _("target model."),
        'serialnumber': _("serial number."),
    }

    def handle_create(self):
        dev = Device(host="10.10.11.27", user="admin", password="op3nl@b")  
        dev.open()  
        db_api.resource_data_set(self, 'hostname', dev.facts['hostname'], redact=True)
        db_api.resource_data_set(self, 'model', dev.facts['model'], redact=True)
        db_api.resource_data_set(self, 'serialnumber', dev.facts['serialnumber'], redact=True)
        dev.close()  

    def handle_delete(self):
        pass

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        pass

    def _resolve_attribute(self, name):
        if name == 'hostname':
          return db_api.resource_data_get(self, 'hostname')
        elif name == 'model':
          return db_api.resource_data_get(self, 'model')
        elif name == 'serialnumber':
          return db_api.resource_data_get(self, 'serialnumber')

def resource_mapping():
    return {
        'OS::PyEZ::GetFacts': GetFacts,
    }
