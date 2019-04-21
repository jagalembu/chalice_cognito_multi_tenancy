import os
import boto3
from chalice import Chalice, AuthResponse
from chalicelib import auth, db

app = Chalice(app_name='mytodo')
app.debug = False
_DB = None
_USER_DB = None


@app.route('/login', methods=['POST'])
def login():
    body = app.current_request.json_body
    record = get_users_db().get_item(
        Key={'username': body['username']})['Item']
    jwt_token = auth.get_jwt_token(body['username'], body['password'], record)
    return {'token': jwt_token.decode('utf-8')}


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
def jwt_auth(auth_request):
    token = auth_request.token
    decoded = auth.decode_jwt_token(token)
    return AuthResponse(routes=['*'], principal_id=decoded['sub'])


def get_users_db():
    global _USER_DB
    if _USER_DB is None:
        _USER_DB = boto3.resource('dynamodb').Table(
            os.environ['USERS_TABLE_NAME'])
    return _USER_DB


# Rest API code


def get_app_db():
    global _DB
    if _DB is None:
        _DB = db.DynamoDBTodo(
            boto3.resource('dynamodb').Table(os.environ['APP_TABLE_NAME']))
    return _DB


def get_authorized_username(current_request):
    return current_request.context['authorizer']['principalId']


@app.route('/todos', methods=['GET'], authorizer=jwt_auth)
def get_todos():
    username = get_authorized_username(app.current_request)
    return get_app_db().list_items(username=username)


@app.route('/todos', methods=['POST'], authorizer=jwt_auth)
def add_new_todo():
    body = app.current_request.json_body
    username = get_authorized_username(app.current_request)
    return get_app_db().add_item(
        username=username,
        description=body['description'],
        metadata=body.get('metadata'),
    )


@app.route('/todos/{uid}', methods=['GET'], authorizer=jwt_auth)
def get_todo(uid):
    username = get_authorized_username(app.current_request)
    return get_app_db().get_item(uid, username=username)


@app.route('/todos/{uid}', methods=['DELETE'], authorizer=jwt_auth)
def delete_todo(uid):
    username = get_authorized_username(app.current_request)
    return get_app_db().delete_item(uid, username=username)


@app.route('/todos/{uid}', methods=['PUT'], authorizer=jwt_auth)
def update_todo(uid):
    body = app.current_request.json_body
    username = get_authorized_username(app.current_request)
    get_app_db().update_item(
        uid,
        description=body.get('description'),
        state=body.get('state'),
        metadata=body.get('metadata'),
        username=username)