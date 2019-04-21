from uuid import uuid4
from boto3.dynamodb.conditions import Key


class Tenant_DB(object):
    def add_item(self, tenant_name, metadata=None):
        pass

    def get_item(self, tenant_id):
        pass

    def delete_item(self, tenant_id):
        pass


class UserTenants_DB(object):
    def list_items(self, principal_id):
        pass

    def add_item(self, principal_id, tenant_id, roles, metadata=None):
        pass

    def get_item(self, principal_id):
        pass

    def delete_item(self, principal_id):
        pass

    def update_item(self,
                    principal_id,
                    tenant_id,
                    roles,
                    state=None,
                    metadata=None):
        pass


class DynamoDBTenant(Tenant_DB):
    def __init__(self, table_resource):
        self._table = table_resource

    def list_all_items(self):
        response = self._table.scan()
        return response['Items']

    def add_item(self, tenant_name, metadata=None):
        uid = str(uuid4())
        self._table.put_item(
            Item={
                'tenant_id': uid,
                'tenant_name': tenant_name,
                'state': 'unstarted',
                'metadata': metadata if metadata is not None else {},
            })
        return uid

    def get_item(self, tenant_id):
        response = self._table.get_item(Key={'tenant_id': tenant_id}, )
        return response['Item']

    def delete_item(self, tenant_id):
        self._table.delete_item(Key={'tenant_id': tenant_id})

    def update_item(self, tenant_id, tenant_name, state=None, metadata=None):
        item = self.get_item(tenant_id)
        if tenant_name is not None:
            item['firstname'] = tenant_name
        self._table.put_item(Item=item)


class DynamoDBUserTenants(UserTenants_DB):
    def __init__(self, table_resource):
        self._table = table_resource

    def list_all_items(self):
        response = self._table.scan()
        return response['Items']

    def list_items(self, principal_id):
        response = self._table.query(
            KeyConditionExpression=Key('principal_id').eq(principal_id))
        return response['Items']

    def add_item(self, principal_id, tenant_id, roles, metadata=None):
        self._table.put_item(
            Item={
                'principal_id': principal_id,
                'tenant_id': tenant_id,
                'roles': roles,
                'state': 'unstarted',
                'metadata': metadata if metadata is not None else {},
            })
        return uid

    def get_item(self, principal_id, tenant_id):
        response = self._table.get_item(
            Key={
                'principal_id': principal_id,
                'tenant_id': tenant_id
            }, )
        return response['Item']

    def delete_item(self, principal_id, tenant_id):
        self._table.delete_item(Key={
            'tenant_id': tenant_id,
            'principal_id': principal_id
        })

    def update_item(self,
                    principal_id,
                    tenant_id,
                    roles,
                    state=None,
                    metadata=None):
        item = self.get_item(principal_id, tenant_id)
        if roles is not None:
            item['roles'] = roles
        self._table.put_item(Item=item)