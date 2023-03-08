#! /usr/bin/python3
import sys
from subprocess import call
import tempfile
import boto3
import logging
import argparse
import re
from subprocess import call
import ast
import os


def isIP(ip):
    ip_pattern = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    return ip_pattern.match(ip)

def get_instance(name, region):
    logging.info('the instance name:{}, and the region is:{}'.format(name, region))
    ec2client = boto3.client('ec2', region_name=region)
    ec2instances =  ec2client.describe_instances(
        Filters=[
           {
              'Name': 'tag:Name',
              'Values': [name]
           },
           {
              'Name': 'instance-state-name',
              'Values': ['running']
           }
       ],
        MaxResults=12,
    )
    logging.debug(ec2instances)
    return ec2instances


parser = argparse.ArgumentParser(
    description='connects to CSRv using SSH'
)

parser.add_argument(
    '--key',
    action='store',
    dest='key',
    help='the ssh key pair name used to connect to CSRv'
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


parser.add_argument(
    dest='parameters',
    nargs='+',
    help='ssh command arguments(do not include ssh), ex. user@1.1.1.1 or user@csrvname'
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

logging.info('key:{}, user@instance:{}, region:{}'.format(args.key, args.parameters, args.region))

ip = None
path = None

#parse the args parameters 
for i in args.parameters:
    remCommand =i
    if ip == None:
        index = args.parameters.index(i)
        tempUser = None
        tempIp = remCommand
        tempUser = "ec2-user"
        if '@' in remCommand:
            userip   = i.split('@')
            tempUser = userip[0]
            tempIp   = userip[1]
        
        command = '/usr/bin/ssh -o PreferredAuthentications=publickey -o Compression=no -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR'
        if isIP(tempIp):
            if tempUser:
                user = tempUser
            elif user:
                args.parameters[index] = '{0}@{1}'.format(user, i)
            ip = tempIp
            logging.info('New Connection String:{}'.format(args.parameters[index]))
        else:
            results = get_instance(tempIp,args.region)
            instances = []
            for reservation in results['Reservations']:
                for instance in reservation['Instances']:
                    logging.info('Instance Found:{}'.format(instance['PrivateIpAddress']))
                    instances.append(instance)
            logging.debug('# Instances Found:{}'.format(len(instances)))
            logging.debug('Instances Found:{}'.format(instances))
            if len(instances) == 0:
                raise ValueError('No instance found with CSRv name')
            elif len(instances) > 1:
                raise ValueError('Multiple instances found with CSRv name')
            ip = instances[0]['PrivateIpAddress']
            if tempUser:
                user = tempUser
            args.parameters[index] = '{0}@{1}'.format(user, ip)
            logging.info('New Connection String:{}'.format(args.parameters[index]))

if not isIP(ip):
    parser.print_help()
    quit()

# get secret manager's key data and store it in the tempfile, .

private_file= tempfile.NamedTemporaryFile(mode='w+')
logging.info('Private key file created:{}'.format(private_file.name))

secmanager = boto3.client('secretsmanager', region_name=args.region)
secrets = secmanager.describe_secret(SecretId = args.key)
secret_value_response = secmanager.get_secret_value(SecretId = args.key)
private_key = None
if secret_value_response:
    private_key = secret_value_response['SecretString']


if private_key:
    private_file.write(private_key)
    
    private_file.flush()
    logging.info('Private key write to file:{}'.format(private_file.name))


shell_command = ' '.join([command, logs_flag, ' '.join(unknow), '-i', private_file.name, ' '.join(args.parameters) ])

private_file.seek(0)
contents = private_file.read()
logging.info('content read out from file :{}'.format(contents))
logging.info(shell_command)
# run ssh command with ssh key point to the tempfile
ret = call(shell_command, shell=True)
# close the tempfile
#private_file.close()
sys.exit(ret)
