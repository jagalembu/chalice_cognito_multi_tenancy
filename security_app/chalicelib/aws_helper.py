def parse_arn(arn):
    # http://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html
    elements = arn.split(':', 5)
    result = {
        'arn': elements[0],
        'partition': elements[1],
        'service': elements[2],
        'region': elements[3],
        'account': elements[4],
        'resource': elements[5],
        'resource_type': None,
        'tenant_id': None
    }
    if '/' in result['resource']:
        result['resource_type'] = result['resource'].split('/', 1)
        resourcesplit = result['resource'].split('/')
        result['tenant_id'] = resourcesplit[3]
    elif ':' in result['resource']:
        result['resource_type'] = result['resource'].split(':', 1)
    return result