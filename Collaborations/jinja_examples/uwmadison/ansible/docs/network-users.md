
# Playbook `network-users.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-users)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-users.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-users.yml)


## Play IOS Local Users

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `s-*:r-*:t-*:VG-*`
- Tags: []

## Network Device local account emergency credential management

The `network-users.yml` playbook will configure local `emerg` account and
`enable` credential using the most secure password hash encoding availble
on Catalyst family devices (type 5 MD5 for IOS 12.x and type 8 PBKDF2 for
IOS 15.x and IOS-XE) with the cleartext and password hashes in all relevant
formats stored in the DoIT Network Service credential vault `/usr/local/ns/etc/devinforc`.
This playbok is included as the last step in the `network-firmware-reload.yml`
playbook to upgrade the local password hashes after firmware updates, and could
be used independantly to push out mass updates for the local credentials
should they ever need to be updated.


### DevInfo

The `/usr/local/ns/bin/devinfo` utility from
[ns-utils-common-bin](https://git.doit.wisc.edu/NS/ns-utils-common-bin) is used
to query entries in our credential vault `/usr/local/ns/etc/devinforc`
used by DoIT Network Services device management applications.  There is an entry
for `emergency` and `enable` which has the cleartext password and the type 8 hashed
password as the enable_password, with type 5, type 7 and type 8 versions of the
credential as attriutes.

```
# Regex : Username : Password : Enable Password : Service : Attributes
emergency:emerg:password:type8hash:ssh:type7hash=<encoded_password>,type5hash=<hashed_password>,type8hash=<hashed_password>
```

The `devinfo` CLI tool has a `-j` JSON mode which allows it to be used with Ansible,
reading the data in using a jinja filter.

```yaml
    emergency_user: "{{ lookup('pipe', '/usr/local/ns/bin/devinfo -j emergency') | from_json }}"
    enable_secret: "{{ lookup('pipe', '/usr/local/ns/bin/devinfo -j enable') | from_json }}"
```

```json
"emergency_user": {
  "connection_method": "ssh",
  "password": "<password>",
  "enable_password": "<type8hash>",
  "attributes": {
    "type5hash": "<type5hash>",
    "type7hash": "<type7hash>",
    "type8hash": "<type8hash>"
  },
  "username": "emerg"
}
```

### Ansible

The Ansible playbok applies to `s-*:r-*` devices to only operate on Catalyst family
devices running IOS and IOS-XE and uses
[ios_facts](https://docs.ansible.com/ansible/latest/collections/cisco/ios/ios_facts_module.html)
to get the current version and determine which password hash format to use (type 5 or type 8) and
make the change using
[ios_config](https://docs.ansible.com/ansible/latest/collections/cisco/ios/ios_config_module.html)
with the current configuration retrieved from NetCMS using RCS rather than using `ios_facts`
to fetch the running config and passed to the `ios_config` module for comparison,
so it only attempts to make changes when the checked-in device config shows a difference
from our standard config encoded in the playbook.
[ios_command](https://docs.ansible.com/ansible/latest/collections/cisco/ios/ios_command_module.html)
is then used to `write memory` and the configuration change checked into NetCMS automatically
if something has changed.


* Retrieve `emergency_user` and `enable_secret` credentials from `/usr/local/ns/etc/devinforc`
* Parse `show version` and related commands using [ios_facts](https://docs.ansible.com/ansible/latest/collections/cisco/ios/ios_facts_module.html)
* Get the current configuration from NetCMS RCS `ansible_net_config`
* Configure the `enable` secret, on IOS 12.x use the type 5 hash, on IOS 15.x+ (IOS-XE) the type 8 hash.  Existing config needs to be removed to convert from type 7 `password` to type 5 or 8 `secret`.
* Configure a local `username emerg privilege 15 secret (5|8) <hash>` account, on IOS 12.x use the type 5 hash, on IOS 15.x+ (IOS-XE) the type 8 hash.  Existing account needs to be removed to convert from type 7 `password` to type 5 or 8 `secret`.
* If any of these configuration statements required a change then `write memory` and use the NetCMS Makefile to perform a `make {{ inventory_hostname }}.update` to check in the config change, once at the end.

This playbook is fairly straight forward and may be a good resource for training.

### Tasks IOS Local Users

- Set ansible_net_config (Tags: [] [])
  - Get Config from NetCMS (Tags: [] [] [])
  - Enable NetCMS Check-in (Tags: [] [] [])
  - Disable NetCMS Check-in
  - Get Facts from live device
  - Show Facts from device (hostname, model, image, version)
- Enable Secret IOS (Tags: [] []) (Notify: `copy running-config startup-config`)
- Local User Account (ios_config) (Tags: [] []) (Notify: `copy running-config startup-config`)
- Parse users from IOS config (Tags: [] [])
- check mode user verification (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_check_mode and item is defined and item.name not in ios_user_list and item.name != 'emerg'`)
- Remove defunct IOS Local User Accounts (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `not ansible_check_mode and item is defined and item.name not in ios_user_list and item.name != 'emerg'`) (Notify: `copy running-config startup-config`)
- Remove defunct IOS Local User Accounts second pass (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `not ansible_check_mode and item is defined and item.name not in ios_user_list and item.name != 'emerg'`) (Notify: `copy running-config startup-config`)

### Handlers IOS Local Users

- copy running-config startup-config  ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `not ansible_check_mode`)
- NetCMS Check-in  ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `not ansible_check_mode and netcms_enabled`)

## Play NXOS Local Users

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `sn-*:rn-*`
- Tags: []



### Tasks NXOS Local Users

- Get Config from NetCMS (Tags: [] [])
- Parse users from NXOS config (Tags: [] [])
- remove baddies (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `item.name not in nxos_user_list`) (Notify: `copy running-config startup-config`)
- Local User Accounts Mangement VDC (nxos_config) (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'system admin-vdc' in ansible_net_config and not 'no system admin-vdc' in ansible_net_config`) (Notify: `copy running-config startup-config`)
- Local User Accounts Athletics Mangement VDC (nxos_config) (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'no system admin-vdc' in ansible_net_config`) (Notify: `copy running-config startup-config`)
- Local User Accounts Guest VDC (nxos_config) (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'tags_mgmt_vdc' in group_names`) (Notify: `copy running-config startup-config`)
- Local User Accounts (nxos_config) (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'tags_mgmt_vdc' not in group_names and 'system admin-vdc' not in ansible_net_config`) (Notify: `copy running-config startup-config`)

### Handlers NXOS Local Users

- copy running-config startup-config  ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `not ansible_check_mode`)
- NetCMS Check-in  ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `not ansible_check_mode`)

## Play PaloAlto Local Users

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `fp-*:mp-*`
- Tags: []



### Tasks PaloAlto Local Users

- Local User Accounts (Tags: [] []) (Notify: `commit panos config`)

### Handlers PaloAlto Local Users

- commit panos config
