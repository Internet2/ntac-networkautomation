
# Playbook `network-nohttpserv.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-nohttpserv)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-nohttpserv.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-nohttpserv.yml)


## Play IOS Management Services

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `s-*:r-*:t-*:VG-*`
- Tags: []

Audit that `ip http` is *NOT* enabled on managed IOS/IOS-XE devices
as the factory default has a web interface enabled which could accidently
be left on, an unnecessary risk

FIXME: move variables from play-local to `hosts.yml` inventory file


### Tasks IOS Management Services

- Set ansible_net_config (Tags: [] [])
  - Get Config from NetCMS (Tags: [] [] [])
  - Get Minimal Facts (Tags: [] [] [])
  - Disable NetCMS Check-in
  - Get Facts from live device
  - Show Facts from device (hostname, model, image, version)
- Disable web-based management (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'ip http server' in ansible_net_config or 'ip http secure-server' in ansible_net_config`) (Notify: `copy running-config startup-config`)
- Disable Smart Install (vstack) (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `item.startswith('ios-12-255') or item.startswith('ios-12-258')`) (Notify: `copy running-config startup-config`) `when: "ansible_net_version is version('15', 'lt')"` is not necessary as
  there are only a handful of legacy devices in service even capable of this (risky) feature.
  
  Smartinstall `no vstack` command appears in IOS 12.2(55)
  and smartinstall is removed from IOS 15.x IOS-XE 16.x versions
  that we have deployed so we only need to check limited legacy versions
  https://www.cisco.com/c/en/us/td/docs/switches/lan/smart_install/configuration/guide/smart_install/supported_devices.html#43328
  
  This is created as a list by nb_inventory even though it is only one item
  

### Handlers IOS Management Services

- copy running-config startup-config 
- NetCMS Check-in 
