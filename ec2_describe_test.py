import boto3
import pprint


def role_arn_to_session(**args):
    """
    Lets you assume a role and returns a session ready to use
    Usage :
        session = role_arn_to_session(
            RoleArn='arn:aws:iam::012345678901:role/example-role',
            RoleSessionName='ExampleSessionName')
        client = session.client('sqs')
    """
    client = boto3.client('sts')
    response = client.assume_role(**args)
    print "assume role will expired on   " + str(response['Credentials']['Expiration'])
    return boto3.Session(
        aws_access_key_id=response['Credentials']['AccessKeyId'],
        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
        aws_session_token=response['Credentials']['SessionToken'])



TARGET_ACCOUNT_ID='909119180557'
ROLE_ON_TARGET_ACCOUNT='arn:aws:iam::' + TARGET_ACCOUNT_ID + ':role/ITAdmin-Role'


pp=pprint.PrettyPrinter(indent=4)
ec2=boto3.resource('ec2')
instance = ec2.Instance('i-020d570e2eda4def3')

devicedict={}

block_device_mappings = instance.block_device_mappings
pp.pprint(block_device_mappings)
for block in block_device_mappings:
    print (block['DeviceName'],block['Ebs']['VolumeId'])
    devicedict.update({block['DeviceName']:block['Ebs']['VolumeId']})



voldict={}
for vol in instance.volumes.all():
    print (vol.volume_id,vol.volume_type)
    voldict.update({vol.volume_id:vol.volume_type})

print str(voldict)

for dev,vol in devicedict.items():
    print dev,vol,voldict[vol]

target_session = role_arn_to_session(
    RoleArn=ROLE_ON_TARGET_ACCOUNT,
    RoleSessionName='share-admin-temp-session',
    DurationSeconds = 40000
)

target_ec2 = target_session.client('ec2', region_name='us-east-1')
snapshotdict={}
print str(target_ec2.describe_snapshots)
for snap in target_ec2.describe_snapshots(OwnerIds=['909119180557'])['Snapshots']:
    if snap['Description'] in voldict.keys():
        snapshotdict.update({snap['Description'].strip():snap['SnapshotId']})
        print (snap['SnapshotId'], snap['Description'])


finaldict={}
for dev,vol in devicedict.items():
    print dev,vol,snapshotdict.get(vol,'NA'),voldict.get(vol,'NA')
    finaldict.update({dev:[vol,snapshotdict.get(vol,'NA'),voldict.get(vol,'NA')]})

pp.pprint(finaldict)

for vol,info in finaldict.items():
    print "  {"
    print ("    'DeviceName': '{0}',".format(vol))
    print ("    'Ebs': {" )
    print ("       'SnapshotId': '{0}',".format(info[1]))
    print ("       'VolumeType': '{0}'".format(info[2]))
    print ("    }")
    print ("  },")