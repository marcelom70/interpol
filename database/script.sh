#!/bin/bash
#Creation of instance for postgres database using script

aws ec2 create-security-group --group-name 'database-instace-sg' 
    --description 'Instance that allows only Postgres default port besides ssh, of course' 
    --vpc-id 'vpc-0f01f6ae053e554e4' 

aws ec2 authorize-security-group-ingress 
    --group-id 'sg-09c0529f26bbbe7af' 
    --ip-permissions '{"IpProtocol":"tcp","FromPort":22,"ToPort":22,"IpRanges":[{"CidrIp":"0.0.0.0/0"}]}' '{"IpProtocol":"tcp","FromPort":5432,"ToPort":5432,"IpRanges":[{"CidrIp":"0.0.0.0/0"}]}' 

aws ec2 run-instances --image-id 'ami-06a73f9d93a3879b5' 
    --instance-type 't3.micro' --key-name 'sa-east-1' 
    --network-interfaces '{"AssociatePublicIpAddress":true,"DeviceIndex":0,"Groups":["sg-09c0529f26bbbe7af"]}' 
    --credit-specification '{"CpuCredits":"unlimited"}' 
    --tag-specifications '{"ResourceType":"instance","Tags":[{"Key":"Name","Value":"database-instance"}]}' 
    --iam-instance-profile '{"Arn":"arn:aws:iam::358592703806:instance-profile/AWS-SSM"}' 
    --metadata-options '{"HttpEndpoint":"enabled","HttpPutResponseHopLimit":2,"HttpTokens":"required"}' 
    --private-dns-name-options '{"HostnameType":"ip-name","EnableResourceNameDnsARecord":true,"EnableResourceNameDnsAAAARecord":false}' 
    --count '1' 
