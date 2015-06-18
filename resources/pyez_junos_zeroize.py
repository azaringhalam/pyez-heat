from heat.db import api as db_api
from heat.engine import properties
from heat.engine import resource
import logging
from os.path import isfile
import os
import re
import string

try:
    from jnpr.junos import Device
    from jnpr.junos.exception import *
    from jnpr.junos.utils.config import Config
    from jnpr.junos.version import VERSION
    if not float(re.match('\d+.\d+', VERSION).group()) >= 1.1:
        HAS_PYEZ = False
    else:
        HAS_PYEZ = True
except ImportError:
    HAS_PYEZ = False


class JunosZeroize(resource.Resource):
    '''
    JUNOS PyEZ resource for installation and configuration

    This resource is useful for installation and configuration of JUNOS devices
    '''
    PROPERTIES = (
        HOST, USER, PASSWORD, CONSOLE, ZEROIZE, LOGFILE, PORT, CHECK_MODE,
    ) = (
        'host', 'user', 'password', 'console', 'zeroize', 'logfile', 'port', 'check_mode',
    )

    properties_schema = {
        HOST: properties.Schema(
            properties.Schema.STRING,
            _('JUNOS device host name.'),
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
        CONSOLE: properties.Schema(
            properties.Schema.INTEGER,
            _('Use console port.'),
            required=True,
            default=None,
            update_allowed=False,
        ),
        ZEROIZE: properties.Schema(
            properties.Schema.STRING,
            _('Safety mechanism. You MUST set this to zeroize.'),
            required=True,
            default=None,
            update_allowed=False,
        ),
        LOGFILE: properties.Schema(
            properties.Schema.STRING,
            _('Path to log file.'),
            required=True,
            default=None,
            update_allowed=False,
        ),
        PORT: properties.Schema(
            properties.Schema.INTEGER,
            _('Path to diffs_file file.'),
            required=True,
            default=None,
            update_allowed=False,
        ),
        CHECK_MODE: properties.Schema(
            properties.Schema.INTEGER,
            _('Check mode.'),
            required=True,
            default=None,
            update_allowed=False,
        ),
    }
    
    def handle_create(self):
        assert self.properties[self.ZEROIZE] == 'zeroize', "You must set 'zeroize=zeroize' ({0})".format(self.properties[self.ZEROIZE])

        #
        # ! UNREACHABLE

        results = {}
    
        logfile = self.properties[self.LOGFILE]
        if logfile is not None:
            logging.basicConfig(filename=logfile, level=logging.INFO,
                                format='%(asctime)s:%(name)s:%(message)s')
            logging.getLogger().name = 'NETCONIFY:' + self.properties[self.HOST]
    
            def log_notify(self, event, message):
                logging.info("%s:%s" % (event, message))
            use_notifier = log_notify
        else:
            def silent_notify(self, event, message):
                pass
            use_notifier = silent_notify
    
        if self.properties[self.CONSOLE] is 0:
            # via NETCONF
            assert HAS_PYEZ, "junos-eznc >= 1.1.x is required for this module"
    
            dev = Device(self.properties[self.HOST], user=self.properties[self.USER], password=self.properties[self.PASSWORD], port=self.properties[self.PORT])
            try:
                use_notifier(None, 'LOGIN', 'host={0}'.format(self.properties[self.HOST]))
                dev.open()
                use_notifier(None, 'LOGIN', 'OK')
            except Exception as err:
                logging.info("connecting to host: {0}:{1}".format(self.properties[self.HOST], str(err)))
                return
                # --- UNREACHABLE ---
    
            use_notifier(None, 'ZEROIZE', 'invoking command')
            dev.cli('request system zeroize')
            results['changed'] = True
            # no close, we're done after this point.
        else:
            try:
                from netconify.cmdo import netconifyCmdo
                from netconify.constants import version
                if not float(re.match('\d+.\d+', version).group()) >= 1.0:
                    logging.info("junos-netconify >= 1.0.x is required for this module")
                    return
            except ImportError:
                logging.info("junos-netconify >= 1.0.x is required for this module")
                return
            nc_args = []
            nc_args.append(self.properties[self.CONSOLE])
            nc_args.append('--zeroize')
            if self.properties[self.USER] is not None:
                nc_args.append('--user=' + self.properties[self.USER])
            if self.properties[self.PASSWORD] is not None:
                nc_args.append('--passwd=' + self.properties[self.PASSWORD])
    
            try:
                nc = netconifyCmdo(notify=use_notifier)
                nc.run(nc_args)
            except Exception as err:
                logging.info("connecting to host: {0}".format(str(err)))
                return
            results['changed'] = True
    
        # indicate done in the logfile and return results
        use_notifier(None, 'DONE', 'OK')
        #module.exit_json(**results)
        
    def handle_delete(self):
        pass

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        pass

    def _resolve_attribute(self, name):
        pass


def resource_mapping():
    return {
        'OS::PyEZ::JunosZeroize': JunosZeroize,
    }
