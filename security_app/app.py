import boto3, os, urllib, json
from warrant.aws_srp import AWSSRP
from warrant.exceptions import ForceChangePasswordException
from warrant import Cognito
from chalice import Chalice, BadRequestError, AuthResponse, UnauthorizedError
from chalicelib import user_manager, tenant_manager, token_helper, aws_helper

app = Chalice(app_name='security_app')

keys = None

with urllib.request.urlopen(os.environ['COGNITOJWKSURL']) as response:
    keys = json.loads(response.read())['keys']

_TENANT_DB = None
_USER_TENANTS_DB = None
_USER_DB = None

# tenant creation - registration - Done manually for now
# event lambda
# 1) Create Schema - with admin user
# 2) RUn migration - to bring up to date
# 3) Create record in tenant table for new tenant

# Roles Table
# 1) Create roles

# create user
# 1) User created in in user pool
# 2) Create user table entry with user pool
# 3) Who can create users ?
#   a) For now only Line-45 admin user - manually created user
#   b) Tenant admin - add this feature later

# Tenant user association
# 1) User is added to Tenant
# 2) User is assigned a role for the Tenant

# Login
# 1) Loging through IDentity Pool with user pool id
# 2) Build tenant list with roles add it to tokem - Pre Token Generation Lambda Trigger - Can i use python?
# 3) Token refresh

# Authorization
# 1) Role based isolation with acess to URL + traverse post input for authorization + role


@app.authorizer()
def god_auth(auth_request):
    token = auth_request.token
    print(auth_request.method_arn)
    decoded = token_helper.retrieve_verified_token_claims(
        keys, token, os.environ['APPCLIENTID'])
    if isinstance(decoded, dict) and decoded['custom:app_role'] == 'godmode':
        return AuthResponse(
            routes=['*'],
            principal_id=decoded['sub'],
            context={"email": decoded['email']})
    # Default to cleaner option not allowing access.
    # but this code is executed as result of token_helper issues which
    # should be handled - Timed out tokens, invalid tokens. Future defect...
    return AuthResponse(routes=[], principal_id='none')


@app.authorizer()
def tenant_admin_and_god_auth(auth_request):
    token = auth_request.token
    decoded = token_helper.retrieve_verified_token_claims(
        keys, token, os.environ['APPCLIENTID'])
    if isinstance(decoded, dict) and (
            decoded['custom:app_role'] == 'godmode'
            or match_tenant_role('tenantadmin', decoded, auth_request)):
        return AuthResponse(
            routes=['*'],
            principal_id=decoded['sub'],
            context={"email": decoded['email']})
    # Default to cleaner option not allowing access.
    # but this code is executed as result of token_helper issues which
    # should be handled - Timed out tokens, invalid tokens. Future defect...
    return AuthResponse(routes=[], principal_id='none')


@app.route('/login', methods=['POST'])
def login():
    body = app.current_request.json_body
    aws = AWSSRP(
        username=body['email'],
        password=body['password'],
        pool_id=os.environ['APPUSERPOOLID'],
        client_id=os.environ['APPCLIENTID'])
    tokens = None
    try:
        if 'newpassword' in body:
            tokens = aws.set_new_password_challenge(body['newpassword'])
        else:
            tokens = aws.authenticate_user()
        return {'token': tokens, 'status': 'loggedin'}
    except ForceChangePasswordException:
        return {"status": "changepwd"}


@app.route('/user', methods=['POST'], authorizer=god_auth)
def admin_create_user():
    body = app.current_request.json_body

    client = cognito_client()

    try:
        resp = client.admin_create_user(
            UserPoolId=os.environ['APPUSERPOOLID'],
            Username=body['email'],
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': body['email']
                },
                {
                    'Name': 'custom:app_role',
                    'Value': 'tenantuser'
                },
            ],
            ForceAliasCreation=False,
            DesiredDeliveryMediums=[
                'EMAIL',
            ])

        print(resp)

    except client.exceptions.UsernameExistsException:
        return {"status": "userexists"}

    return {"status": "success"}


@app.route('/user', methods=['DELETE'], authorizer=god_auth)
def admin_delete_user():
    body = app.current_request.json_body

    # try:
    client = cognito_client()

    client.admin_delete_user(
        UserPoolId=os.environ['APPUSERPOOLID'], Username=body['username'])

    return {"status": "success"}


@app.route('/tenant', methods=['POST'], authorizer=god_auth)
def admin_create_tenant(tenant_id):
    body = app.current_request.json_body
    return get_tenant_db().add_item(
        tenant_name=body['tenantname'],
        metadata=body.get('metadata'),
    )


@app.route('/user/tenant', methods=['POST'])
def assign_user_tenants():
    pass


@app.route('/user/tenant/role', methods=['POST'])
def assign_user_tenants_roles():
    pass


@app.route(
    '/{tenant_id}/test', methods=['GET'], authorizer=tenant_admin_and_god_auth)
def test(tenant_id):
    return {
        "test": "good",
        "principal": app.current_request.context['authorizer']['principalId'],
        "email": app.current_request.context['authorizer']['email'],
        "tenant_id": tenant_id
    }


def cognito_client():
    return boto3.client('cognito-idp')


def match_tenant_role(in_tenant_role, claims, auth_request):
    if isinstance(claims, dict):
        tenant_id = aws_helper.parse_arn(auth_request.method_arn)['tenant_id']
        if tenant_id == None:
            return False

        if f'{tenant_id}_roles' not in claims:
            return False

        tenant_roles = claims[f'{tenant_id}_roles']

        print(tenant_roles)
         
        if in_tenant_role in tenant_roles:
            print('matched')
            return True
        return False

    return False


def get_user_db():
    global _USER_DB
    if _USER_DB is None:
        _USER_DB = user_manager.DynamoDBUser(
            boto3.resource('dynamodb').Table(os.environ['TENANT_TABLE_NAME']))
    return _USER_DB


def get_tenant_db():
    global _TENANT_DB
    if _TENANT_DB is None:
        _TENANT_DB = tenant_manager.DynamoDBTenant(
            boto3.resource('dynamodb').Table(os.environ['TENANT_TABLE_NAME']))
    return _TENANT_DB


def get_user_tenants_db():
    global _USER_TENANTS_DB
    if _USER_TENANTS_DB is None:
        _USER_TENANTS_DB = tenant_manager.DynamoDBUserTenants(
            boto3.resource('dynamodb').Table(
                os.environ['USER_TENANTS_TABLE_NAME']))
    return _USER_TENANTS_DB