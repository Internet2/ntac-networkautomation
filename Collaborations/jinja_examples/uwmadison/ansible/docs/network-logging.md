
# Playbook `network-logging.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-logging)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-logging.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-logging.yml)


## Play IOS Config Logging

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `s-*:r-*:t-*:VG-*`
- Tags: []

Ensure logging is configured according to standard on requested devices

```yaml
parents:
  - archive
  - log config
lines:
  - logging enable
  - logging size 500
  - notify syslog contenttype plaintext
  - hidekeys
```

FIXME: move variables from play-local to `hosts.yml` inventory file


### Tasks IOS Config Logging

- Set ansible_net_config (Tags: [] [])
  - Get Config from NetCMS (Tags: [] [] [])
  - Get Minimal Facts (Tags: [] [] [])
  - Disable NetCMS Check-in
  - Get Facts from live device
  - Show Facts from device (hostname, model, image, version)
- Debug ansible_net_version (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_iostype == 'IOS-XE'`)
- Enable logging cli commands v < 17 (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_iostype == 'IOS-XE' and ansible_net_version is version('15', 'gt') and ansible_net_version is version('17', 'lt')`) (Notify: `copy running-config startup-config`)
- Enable logging cli commands v >= 17 (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_iostype == 'IOS-XE' and ansible_net_version is version('15', 'gt') and ansible_net_version is version('17', 'ge')`) (Notify: `copy running-config startup-config`)

### Handlers IOS Config Logging

- copy running-config startup-config  ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `not ansible_check_mode`)
- NetCMS Check-in  ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `not ansible_check_mode and netcms_enabled`)
