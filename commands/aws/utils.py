import boto3


def create_aws_session(profile_name):
    return boto3.Session(profile_name=profile_name, region_name='eu-central-1')
