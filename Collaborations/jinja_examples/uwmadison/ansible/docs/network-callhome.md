
# Playbook `network-callhome.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-callhome)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-callhome.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-callhome.yml)


## Play IOS-XE Smart Licensing Call-Home proxy config

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `s-*:r-*:t-*:VG-*:&ios_17`
- Tags: []

Set HTTP proxy config if Smart Licensing requires it as managed network devices ACLs
prevent direct access to/from the Internet.

FIXME: migrate playbook-local variables to shared `hosts.yml` to reduce duplication

### Example Ansible Inventory
```yaml
all:
  vars:
    ansible_network_import_modules: true
    ansible_host_key_auto_add: true
    ansible_host_key_checking: false
    net_user: "{{ lookup('pipe', '/usr/local/ns/bin/devinfo -j ' + inventory_hostname) | from_json }}"
    emergency_user: "{{ lookup('pipe', '/usr/local/ns/bin/devinfo -j emergency') | from_json }}"
    cms_service_ipv4: "192.0.2.101"
    cms_service_ipv6: "2001:db6::101"
  children:
    test:
      vars:
        cms_service_ipv4: "192.168.42.21"
        cms_service_ipv6: ""
    qa:
      vars:
        cms_service_ipv4: "146.151.144.26"
        cms_service_ipv6: "2607:f388:2:2000::1038"
    ios_17:
      children:
        # Inherited from Netbox inventory Device record Platform field.
        platforms_iosxe_bengaluru_17_06_03:
        platforms_iosxe_bengaluru_17_06_05:
        platforms_iosxe_17_6_5:
        platforms_iosxe_cupertino_17_09_03:
        platforms_iosxe_dublin_17_12_02:
        platforms_iosxe_dublin_17_12_03:
      vars:
        # ansible_private_key_file: "/home/net/.ssh/id_rsa.pub"
        # ansible_net_ssh_keyfile: "/home/net/.ssh/id_rsa.pub"
        # Ansible collection ansible.netcommon and cisco.ios
        ansible_network_os: "cisco.ios.ios"
        # ansible_network_cli_ssh_type: libssh
        # ansible_network_cli_ssh_type: paramiko
        ansible_command_timeout: 300
        ansible_connect_timeout: 300
        ansible_user: "{{ net_user.username }}"
        ansible_password: "{{ net_user.password }}"
        ansible_become_password: "{{ net_user.enable_password }}"
```


### Tasks IOS-XE Smart Licensing Call-Home proxy config

- Set ansible_net_config (Tags: [] [])
  - Get Config from NetCMS (Tags: [] [] [])
  - Get Minimal Facts (Tags: [] [] [])
  - Disable NetCMS Check-in
  - Get Facts from live device
  - Show Facts from device (hostname, model, image, version)
- HTTP client proxy-server (Tags: [] []) (Notify: `copy running-config startup-config`)
- Call-Home http-proxy (Tags: [] []) (Notify: `copy running-config startup-config`)

### Handlers IOS-XE Smart Licensing Call-Home proxy config

- copy running-config startup-config  ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `not ansible_check_mode`)
- NetCMS Check-in  ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `not ansible_check_mode and netcms_enabled`)
