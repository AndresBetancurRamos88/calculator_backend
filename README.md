# calculator backend

## Project Description
```
This project is a calculator where you can do the following mathematical operations:
- Addition
- Subtraction,
- Multiplication, 
- Division, 
- Square root
- Random string generation
For each operation credits will be deducted from the user (every time a user is created by default, 200 credits are granted)
```

## Technologies Used
```
- Python
- Django
- Django Rest framework
- AWS S3
- AWS Lambda
- AWS API Getaway
- AWS RDS postgres
- AWS CloudWatch
```
## Getting Started
```
Clone this repository 
- git clone https://github.com/AndresBetancurRamos88/calculator_backend

```

### Run project locally
```
Use the docker image to create the other containers with docker-compose
create the following .env files:
    - .env-db: contains the parameters for the connection to the database
        DB_USER=postgres
        DB_PASSWORD=postgres
        DB_NAME=db_name
        DB_HOST=db_host
        DB_PORT=5432

    - .env-django: contains the secrete key that each django project create 
        SECRET_KEY=django_key

    - .env-pgadmin: in case you want to see the data from the database you can use pgadmin, otherwise you can remove the container from the docker-compose
        PGADMIN_DEFAULT_EMAIL=admin@admin.com
        PGADMIN_DEFAULT_PASSWORD=admin

Open a command executor and go to the root of your project.

Then run the following commands:
    - docker compose up --build -d (to build your containers)
    - docker ps (to get the container id of your application)
    - docker exec -it id_application /bin/sh/ (to enter the application container)
    - python manage.py makemigration
    - python manage.py migrate
    - python manage.py createsuperuser

login into the admin panel with user you ctreated previous:
    example: https://localhost:8000/admin

Go to the folowing url to register you application:
    https://localhost:8000/o/applications

Fill in the following fields
    - Name: application name
    - Client type: Confidencial
    - Authorization Grant Type: password

Before save take the Client id and Client secret (frontend will need them)

you can start to use the application
```

### Run project on AWS

#### Create AWS Policy for AWS Role
```
Go to AWS IAM an create the following policy (Name the policy something like: ZappaRolePolicy)
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:*"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "lambda:GetFunctionConfiguration",
                    "lambda:UpdateFunctionConfiguration",
                    "lambda:InvokeFunction"
                ],
                "Resource": [
                    "*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "xray:PutTraceSegments",
                    "xray:PutTelemetryRecords"
                ],
                "Resource": [
                    "*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "ec2:AttachNetworkInterface",
                    "ec2:CreateNetworkInterface",
                    "ec2:DeleteNetworkInterface",
                    "ec2:DescribeInstances",
                    "ec2:DescribeSecurityGroups",
                    "ec2:DescribeNetworkInterfaces",
                    "ec2:DetachNetworkInterface",
                    "ec2:ModifyNetworkInterfaceAttribute",
                    "ec2:ResetNetworkInterfaceAttribute"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:*"
                ],
                "Resource": "arn:aws:s3:::*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "kinesis:*"
                ],
                "Resource": "arn:aws:kinesis:*:*:*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "sns:*"
                ],
                "Resource": "arn:aws:sns:*:*:*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "sqs:*"
                ],
                "Resource": "arn:aws:sqs:*:*:*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:*"
                ],
                "Resource": "arn:aws:dynamodb:*:*:*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "route53:*"
                ],
                "Resource": "*"
            }
        ]
    }
```

#### Create AWS IAM ROLE
```
For "Select Type of trusted entity" select "AWS service"

For "Choose the service that will use this role" select "Lambda"

Click "Next: Permissions"

Find the newly created policy from above ZappaRolePolicy and select it

Click Next: Review

Give a role name such as ZappaDjangoRole

Add/change Role description as needed.

Click Create role

Click on your newly created role (such as ZappaDjangoRole) in IAM roles

Click Trust Relationships

Click Edit trust relationship and add the following json: 
    { 
    "Version": "2012-10-17", 
    "Statement": [ 
        { "Sid": "", "Effect": "Allow", "Principal": 
        { "Service": [ "lambda.amazonaws.com", "apigateway.amazonaws.com", "events.amazonaws.com" ] }, 
        "Action": "sts:AssumeRole" } 
        ] 
    }

Click Update Trust Policy

Copy the Role ARN such as arn:aws:iam::123456:role/ZappaDjangoRole
```

#### Group-Level Permissions Policy for Lambda Role and Zappa Related
```
Create the following policy

add in: json 
    { 
        "Version": "2012-10-17", 
        "Statement": [ 
            { 
                "Effect": "Allow", "Action": [ 
                "iam:GetRole", 
                "iam:PutRolePolicy" 
                ], 
                "Resource": [ "*" ] 
            }, 
            { 
                "Effect": "Allow", 
                "Action": [ "iam:PassRole" ], 
                "Resource": [ "arn:aws:iam::[ROLE_ID]:role/[ROLENAME]" ] 
            }, 
            { 
                "Effect": "Allow", 
                "Action": [ 
                    "apigateway:DELETE", 
                    "apigateway:GET", 
                    "apigateway:PATCH", 
                    "apigateway:POST", 
                    "apigateway:PUT", 
                    "cloudformation:CreateStack", 
                    "cloudformation:DeleteStack", 
                    "cloudformation:DescribeStackResource", 
                    "cloudformation:DescribeStacks", 
                    "cloudformation:ListStackResources", 
                    "cloudformation:UpdateStack", 
                    "events:DeleteRule", 
                    "events:DescribeRule", 
                    "events:ListRules", 
                    "events:ListRuleNamesByTarget", 
                    "events:ListTargetsByRule", 
                    "events:PutRule", 
                    "events:PutTargets", 
                    "events:RemoveTargets", 
                    "lambda:*", 
                    "lambda:AddPermission", 
                    "lambda:CreateFunction", 
                    "lambda:DeleteFunction", 
                    "lambda:GetFunction", 
                    "lambda:GetFunctionConfiguration", 
                    "lambda:ListVersionsByFunction", 
                    "lambda:UpdateFunctionCode", 
                    "logs:DescribeLogStreams", 
                    "logs:FilterLogEvents", 
                    "route53:ListHostedZones", 
                    "route53:ChangeResourceRecordSets", 
                    "route53:GetHostedZone" 
                ], 
                "Resource": [ "*" ] 
            } 
        ] 
    }

Replace arn:aws:iam::[ROLE_ID]:role/[ROLENAME] with your above Role ARN

Add the name, such as ZappaUserGeneralPolicy
```

#### Create an S3 Bucket

#### Group-Level Permissions Policy for S3 for Zappa
```
Create the following policy (Name the policy something like: ZappaUserS3Policy)
add in: json 
    { 
        "Version": "2012-10-17", 
        "Statement": [ 
            { 
                "Effect": "Allow", 
                "Action": [ "s3:ListBucket" ],
                "Resource": [ "arn:aws:s3:::[YOUR_BUCKET_NAME]" ] 
            }, 
            { 
                "Effect": "Allow", 
                "Action": [ 
                    "s3:DeleteObject", 
                    "s3:GetObject", 
                    "s3:PutObject", 
                    "s3:CreateMultipartUpload", 
                    "s3:AbortMultipartUpload", 
                    "s3:ListMultipartUploadParts", 
                    "s3:ListBucketMultipartUploads" 
                ], 
                "Resource": [ "arn:aws:s3:::[YOUR_BUCKET_NAME]/*" ] 
            } 
        ] 
    }
```

#### Create AWS IAM Group
```
Set a name for your group, something like: ZappaGroup

Find your policy ZappaUserS3Policy and ZappaUserGeneralPolicy
```

#### Create AWS IAM User.
```
Add user to the ZappaGroup created above
```

#### Django configuration
```
Install pipenv

Open a command executor and go to the root of your project an run the following code

pipenv shell 

pipenv install 

zappa init

Once the execution is finished, a zappa_settings.json file will be generated

update the file like this

{
    "dev": {
        "aws_region": "us-west-2",
        "django_settings": "zapdj.settings",
        "profile_name": "default",
        "project_name": "zappacfe",
        "runtime": "python3.6",
        "s3_bucket": "my-awesome-zappa-bucket",
        "timeout_seconds": 900,
        "manage_roles": false,
        "role_name": "ZappaDjangoRole",
        "role_arn": "arn:aws:iam::123456:role/ZappaDjangoRole"
    }
}

run the following code on your terminal:
zappa deploy dev

At the end your goint to get the url to your live django project
https://123456789.execute-api.us-west-2.amazonaws.com/dev

in your django project update the settings 
ALLOWED_HOSTS = ['123456789.execute-api.us-west-2.amazonaws.com']
Save the settings.py file and update zappa with
run the following code on your terminal:
zappa update dev
```

#### CReate RDS database
```
Select the option "Free Usage Tier" 

Choose PostgreSQL

DB instance identifier: zapdjangodb

Master username: your username

Master password: your password

Confirm password: your password

Click "Create database"

Look for the following settings:
    - VPC 
    - Security groups
    - Subnets

Add Inbound Rule to Security Group
    - Once the database is created go to the database and find "Security group rules"
    - click on the security group
    - click on inbound rules and edit
    - click Add Rule
    - click dropdown (current value is likely Custom TCP Rule), select PostgreSQL
    - Change source to match your security group

Update your dajngo settings data base
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'zapdjangodb',
            'USER': your username,
            'PASSWORD': your password,
            'HOST': your host (you can fin it when on aws you open your database in the option "Connectivity & security" Endpoint),
            'PORT': your port (you can fin it when on aws you open your database in the option "Connectivity & security" port),
        }
    }
```

#### Add the Security Group to LambdaAdd the Security Group to Lambda
```
Go to AWS lambda and find the function that zappa created

Click on Configuration

In the left panel find VPC

Select the VPC of your RDS DB (done above)
Add your Subnets (again from above)
In Security groups be sure to use the same value as your Security groups above.
```

#### Update zappa_settings.json
```
{
    "dev": {
        "aws_region": "us-west-2",
        "django_settings": "zapdj.settings",
        "profile_name": "default",
        "project_name": "zappacfe",
        "runtime": "python3.6",
        "s3_bucket": "my-awesome-zappa-bucket",
        "timeout_seconds": 900,
        "manage_roles": false,
        "role_name": "ZappaDjangoRole",
        "role_arn": "arn:aws:iam::123456:role/ZappaDjangoRole",
        "vpc_config" : {
            "SubnetIds": ["your subnet ind", "your subnet ind"],
            "SecurityGroupIds": [ "your security group" ]
        }
    }
}

run the following code in your terminal

zappa update dev
python manage.py makemigrations
zappa update dev
zappa manage dev migrate
```