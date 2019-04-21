import argparse
from userpool_helper import get_env_var_from_config, USERPOOL_CFG
import boto3


def create_admin_user(username, user_pool_id):
    client = boto3.client('cognito-idp')

    resp = client.admin_create_user(
        UserPoolId=user_pool_id,
        Username=username,
        UserAttributes=[
            {
                'Name': 'email',
                'Value': username
            },
            {
                'Name': 'custom:app_role',
                'Value': 'godmode'
            },
        ],
        ForceAliasCreation=False,
        DesiredDeliveryMediums=[
            'EMAIL',
        ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--stage', default='dev')
    parser.add_argument(
        '-e', '--email', help='Specify the username which is an email address')
    args = parser.parse_args()
    create_admin_user(
        args.email,
        get_env_var_from_config(USERPOOL_CFG['env_var_poolid'], args.stage))


if __name__ == '__main__':
    main()