import argparse
from userpool_helper import get_env_var_from_config, record_as_env_var, USERPOOL_CFG
import boto3


def create_user_pool_client(user_pool_id, client_name, stage):
    client = boto3.client('cognito-idp')
    resp = client.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName=client_name,
        #Need to work on this because AWS SRP does not work with secret...
        GenerateSecret=False,
    )
    record_as_env_var(USERPOOL_CFG['env_var_pool_client'],
                      resp['UserPoolClient']['ClientId'], stage)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--stage', default='dev')
    parser.add_argument(
        '-c', '--clientname', help='Specify the client name for the user pool')
    args = parser.parse_args()
    create_user_pool_client(
        get_env_var_from_config(USERPOOL_CFG['env_var_poolid'], args.stage),
        args.clientname, args.stage)


if __name__ == '__main__':
    main()