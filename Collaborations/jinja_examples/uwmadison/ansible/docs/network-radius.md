
# Playbook `network-radius.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-radius)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-radius.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-radius.yml)


## Play IOS AAA RADIUS

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `s-*:r-*:t-*:VG-*`
- Tags: []

## Network Device RADIUS AAA Remote Access configuration management

The `network-radius.yml` playbook will configure RADIUS, SSH and AAA (Authentication, Authorization, Audit)
settings on the Catalyst platform running IOS `12.2(58)`+ and IOS-XE in support of upgrading
Catalyst 3750X and E models to IOS `15.2` and to provide a long-term ability to deploy and audit
the configuration of remote access on this platform.  This playbook is included
as the first step in the `network-firmware-staging.yml` playbook to ensure devices continue
to have a functional RADIUS configuration after upgrading to `15.2` or newer.

### Netbox

Netbox Configuration Contexts are used
to associate RADIUS server IPs to the Device based on whether the device is
[managed in-band](https://netbox.net.wisc.edu/extras/config-contexts/6/)
or is on the [OOB (Out-of-Band) network](https://netbox.net.wisc.edu/extras/config-contexts/9/)
based on the presense of a [`mgmt_OOB`](https://netbox.net.wisc.edu/extras/tags/9/) tag
on the Netbox Device record, the in-band Config Context having a weight of 1000 and
the OOB Config Context having a weight of 2000 to override it.  If a new set of RADIUS
IPs need to be added then a new Config Context would need to be created and associated
with the following properties of a Device record (Region, Site Group, Site, Device Type, Role,
Platform, Cluster Group, Cluster, Tenant Group, Tenant or Tag) with a higher priority than
the default.

```json
{
    "radius_doit_ns": [
        {
            "ipv4": "146.151.144.37",
            "name": "netcms1"
        },
        {
            "ipv4": "146.151.144.38",
            "name": "netcms2"
        }
    ]
}
```

### DevInfo

The `/usr/local/ns/bin/devinfo` utility from
[ns-utils-common-bin](https://git.doit.wisc.edu/NS/ns-utils-common-bin) is used
to query entries in our credential vault `/usr/local/ns/etc/devinforc`
used by DoIT Network Services device management applications.  There is an entry
for `radius` which has the cleartext shared secret as the password and the
type 7 encoded shared secret as the enable_password.

```
# Regex : Username : Password : Enable Password : Service : Attributes
radius:radius:password:type7encoded:radius:
```

The `devinfo` CLI tool has a `-j` JSON mode which allows it to be used with Ansible,
reading the data in using a jinja filter.

```yaml
radius_secret: "{{ lookup('pipe', '/usr/local/ns/bin/devinfo -j radius') | from_json }}"
```

```json
"radius_secret": {
  "connection_method": "radius",
  "password": "<password>",
  "enable_password": "<type7encoded>",
  "attributes": {},
  "username": "radius"
}
```

This same mechanism is used to retrieve the `net` credential in the NetCMS getcnf
suite of tools and is used by the Ansible playbook to retrieve login credentials
for its `network_cli` connection in the `net_user` variable.  Should one need to
run the playbook against a device which has broken remote authentication using
the `emerg` account one only need change the account information the playbook uses
to authenticate, then the playbook can be used to repair the remote authentication config.

```yaml
    net_user: "{{ lookup('pipe', '/usr/local/ns/bin/devinfo -j ' + inventory_hostname) | from_json }}"
    # net_user: "{{ lookup('pipe', '/usr/local/ns/bin/devinfo -j emergency-' + inventory_hostname) | from_json }}"
    ansible_user: "{{ net_user.username }}"
    ansible_password: "{{ net_user.password }}"
    ansible_become_password: "{{ net_user.enable_password }}"
    emergency_user: "{{ lookup('pipe', '/usr/local/ns/bin/devinfo -j emergency') | from_json }}"
```

### Ansible

The Ansible playbook applies to `s-*:r-*` devices to only operate on IOS and IOS-XE
devices running `12.2(58)` and newer which use the came configuration syntax for AAA using
[ios_facts](https://docs.ansible.com/ansible/latest/collections/cisco/ios/ios_facts_module.html)
to get the current version of the device and making the change using
[ios_config](https://docs.ansible.com/ansible/latest/collections/cisco/ios/ios_config_module.html)
with the current configuration retrieved from NetCMS using RCS rather than using `ios_facts`
to fetch the running config and passed to the `ios_config` module for comparison,
so it only attempts to make changes when the checked-in device config shows a difference
from our standard config encoded in the playbook.
[ios_command](https://docs.ansible.com/ansible/latest/collections/cisco/ios/ios_command_module.html)
is then used to `write memory` and the configuration change checked into NetCMS automatically
if something has changed.

* Retrieve RADIUS shared secret from `/usr/local/ns/etc/devinforc`
* Parse `show version` and related commands using [ios_facts](https://docs.ansible.com/ansible/latest/collections/cisco/ios/ios_facts_module.html)
* Get the current configuration from NetCMS RCS `ansible_net_config: "{{ lookup('pipe', '/usr/bin/co -q -p /home/net/cms/' + inventory_hostname + '.conf') }}"`
  * Only proceed `when: "'12.2(58)' in ansible_net_version or ansible_net_version is version('15', 'gt') or ansible_net_version is version('4', 'lt')"` if the device is running IOS `12.2(58).x` or IOS/IOS-XE `15`+ or IOS-XE `3.x` (less than 4)
  * Remove `radius-server host <ip>` and `radius-server key` from global-level config stanza if it exists as this is not supported on IOS/IOS-XE 15+.
  * Remove old-style ` server <ip> ` group definitions from `aaa group server radius RAD_SERVERS` group if they exist in favor of named RADIUS server definitions
  * Configure named `radius server {{ name }}` definitions with the ipv4 address from Netbox Configuration Context `radius_doit_ns` and `radius_secret.enable_password` from devinfo
  * Configure global `radius-server` retransmit and timeout values
  * Configure `aaa group server radius RAD_SERVERS` group using the named `radius server {{ name }}` definitions
  * Configure `aaa new-model` authentication, authorization and accounting to default to remote auth using the `RAD_SERVERS` group then local
  * Configure `login` delay and failure/success logging
  * Configure `ip ssh` timeout retries and version
* If any of these configuration statements required a change then `write memory` and use the NetCMS Makefile to perform a `make {{ inventory_hostname }}.update` to check in the config change, once at the end.

The actual lines of templated config are included in the playbook, if they need
to be changed then they can be changed in the playbook, if different
devices need different config statements, for timeout or retry or some other value,
then a new Netbox Config Context can be created to contain that info and associated
with the appropriate devices, or added to the existing Config Context or some other
mechanism in the playbook, depending on the nature of the change.

If a device does not have a working remote authentication configuration but
does have an `emerg` local account and is network accessible then the credentials
the playbook uses to authenticate the device from `devinfo` can be changed
to use emergency access and the remote authentication configuration repaired by
the playbook.



### Tasks IOS AAA RADIUS

- Set ansible_net_config (Tags: [] [])
  - Get Config from NetCMS (Tags: [] [] [])
  - Enable NetCMS Check-in (Tags: [] [] [])
  - Get Minimal Facts (Tags: [] [] [])
  - Disable NetCMS Check-in
  - Get Facts from live device
  - Show Facts from device (hostname, model, image, version)
- RADIUS Config on IOS 12.2(58)+ and IOS-XE (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'12.2(58)' in ansible_net_version or ansible_net_version is version('15', 'gt') or ansible_net_version is version('4', 'lt')`)
  - Remove old global RADIUS Key syntax (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'12.2(58)' in ansible_net_version or ansible_net_version is version('15', 'gt') or ansible_net_version is version('4', 'lt')` AND `'radius-server key ' in ansible_net_config`) (Notify: `copy running-config startup-config`)
  - Remove old RADIUS Server syntax (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'12.2(58)' in ansible_net_version or ansible_net_version is version('15', 'gt') or ansible_net_version is version('4', 'lt')` AND `'radius-server host ' in ansible_net_config and '12.2(58)' in ansible_net_version`) (Notify: `copy running-config startup-config`)
  - Remove old RADIUS Server group syntax (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'12.2(58)' in ansible_net_version or ansible_net_version is version('15', 'gt') or ansible_net_version is version('4', 'lt')` AND `' server ' + config_context[0].radius_doit_ns[0].ipv4 in ansible_net_config or ' server ' + config_context[0].radius_doit_ns[1].ipv4 in ansible_net_config`) (Notify: `copy running-config startup-config`)
  - AAA RADIUS Servers (Tags: [] [] []) (Notify: `copy running-config startup-config`)
  - AAA RADIUS Global Config (Tags: [] [] []) (Notify: `copy running-config startup-config`)
  - AAA RAD_SERVERS Group (Tags: [] [] []) (Notify: `copy running-config startup-config`)
  - AAA AuthN AuthZ Accounting (Tags: [] [] []) (Notify: `copy running-config startup-config`)
  - AuthN Logging (Tags: [] [] []) (Notify: `copy running-config startup-config`)
  - SSH Access (Tags: [] [] []) (Notify: `copy running-config startup-config`)

### Handlers IOS AAA RADIUS

- copy running-config startup-config  ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `not ansible_check_mode`)
- NetCMS Check-in  ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `not ansible_check_mode and netcms_enabled`)
