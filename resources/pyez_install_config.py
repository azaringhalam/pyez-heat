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


class InstallConfig(resource.Resource):
    '''
    JUNOS PyEZ resource for installation and configuration

    This resource is useful for installation and configuration of JUNOS devices
    '''
    PROPERTIES = (
        HOST, USER, PASSWORD, CONSOLE, FILE, OVERWRITE, LOGFILE, DIFFS_FILE, SAVEDIR, TIMEOUT, COMMENT, PORT, CHECK_MODE
    ) = (
        'host', 'user', 'password', 'console', 'file', 'overwrite', 'logfile', 'diffs_file', 'savedir', 'timeout', 'comment', 'port', 'check_mode',
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
            properties.Schema.STRING,
            _('Use console port.'),
            required=False,
            default=None,
            update_allowed=False,
        ),
        FILE: properties.Schema(
            properties.Schema.STRING,
            _('Configuration file.'),
            required=True,
            default=None,
            update_allowed=False,
        ),
        OVERWRITE: properties.Schema(
            properties.Schema.NUMBER,
            _('Overwrite flag.'),
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
        DIFFS_FILE: properties.Schema(
            properties.Schema.STRING,
            _('Path to diffs_file file.'),
            required=True,
            default=None,
            update_allowed=False,
        ),
        SAVEDIR: properties.Schema(
            properties.Schema.STRING,
            _('Directory to save device facts.'),
            required=True,
            default=None,
            update_allowed=False,
        ),
        TIMEOUT: properties.Schema(
            properties.Schema.INTEGER,
            _('NETCONF RPC timeout.'),
            required=True,
            default=None,
            update_allowed=False,
        ),
        COMMENT: properties.Schema(
            properties.Schema.STRING,
            _('Comments for commit.'),
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
    
    def junos_install_config(self):
        cu = Config(self.dev)
    
        results = {}
    
        file_path = self.properties[self.FILE]
        file_path = os.path.abspath(file_path)
    
        results['file'] = file_path
        results['changed'] = False
    
        logfile = self.properties[self.LOGFILE]
        if logfile is not None:
            logging.basicConfig(filename=logfile, level=logging.INFO,
                                format='%(asctime)s:%(name)s:%(message)s')
            logging.getLogger().name = 'CONFIG:' + self.properties[self.HOST]

        logging.info("pushing file: {0}".format(file_path))
        try:
            logging.info("taking lock")
            cu.lock()
    
            try:
                # load the config.  the cu.load will raise
                # an exception if there is even a warning.
                # so we want to avoid that condition.
                logging.info("loading config")
                load_args = {'path': file_path}
                overwrite = self.properties[self.OVERWRITE]
                if True == overwrite:
                    load_args['overwrite'] = True
                elif False == overwrite:
                    load_args['merge'] = True
                cu.load(**load_args)
                logging.info("load arguments: {0}".format(load_args))
            except ValueError as err:
                logging.error("unable to load config:{0}".format(err.message))
                raise err
            except ConfigLoadError as err:
                logging.error("unable to load config:{0},{1},{2}".format(err.errs['severity'],
                                                                         err.errs['bad_element'],
                                                                         err.errs['message']))
                raise err
            except Exception as err:
                if err.rsp.find('.//ok') is None:
                    rpc_msg = err.rsp.findtext('.//error-message')
                    logging.error("unable to load config:{0}".format(rpc_msg))
                raise err
            else:
                pass
    
            diff = cu.diff()
    
            if diff is not None:
                diffs_file = self.properties[self.DIFFS_FILE]
                if diffs_file is not None:
                    try:
                        f = open(diffs_file, 'w')
                        f.write(diff)
                        f.close()
                    except IOError as (errno, strerror):
                        msg = "Problem with diffs_file {0}: ".format(diffs_file)
                        msg += "I/O Error: ({0}): {1}".format(errno, strerror)
                        #module.fail_json(msg=msg)
                    except:
                        msg = "Problem with diffs_file {0}: ".format(diffs_file)
                        #msg += "Unexpected error:", sys.exc_info()[0]
                        #module.fail_json(msg=msg)
    
                if (self.properties[self.CHECK_MODE]):
                    logging.info("doing a commit-check, please be patient")
                    cu.commit_check()
                else:
                    logging.info("committing change, please be patient")
                    if self.properties[self.COMMENT] is not None:
                        cu.commit(comment=self.properties[self.COMMENT])
                    else:
                        cu.commit()
                    results['changed'] = True
    
            logging.info("unlocking")
            cu.unlock()
            logging.info("change completed")
    
        except LockError:
            results['failed'] = True
            msg = "Unable to lock configuration"
            results['msg'] = msg
            logging.error(msg)
    
        except CommitError as err:
            results['failed'] = True
            msg = "Unable to commit configuration:{0},{1},{2}".format(err.errs['severity'],
                                                                      err.errs['bad_element'],
                                                                      err.errs['message'])
            results['msg'] = msg
            logging.error(msg)
    
        except Exception as err:
            results['failed'] = True
            msg = "Unable to make changes"
            results['msg'] = msg
            logging.error(msg)
    
        return results

    
    def _load_via_netconf(self):
    
        logfile = self.properties[self.LOGFILE]
        if logfile is not None:
            logging.basicConfig(filename=logfile, level=logging.INFO,
                                format='%(asctime)s:%(name)s:%(message)s')
            logging.getLogger().name = 'CONFIG:' + self.properties[self.HOST]
    
        logging.info("connecting to host: {0}@{1}:{2}".format(self.properties[self.USER], self.properties[self.HOST], self.properties[self.PORT]))
    
        try:
            self.dev = Device(host=self.properties[self.HOST], user=self.properties[self.USER], password=self.properties[self.PASSWORD], port=self.properties[self.PORT])
            self.dev.open()
        except Exception as err:
            msg = 'unable to connect to {0}: {1}'.format(self.properties[self.HOST], str(err))
            print msg
            return
    
        timeout = int(self.properties[self.TIMEOUT])
        if timeout > 0:
            self.dev.timeout = timeout
        self.junos_install_config()
        self.dev.close()
    
    def _load_via_console(self):
        try:
            from netconify.cmdo import netconifyCmdo
            from netconify.constants import version
            assert float(re.match('\d+.\d+', version).group()) >= 1.0, 'junos-netconify >= 1.0.x is required for this module'
        except ImportError:
            msg='junos-netconify >= 1.0.x is required for this module'
            #module.fail_json
            print msg
    
        c_args = []
        c_args.append((self.properties[self.CONSOLE]))
        c_args.append('--file=' + self.properties[self.FILE])
        if self.properties[self.SAVEDIR] is not None:
            c_args.append('--savedir=' + self.properties[self.SAVEDIR])
        c_args.append('--user=' + self.properties[self.USER])
        if self.properties[self.PASSWORD] is not None:
            c_args.append('--passwd=' + self.properties[self.PASSWORD])
    
        # the default mode for loading a config via the console
        # is to load-overwrite.  So we need to check the module
        # option and set the "--merge" option if overwrite is False
    
        #overwrite = module.boolean(module.params['overwrite'])
        overwrite = self.properties[self.OVERWRITE]
        if overwrite is False:
            c_args.append('--merge')
    
        c_args.append(self.properties[self.HOST])
    
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
    
        try:
            nc = netconifyCmdo(notify=use_notifier)
            c_results = nc.run(c_args)
        except Exception as err:
            #module.fail_json(msg=str(err))
            logging.info("netconfify failed: {0}".format(str(err)))
            return
        m_results = dict(changed=c_results['changed'])
        if c_results['failed'] is True:
            #module.fail_json(msg=c_results['errmsg'])
            logging.info("netconfify failed: {0}".format(c_results['errmsg']))
            return
        else:
            #module.exit_json(**m_results)
            print (m_results)

    def handle_create(self):
        assert HAS_PYEZ, "junos-eznc >= 1.1.x is required for this module"
        assert isfile(self.properties[self.FILE]), 'file not found: {0}'.format(self.properties[self.FILE])
        
        _ldr = self._load_via_netconf if self.properties[self.CONSOLE] is None else self._load_via_console
        _ldr()
            
    def handle_delete(self):
        pass

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        pass

    def _resolve_attribute(self, name):
        pass


def resource_mapping():
    return {
        'OS::PyEZ::InstallConfig': InstallConfig,
    }
