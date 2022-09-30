# This code accepts explicit vpc credentials but can also utilize IAM roles. 
# If IAM roles are not used you need to specify them either in a pillar file or in the minion's config file
# It's also possible to specify key, keyid and region via a profile, either passed in as a dict, or as a string to pull from pillars or minion config:

# NOT SURE ABOUT "Ensure ___ exists vs Create ____ I'VE SEEN BOTH

# === HELPFUL RESOURCES === 
# * https://docs.saltproject.io/en/latest/ref/states/all/salt.states.boto_vpc.html
# * https://github.com/saltstack-formulas/aws-formula/blob/master/pillar.example
# * https://stackoverflow.com/questions/39999980/create-full-vpc-using-salt-stack-and-boto-vpc
# * https://salt-users.narkive.com/rmrnuVuW/create-vpc-using-salt
# * https://sixfeetup.com/blog/build-aws-vpc-with-saltstack

# ---------------------------------------------CREATE VPC, SUBNET, ROUTE TABLE, GATEWAYS, AND ROUTE TABLE-----------------------------------------------

# EACH OF THESE STATE MODELS WILL ACCEPT EITHER vpc_name OR vpc_id

# CREATES VPC
Ensure VPC exists:
  boto_vpc.present:
    - name: myvpc
    - cidr_block: 10.10.11.0/24
    - dns_hostnames: True
    - region: us-east-1
    - keyid: GKTADJGHEIQSXMKKRBJ08H
    - key: askdjghsdfjkghWupUjasdflkdfklgjsdfjajkghs

# CREATES SUBNET
Ensure subnet exists:
  boto_vpc.subnet_present:
    - name: mysubnet
    - vpc_id: vpc-123456
    - cidr_block: 10.0.0.0/16
    - region: us-east-1
    - profile: myprofile

# CREATES INTERNET GATEWAY
{% set profile = salt['pillar.get']('aws:region:us-east-1:profile' ) %}
Ensure internet gateway exists:
  boto_vpc.internet_gateway_present:
    - name: myigw
    - vpc_name: myvpc
    - profile: {{ profile }}

# CREATES ROUTE TABLE
Ensure route table exists:
  boto_vpc.route_table_present:
    - name: my_route_table
    - vpc_id: vpc-123456
    - routes:
      - destination_cidr_block: 0.0.0.0/0
        instance_id: i-123456
      - subnet_names:
        - subnet1
        - subnet2
      - region: us-east-1
      - profile:
        keyid: GKTADJGHEIQSXMKKRBJ08H
        key: askdjghsdfjkghWupUjasdflkdfklgjsdfjajkghs
          
# CREATES NAT GATEWAY
Ensure nat gateway exists:
  boto_vpc.nat_gateway_present:
  - subnet_name: mysubnet
  - allocation_id:  #If specified, the elastic IP address referenced by the ID is associated with the gateway. Or a new allocation_id is created and used.
  - region: us-east-1  
  - profile:
    keyid: GKTADJGHEIQSXMKKRBJ08H
    key: askdjghsdfjkghWupUjasdflkdfklgjsdfjajkghs 
          
# -----------------------------------------CREATE SUBNET, GATEWAY, AND ROUTE TABLE W/ ENV VARIABLES-----------------------------------------------

# ENVIRONMENT VARIABLES
{% set custom_vpc_name = 'dlab-new' %}
{% set custom_keyid = keyid %}
{% set custom_key = key %}
{% set custom_region = 'us-east-1' %}
{% set cidr_block = '10.0.0.1/24' %}
{% set instance_id = 'i-123456' %}

{% set create_vpc = salt.boto_vpc.create(vpc_name=custom_vpc_name,cidr_block=cidr_block,enable_dns_hostnames=True,region=custom_region,keyid=custom_keyid,key=custom_key) %}


# THIS LINE USES boto_vpc execution module AND get_id function WHICH WILL RETURN VPC id IF MATCH IS FOUND 
{% set vpc_id = salt.boto_vpc.get_id(name=custom_vpc_name, region=custom_region, keyid=custom_keyid, key=custom_key)['id'] %}

# CREATES VPC
 Create VPC:
    boto_vpc.present:
        - name: {{ custom_vpc_name }}
        - cidr_block: {{ cidr_block }}
        - dns_hostnames: True
        - region: {{ custom_region }}
        - keyid: {{ custom_keyid }}
        - key: {{ custom_key }}

# CREATES SUBNET
Create subnet:
  boto_vpc.subnet_present:
    - name: {{ custom_vpc_name }}-subnet
    - vpc_id: {{ vpc_id }}
    - cidr_block: {{ cidr_block }}
    - region: {{ custom_region }}
    - keyid: {{ custom_keyid }}
    - key: {{ custom_key }}

Create internet gateway:
  boto_vpc.internet_gateway_present:
    - name: {{ custom_vpc_name }}-igw
    - vpc_id: {{ vpc_id }} # I have changed this line from vpc_name into vpc_id, is that what you meant ?
    - keyid: {{ custom_keyid }}
    - key: {{ custom_key }}

Create route:
  boto_vpc.route_table_present:
    - name: my_route_table
    - vpc_id: {{ vpc_id }}
    - routes:
        - destination_cidr_block: {{ cidr_block }}
          instance_id: {{ instance_id }}
    - subnet_names:
        - {{ custom_vpc_name }}-subnet
    - region: {{ custom_region }}
    - profile:
        keyid: {{ custom_keyid }}
        key: {{ custom_key }}
          
# CREATES NAT GATEWAY
Ensure nat gateway exists:
  boto_vpc.nat_gateway_present:
  - subnet_name: 
      - {{ custom_vpc_name }}-subnet
  - allocation_id:  #If specified, the elastic IP address referenced by the ID is associated with the gateway. Or a new allocation_id is created and used.
  - region: {{ custom_region }}
  - profile:
       keyid: {{ custom_keyid }}
       key: {{ custom_key }}
