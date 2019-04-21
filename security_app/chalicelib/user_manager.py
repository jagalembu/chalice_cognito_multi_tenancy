from boto3.dynamodb.conditions import Key


class User_DB(object):
    def list_items(self):
        pass

    def add_item(self,
                 principal_id,
                 username,
                 userpool_id,
                 firstname,
                 lastname,
                 metadata=None):
        pass

    def get_item(self, principal_id):
        pass

    def delete_item(self, principal_id):
        pass

    def update_item(self,
                    principal_id,
                    username,
                    firstname,
                    lastname,
                    state=None,
                    metadata=None):
        pass


class DynamoDBUser(User_DB):
    def __init__(self, table_resource):
        self._table = table_resource

    def list_all_items(self):
        response = self._table.scan()
        return response['Items']

    def list_items(self):
        response = self._table.scan()
        return response['Items']

    def add_item(self,
                 principal_id,
                 userpool_id,
                 firstname,
                 lastname,
                 metadata=None):
        self._table.put_item(
            Item={
                'principal_id': principal_id,
                'userpool_id': userpool_id,
                'firstname': firstname,
                'lastname': lastname,
                'state': 'unstarted',
                'metadata': metadata if metadata is not None else {},
            })
        return principal_id

    def get_item(self, principal_id):
        response = self._table.get_item(Key={'principal_id': principal_id}, )
        return response['Item']

    def delete_item(self, principal_id):
        self._table.delete_item(Key={'principal_id': principal_id})

    def update_item(self,
                    principal_id,
                    firstname,
                    lastname,
                    state=None,
                    metadata=None):
        # We could also use update_item() with an UpdateExpression.
        item = self.get_item(principal_id)
        if firstname is not None:
            item['firstname'] = firstname
        if lastname is not None:
            item['lastname'] = lastname
        if metadata is not None:
            item['metadata'] = metadata
        self._table.put_item(Item=item)