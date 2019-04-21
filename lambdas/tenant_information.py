def lambda_handler(event, context):
    event['response'] = {
        "claimsOverrideDetails": {
            "claimsToAddOrOverride": {
                "t1": "tenant_admin"
            }
        }
    }
    return event