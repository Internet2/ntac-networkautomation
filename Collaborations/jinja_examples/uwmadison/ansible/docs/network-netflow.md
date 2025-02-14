
# Playbook `network-netflow.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-netflow)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-netflow.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-netflow.yml)


## Play IOS Netflow Enable

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `r-*`
- Tags: []

EXPERIMENTAL configuration of NetFlow in QA for OpenNMS PoC testing


### Tasks IOS Netflow Enable

- Get Config from NetCMS (Tags: [] [])
- Enable Netflow (Tags: [] []) (Notify: `copy running-config startup-config`)
- Check Netflow Exporters (Tags: [] []) (Notify: `copy running-config startup-config`) This doesn't work unless we explicitly remove existing entries, which means parsing config, no way to replace config sections in IOS-XE

### Handlers IOS Netflow Enable

- copy running-config startup-config 
- NetCMS Check-in 

## Play NXOS Netflow Enable

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `device_roles_core:device_roles_node:&rn-*`
- Tags: []

EXPERIMENTAL configuration of NetFlow in QA for OpenNMS PoC testing

SSH auto-enabled via RADIUS and Ansible tries to detect the status using
"show feature privilege" which doesn't exist in NXOS VDC in the lab,
breaking the playbook.  We can ignore this as we are already privileged
If we need this then look in net_user for the ae=0|1 attribute from devinfo


### Tasks NXOS Netflow Enable

- Get Config from NetCMS (Tags: [] [])
- Enable Netflow on BGP routers (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'feature bgp' in ansible_net_config`)
  - Enable Netflow (Tags: [] [] []) (Notify: `copy running-config startup-config`)
  - Netflow Record (Tags: [] [] []) (Notify: `copy running-config startup-config`)
  - Netflow Exporters (Tags: [] [] []) (Notify: `copy running-config startup-config`)
  - Netflow Monitor (Tags: [] [] []) (Notify: `copy running-config startup-config`)
  - Netflow Sampler (Tags: [] [] []) (Notify: `copy running-config startup-config`)
  - Enable Netflow Interfaces (Tags: [] [] []) (Notify: `copy running-config startup-config`) Query interfaces on target device where custom filed `enable_netflow` is true on the Netbox Interface

### Handlers NXOS Netflow Enable

- copy running-config startup-config 
- NetCMS Check-in 
