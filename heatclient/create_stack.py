'''
Created on Nov 21, 2015

@author: azaringh
'''
import yaml
import jinja2
from heatclient.client import Client as Heat_Client
from keystoneclient.v2_0 import Client as Keystone_Client

def get_keystone_creds(config_node_ip, tenant_name):
    d = {}
    d['username'] = 'admin'
    d['password'] = 'contrail123'
    d['auth_url'] = 'http://' + config_node_ip + ':5000/v2.0'
    d['tenant_name'] = tenant_name
    return d

def create_stack(config_node_ip, tenant_name, **kwargs):
    cred = get_keystone_creds(config_node_ip, tenant_name)
    ks_client = Keystone_Client(**cred)
    heat_endpoint = ks_client.service_catalog.url_for(service_type='orchestration', endpoint_type='publicURL')
    heatclient = Heat_Client('1', heat_endpoint, token=ks_client.auth_token)
     
    f = open(kwargs['yaml_file'])
    txt = f.read()
    
    templateLoader = jinja2.FileSystemLoader( searchpath=kwargs['jinja_path'])
    templateEnv = jinja2.Environment( loader=templateLoader )
    TEMPLATE_FILE = kwargs['jinja_file']
    template = templateEnv.get_template( TEMPLATE_FILE )
    template_vars = kwargs['stack_template']
    data = yaml.load(template.render( template_vars ))
    
    tx = { "files": {}, "disable_rollback": "true", "stack_name": kwargs['stack_name'], "template": txt, "parameters": data, "environment": {}}
    
    stack = heatclient.stacks.create(**tx)
    return stack