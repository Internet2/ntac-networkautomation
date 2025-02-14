
# Playbook `network-opennms.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-opennms)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-opennms.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-opennms.yml)


## Play OpenNMS Network Device Provisioning

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `vlan_area_lab:qa:wa-*`
- Tags: ['opennms_config']

OpenNMS PoC Provisioning from Netbox Devices

NB: Run once for all hosts in play
https://www.reddit.com/r/ansible/comments/t62fia/group_vars_with_a_lookup_does_that_lookup_happen/
https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_delegation.html#id5

Using GraphQL API in Netbox to query all IPv4/IPv6 addresses assigned to interfaces
which is substantially faster than using the REST API which gathers and joins much
more data using the Django ORM than we need, leading to poor performance.

Adding Netbox Sites lat/long data will allow OpenNMS Nodes to be provisioned on the map display

NB: number of uWSGI workers on Netbox app server limits concurrency of provisioning queries

An Ansible inventory which is limited to NS Techlab hosts is expected for this playbook as it
sets additional inventory parameters such as `netbox_id` which is used in the OpenNMS Provisioning
requisition as the Foreign ID number to link the two systems Device/Node records bi-directionally.
We prefix the `foreign_id` with `Device-` or `VM-` as those are two different record types
in Netbox and may have overlapping row ID numbers.

FIXME: move variables from play-local to `hosts.yml` inventory file, including `device_family` expression which is more extensive than other playbooks


### Tasks OpenNMS Network Device Provisioning

- Get Physical Addresses from Netbox (Tags: ['opennms_config'] []) Make one API call to Netbox for Sites, not one per Ansible manged device `run_once: true`
- Get Netbox IPs from GraphQL for Multi-IP Devices (Tags: ['opennms_config'] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `requisition in ['Routers', 'Servers', 'WirelessController', 'Firewalls', 'LoadBalancer']`) All the magic happens in `tasks/netbox-multiip-tasks.yml`
- Create Node records in OpenNMS Requisition API (Tags: ['opennms_config'] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `netbox_id is defined and foreign_id is defined`) 
  Skip records which don't have Netbox inventory
  
  NB: requisitions responds with 202 Accepted when adding new nodes
  
  Don't require two requests for each request (401 then 202)
  
  NB: can't just use ID numbers because Device and VM each have their own records
  
  FIXME: For firewalls where IP autodetection doesn't work, add list of IPs for all interfaces on primary and standalone devices.
         with ICMP service monitoring
  
  Adding OpenNMS asset fields with the street address from Netbox Site data will allow
  the built-in OpenStreetMap or Google Maps API lookups to convert to lat/long, but
  the free OSM lookup service doesn't seem to have many campus locations defined and
  the Google Maps API service requires a paid subscription to use, which we did not
  bother with for the PoC.
  
  All the magic happens in `templates/opennms/opennms_interfaces.yml.j2`
  
  OpenNMS Nodes are tagged with catagories including Requisition name, device family, platform family
  and Ansible groups (which include Site, Platform, Tags, etc.)
  
  This runs in parallel for each node being provisioned and POSTs using the `uri` module to OpenNMS API
  
- Synchronize OpenNMS Requisition making changes active (Tags: ['opennms_config'] []) Reload each requisition one time not once per Ansible managed device being provisioned `run_once: true`
