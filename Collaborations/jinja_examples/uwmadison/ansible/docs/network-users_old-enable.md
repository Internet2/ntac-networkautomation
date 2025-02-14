
# Playbook `network-users_old-enable.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-users_old-enable)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-users_old-enable.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-users_old-enable.yml)


## Play IOS Local Users

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `s-*:r-*:t-*`
- Tags: []



### Tasks IOS Local Users

- Get Facts (Tags: [] [])
- Enable Secret IOS 15.x (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version is version('15','ge') or ansible_net_version is version('4', 'lt')`) (Notify: `copy running-config startup-config`)
- Enable Secret IOS 12.x (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version is version('15','lt') and ansible_net_version is version('4', 'gt')`) (Notify: `copy running-config startup-config`)
- Local User Account (emerg with type8 secret) IOS 15.x (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version is version('15','ge') or ansible_net_version is version('4', 'lt')`) (Notify: `copy running-config startup-config`)
- Local User Account (emerg with type5 secret) IOS 12.x (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version is version('15','lt') and ansible_net_version is version('4', 'gt')`) (Notify: `copy running-config startup-config`)
- init cms checking and add E911 (Tags: [] [])

### Handlers IOS Local Users

- copy running-config startup-config 
- NetCMS Check-in 
