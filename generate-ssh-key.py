#! /usr/bin/python3
import sys
import boto3
import logging
import argparse


parser = argparse.ArgumentParser(
    description='Generate the SSH key pair and store in secretsmanager and create EC2 SSH key'
)

parser.add_argument(
    '--key',
    action='store',
    dest='key',
    help='the key pair name used as secret and ssh key name'
)

parser.add_argument(
    '-v',
    '--verbose',
    action='count',
    dest='verbose',
    help='verbose level. Accepts multiple: -vvv'
)

parser.add_argument(
    '--region',
    action='store',
    dest='region',
    help='the AWS region, default is us-east-1',
    default='us-east-1'
)


args, unknow = parser.parse_known_args()


logs_flag = ''
if args.verbose == None:
    level = logging.WARNING
elif args.verbose == 1:
    level = logging.INFO
    logs_flag = '-v'
elif args.verbose > 1:
    level = logging.DEBUG
    logs_flag = '-vvv'

logging.basicConfig(level=level)

logging.info('key:{},  region:{}'.format(args.key, args.region))


#call aws cli to store the private key to secretsmanager
secmanager = boto3.client('secretsmanager', region_name=args.region)
secrets = secmanager.list_secrets(
    IncludePlannedDeletion =False,
    MaxResults=20
)

found_secret=[]
for secret in secrets['SecretList']:
    logging.info('list the secret with name:{}'.format(secret['Name'] ))
    if secret['Name'] == args.key:
        found_secret.append(secret)
        logging.info('found the secret with the given name:{}'.format(secret['Name'] ))
if len(found_secret)  > 1:
    raise ValueError('found more than one secret with same name, make sure you input the right key name or delete the duplicated secrets with same name')
elif len(found_secret) == 0:
    raise ValueError('did not find any secret with the given name, make sure you input the right key name which secret be created by terraform')  

#call AWS cli to store the public key to EC2 ssh key pair
ec2_client = boto3.client('ec2', region_name=args.region)
ssh_keys = ec2_client.describe_key_pairs()
#logging.info('ssh key output:{}'.format(ssh_keys ))
found_ssh_key= []
for ssh_key in ssh_keys['KeyPairs']:
    if ssh_key['KeyName'] == args.key:
        found_ssh_key.append(ssh_key)
        logging.info('found ssh key pair with keyname:{}'.format(ssh_key['KeyName']))

create_key_output = {}
if len(found_ssh_key) == 0:
    logging.info('didnot found the ssh key with given name will create a new one')
    create_key_output =ec2_client.create_key_pair(
        KeyName = args.key,
        KeyType = 'rsa',
        TagSpecifications=[
            {
                'ResourceType':'key-pair',
                'Tags':[
                    {
                        'Key':'purpose',
                        'Value':'used for CSRv'
                    }
                ]
            }
        ],
        KeyFormat='pem'
    )
    logging.info('create the SSH key pair with ID:{}'.format(create_key_output['KeyPairId']))
else:
    raise ValueError('found the SSH key pair with same name, please manual delete it first') 
    for key in found_ssh_key:
        delete_key_output = {}
        logging.info('try to delete key pair with name:{}'.format(key['KeyName']))
        delete_key_output = ec2_client.delete_key_pair(
            KeyName = key['KeyName']
        )
        logging.info('delete the existing key pair before create key pair with the same name, the delete response with code:{}'.format(delete_key_output['ResponseMetadata']['HTTPStatusCode']))

    create_key_output =ec2_client.create_key_pair(
        KeyName = args.key,
        KeyType = 'rsa',
        TagSpecifications=[
            {
                'ResourceType':'key-pair',
                'Tags':[
                    {
                        'Key':'purpose',
                        'Value':'used for CSRv'
                    }
                ]
            }
        ],
        KeyFormat='pem'
    )
    logging.info('after deleted existing key,the SSH key pair with ID:{}'.format(create_key_output['KeyPairId']))

private_key= None
if create_key_output['KeyName'] == args.key:
    private_key = create_key_output['KeyMaterial']
    logging.info('got the private key with name:{}'.format(create_key_output['KeyName'] ))


if private_key:     
    put_value_response = secmanager.put_secret_value(
        SecretId = found_secret[0]['Name'],
        SecretString= private_key
        )
    logging.info('put secret with Name:{} and version ID:{}'.format(put_value_response['Name'],put_value_response['VersionId'] ))
    if put_value_response['Name'] == args.key:
        sys.exit(0)
sys.exit(1)
