'''
Created on Nov 27, 2015

@author: azaringh
'''
import create_stack

config_node_ip = '10.10.10.156'
junos_device_ip = '10.10.4.101'
project_name = 'admin'
config_file ='/root/pyez-heat/config_examples/vmx_hostname.set'

StackData = {   'stack_name': 'junos_config',
                'yaml_file':'../template/pyez_installconfig.yaml',
                'jinja_path': '../jinja/',
                'jinja_file': 'pyez_installconfig.jinja',
                'stack_template': { 
                                     'host': junos_device_ip,
                                     'user': 'root',
                                     'password': 'juniper123',
                                     'file': config_file,
                                     'comment': 'Set hostname',
                                     'overwrite': 0
                                    }
               }

stack = create_stack.create_stack(config_node_ip, project_name, **StackData)
 
print stack