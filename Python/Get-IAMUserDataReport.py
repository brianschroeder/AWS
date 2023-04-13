import boto3
import csv
import pandas as pd
from datetime import datetime

iam_client = boto3.client('iam')
response = iam_client.list_users()
iamArray = []

for user in response['Users']:

    tags = iam_client.list_user_tags(UserName = user['UserName'])
    groups = (iam_client.list_groups_for_user(UserName = user['UserName']))['Groups']
    policies = (iam_client.list_attached_user_policies(UserName = user['UserName']))['AttachedPolicies']
    access_keys = (iam_client.list_access_keys(UserName = user['UserName']))['AccessKeyMetadata']
    
    grouplist = []
    policieslist = []
    accesskeylist = []

    for tag in (tags['Tags']):
       if (tag['Key']) == 'Owner':
         Owner = (tag['Value'])

    for group in groups:
        grouplist.append(group['GroupName'])

    for policy in policies:
        policieslist.append(policy['PolicyName'])

    for key in access_keys:
        keys_data = iam_client.get_access_key_last_used(AccessKeyId = key['AccessKeyId'])

        try:
           lastused_service = (keys_data['AccessKeyLastUsed']['ServiceName'])
           lastused_date = (keys_data['AccessKeyLastUsed']['LastUsedDate'])

           if lastused_service == 'N/A':
            last_used_service = ''
        except:
            continue


        iamTable = {

            'UserID': user['UserId'],
            'UserName': user['UserName'],
            'ARN': user['Arn'],
            'IAM User Creation Date': str((user['CreateDate'])),
            'Owner': Owner,
            'Groups': ','.join(grouplist),
            'Policies': ','.join(policieslist),
            'Access Key ID': key['AccessKeyId'],
            'Status': key['Status'],
            'Last Used Service': lastused_service,
            'Last Used Date':str(lastused_date),
            'Creation Date': str(key['CreateDate'])

            }

        iamArray.append(iamTable)

df = pd.DataFrame(data=iamArray, columns=['UserName', 'Access Key ID', 'Status', 'Last Used Date', 'Last Used Service', 'Creation Date' , 'UserID', 'ARN', 'IAM User Creation Date', 'Owner', 'Groups', 'Policies']).sort_values(by=['Last Used Date'])
df.to_csv('NBA-DEV-IAMUsers.csv', index=False)
