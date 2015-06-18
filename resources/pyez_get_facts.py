import string

from heat.db import api as db_api
from heat.engine import properties
from heat.engine import resource
from jnpr.junos import Device


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
        'HOME': _("HOME."),
        'reboot_reason': _("last reboot reason."),
        'status': _("status."),
        'up_time': _("up time."),
        'domain': _("domain."),
        'fqdn': _("fqdn."),
        'ifd_style': _("ifd_style."),
        'personality': _("personality."),
        'switch_style': _("switch style."),
        'version': _("version."),
    }

    def handle_create(self):
        dev = Device(host=self.properties[self.TARGET], user=self.properties[self.USER], password=self.properties[self.PASSWORD])  
        dev.open()  
        db_api.resource_data_set(self, 'hostname', dev.facts['hostname'], redact=True)
        db_api.resource_data_set(self, 'model', dev.facts['model'], redact=True)
        db_api.resource_data_set(self, 'serialnumber', dev.facts['serialnumber'], redact=True)
        db_api.resource_data_set(self, 'HOME', dev.facts['HOME'], redact=True)
        db_api.resource_data_set(self, 'reboot_reason', dev.facts['RE0']['last_reboot_reason'], redact=True)
        db_api.resource_data_set(self, 'status', dev.facts['RE0']['status'], redact=True)
        db_api.resource_data_set(self, 'up_time', dev.facts['RE0']['up_time'], redact=True)
        db_api.resource_data_set(self, 'domain', dev.facts['domain'], redact=True)
        db_api.resource_data_set(self, 'fqdn', dev.facts['fqdn'], redact=True)
        db_api.resource_data_set(self, 'ifd_style', dev.facts['ifd_style'], redact=True)
        db_api.resource_data_set(self, 'personality', dev.facts['personality'], redact=True)
        db_api.resource_data_set(self, 'switch_style', dev.facts['switch_style'], redact=True)
        db_api.resource_data_set(self, 'version', dev.facts['version'], redact=True)
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
        elif name == 'HOME':
            return db_api.resource_data_get(self, 'HOME')
        elif name == 'reboot_reason':
            return db_api.resource_data_get(self, 'reboot_reason')
        elif name == 'status':
            return db_api.resource_data_get(self, 'status')
        elif name == 'up_time':
            return db_api.resource_data_get(self, 'up_time')
        elif name == 'domain':
            return db_api.resource_data_get(self, 'domain')
        elif name == 'fqdn':
            return db_api.resource_data_get(self, 'fqdn')
        elif name == 'ifd_style':
            return db_api.resource_data_get(self, 'ifd_style')
        elif name == 'personality':
            return db_api.resource_data_get(self, 'personality')
        elif name == 'switch_style':
            return db_api.resource_data_get(self, 'switch_style')
        elif name == 'version':
            return db_api.resource_data_get(self, 'version')
        

def resource_mapping():
    return {
        'OS::PyEZ::GetFacts': GetFacts,
    }

