import os, json

USERPOOL_CFG = {
    'env_var_poolid': 'APPUSERPOOLID',
    'env_var_cognito_url': 'COGNITOJWKSURL',
    'env_var_pool_client': 'APPCLIENTID',
}


def get_env_var_from_config(key, stage):
    with open(os.path.join('.chalice', 'config.json')) as f:
        data = json.load(f)
        return data['stages'][stage]['environment_variables'][key]
    raise Exception('problem loading config')


def record_as_env_var(key, value, stage):
    with open(os.path.join('.chalice', 'config.json')) as f:
        data = json.load(f)
        data['stages'].setdefault(stage, {}).setdefault(
            'environment_variables', {})[key] = value
    with open(os.path.join('.chalice', 'config.json'), 'w') as f:
        serialized = json.dumps(data, indent=2, separators=(',', ': '))
        f.write(serialized + '\n')