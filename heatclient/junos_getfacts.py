'''
Created on Nov 27, 2015

@author: azaringh
'''
import create_stack

config_node_ip = '10.10.10.156'
junos_device_ip = '10.10.4.101'
project_name = 'admin'

StackData = {   'stack_name': 'junos_getfacts',
                'yaml_file':'../template/pyez_getfacts.yaml',
                'jinja_path': '../jinja/',
                'jinja_file': 'pyez_getfacts.jinja',
                'stack_template': { 
                                     'host': junos_device_ip,
                                     'user': 'root',
                                     'password': 'juniper123',
                                    }
               }

stack = create_stack.create_stack(config_node_ip, project_name, **StackData)
 
print stack