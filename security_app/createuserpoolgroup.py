import os
import uuid
import json
import argparse

import boto3

USERPOOL = {
    'env_var_poolid': 'APPUSERPOOLID',
    'env_var_cognito_url': 'COGNITOJWKSURL',
    'env_var_pool_client': 'APPCLIENTID',
}


def create_user_pool(pool_name, region, stage):
    client = boto3.client('cognito-idp')
    resp = client.create_user_pool(
        PoolName=pool_name, UsernameAttributes='email')
    record_as_env_var(USERPOOL['env_var_poolid'], resp['UserPool']['Id'],
                      stage)
    record_as_env_var(
        USERPOOL['env_var_cognito_url'],
        f"https://cognito-idp.{region}.amazonaws.com/{resp['UserPool']['Id']}/.well-known/jwks.json",
        stage)


def create_user_pool_client(user_pool_id, client_name, stage):
    client = boto3.client('cognito-idp')
    resp = client.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName=client_name,
        #Need to work on this because AWS SRP does not work with secret...
        GenerateSecret=False,
    )
    record_as_env_var(USERPOOL['env_var_pool_client'],
                      resp['UserPoolClient']['ClientId'], stage)


def create_user_pool_group(user_pool_id, group_name):
    client = boto3.client('cognito-idp')
    resp = client.create_group(
        GroupName=group_name,
        UserPoolId=user_pool_id,
    )


def create_admin_user(username, user_pool_id, group_name):
    client = boto3.client('cognito-idp')

    resp = client.admin_create_user(
        UserPoolId=user_pool_id,
        Username=username,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': username
            },
        ],
        ForceAliasCreation=False,
        DesiredDeliveryMediums=[
            'EMAIL',
        ])

    response = client.admin_add_user_to_group(
        UserPoolId=user_pool_id, Username=username, GroupName=group_name)


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--stage', default='dev')
    parser.add_argument('-g', '--groupname', help='Specify group name to be added to the user pool')    
    args = parser.parse_args()
    create_user_pool_group(
        get_env_var_from_config(USERPOOL['env_var_poolid'], args.stage), args.groupname)


if __name__ == '__main__':
    main()