
# Playbook `network-vty.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-vty)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-vty.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-vty.yml)


## Play IOS VTY

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `s-*:r-*:t-*:VG-*`
- Tags: []

Audit IOS VTY to ensure all have ACLs defined

Newer IOS/IOS-XE firmware may pre-configure additional VTY instances by default
which could end up without an ACL

IOS configuration for VTYs is based on ranges so this playbook uses `when:`
statements for the most common ranges so config only applies if those stansas
already exist.  If we have a device with a different `line vty # #` range
then we'd have to add it as it wouldn't be detected without adding a bunch
of parsing logic which we didn't take the time to do when this was created.


### Tasks IOS VTY

- Set ansible_net_config (Tags: [] [])
  - Get Config from NetCMS (Tags: [] [] [])
  - Get Minimal Facts (Tags: [] [] [])
  - Disable NetCMS Check-in
  - Get Facts from live device
  - Show Facts from device (hostname, model, image, version)
- Configure Console stanza (Tags: [] []) (Notify: `copy running-config startup-config`)
- Configure VTY stanza lines 0-4 (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'line vty 0 4' in ansible_net_config`) (Notify: `copy running-config startup-config`)
- Configure VTY stanza lines 5-15 (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'line vty 5 15' in ansible_net_config`) (Notify: `copy running-config startup-config`)
- Configure VTY stanza lines 16-31 (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'line vty 16 31' in ansible_net_config`) (Notify: `copy running-config startup-config`)
- Configure VTY stanza lines 5-31 (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'line vty 5 31' in ansible_net_config`) (Notify: `copy running-config startup-config`)

### Handlers IOS VTY

- copy running-config startup-config  ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `not ansible_check_mode`)
- NetCMS Check-in  ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `not ansible_check_mode and netcms_enabled`)
