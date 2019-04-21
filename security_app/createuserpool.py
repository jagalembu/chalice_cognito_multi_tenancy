import argparse
from userpool_helper import record_as_env_var, USERPOOL_CFG
import boto3


def create_user_pool(pool_name, region, stage):
    client = boto3.client('cognito-idp')
    resp = client.create_user_pool(
        PoolName=pool_name, UsernameAttributes=['email'])
    record_as_env_var(USERPOOL_CFG['env_var_poolid'], resp['UserPool']['Id'],
                      stage)
    record_as_env_var(
        USERPOOL_CFG['env_var_cognito_url'],
        f"https://cognito-idp.{region}.amazonaws.com/{resp['UserPool']['Id']}/.well-known/jwks.json",
        stage)

    respcustomattr = client.add_custom_attributes(
        UserPoolId=resp['UserPool']['Id'],
        CustomAttributes=[
            {
                'Name': 'app_role',
                'AttributeDataType': 'String',
                'DeveloperOnlyAttribute': False,
                'Mutable': True
            },
        ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--stage', default='dev')
    parser.add_argument('-r', '--region', help='Specify the AWS Region')
    parser.add_argument(
        '-p', '--poolname', help='Specify the pool name for the user pool')
    args = parser.parse_args()
    create_user_pool(args.poolname, args.region, args.stage)


if __name__ == '__main__':
    main()