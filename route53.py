instance1.example.com:
boto_route53.present:
- name: instance1.example.com.
- value: {{ grains['ec2']['public_ipv4'] }}
- zone: example.com.
- ttl: 7200
- record_type: A
- region: universal

#https://salt-users.narkive.com/XBeBcMPB/boto-route53-present-region
