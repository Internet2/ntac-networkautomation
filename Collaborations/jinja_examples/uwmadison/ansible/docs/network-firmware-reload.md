
# Playbook `network-firmware-reload.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-firmware-reload)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-firmware-reload.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-firmware-reload.yml)


## Play Catalyst IOS Reboot devices with newer installed firmware

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `s-*:r-*`
- Tags: []

Reboot IOS into new Firmware after staging

Further documentation is found in [network-firmware](network-firmware.md) playbook

Uses `vars_prompt` to allow configuring a future time to reload at to support tight maintenance windows

Also contains a jinja filter expression which parses the device name to determine if the position_number
is even or odd, so that batches of non-HA devices can have staggered reboots which may improve
availability of downstream devices in some limited circumstances.  Mostly provided as an example as
this hasn't been used in production.

Hosts default to `doit_needsreboot: false` and become eligible for reboot if the installed OS is newer
than the currently booted OS.

Batches of explicit hosts can be created by passing a file with a list of devices names (one per line)
using `--limit @filename`

To prevent a failed deployment from bricking a larger number of devices than our field services can handle
we serialize this play in an initial batch of *50* devices with a `max_fail_percentage: 20` which means
that if 10 or more devices fail to complete the first batch the playbook run fails.  Subsequent batches
are in groups of 100 devices at a time, with failure of 20 or more in a single batch failing the playbook.
Tuning the batch sizes and permissable failure percentage between the competing interests of completing
a disruptive change quickly (more parallelization), or the risk of a bad firmware not visible in testing
creating unmanagable disruption, is always open for debate among the network engineers.

Each platform and version has its own command structure for checking and updating firmware
between IOS and IOS-XE 3.x, 15.x, 16.x, 17.x and between hardware platforms like Cat3xxx/4xxx/9xxx.

- NB: This is a common style for Ansible IOS upgrade scripting
  - https://networkproguide.com/example-ansible-playbook-for-updating-cisco-ios-switches/
  - https://gdykeman.github.io/2018/06/26/ios-upgrades/
  - https://blog.sys4.de/ansible-upgrade-ios-en.html


### Tasks Catalyst IOS Reboot devices with newer installed firmware

- GATHER SWITCH FACTS (Tags: [] [])
- Catalyst IOS-XE 4500 family ISSU eligibility (WS-C4500X) (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^WS-C4500') and device_batch_evenodd`)
  - Check bootflash for IOS-XE and ROMMON (Tags: [] [] []) Failure is checked in set_facts below so we don't need to fail here to not reboot unintended hosts
  - show bootvar (Tags: [] [] [])
  - Debug reboot flag Catalyst IOS-XE (Tags: [] [] [])
  - Set reboot flag if current version does not match provisioned version (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^WS-C4500') and device_batch_evenodd` AND `doit_check_firmware.failed is false and ansible_net_image not in cisco_ios_facts.ansible_boot_variable`)
- Catalyst IOS-XE family reboot eligibility (C9300, C9300X) (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^C9300X?') and device_batch_evenodd`) FIXME: should we match on `ansible_net_version is version('17.01.01', 'gt')` instead of model regex
  - show install summary (Tags: [] [] [])
  - Debug reboot flag Catalyst IOS-XE (17.x) (Tags: [] [] [])
  - Set reboot flag if intended version is installed and inactive (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^C9300X?') and device_batch_evenodd` AND `cisco_ios_facts.ansible_installed_versions[config_context[0].ios_version] == 'I'`)
- Catalyst IOS-XE family reboot eligibility (WS-C3650, WS-3850, WS-C3560, WS-C4500) (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^(WS-C3[68]50)') and device_batch_evenodd`)
  - show version provisioned (Tags: [] [] [])
  - Debug reboot flag Catalyst IOS-XE (16.x) (Tags: [] [] [])
  - Set reboot flag if current version does not match provisioned version (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^(WS-C3[68]50)') and device_batch_evenodd` AND `ansible_net_version != cisco_ios_facts.ansible_provisioned_version`)
- Catalyst IOS family reboot eligibility (WS-3750, WS-3560CX) (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^WS-C3(750|560CX)') and device_batch_evenodd`)
  - show boot (Tags: [] [] [])
  - Debug reboot flag Catalyst IOS (Tags: [] [] [])
  - Set reboot flag if current firmware does not match booted firmware (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^WS-C3(750|560CX)') and device_batch_evenodd` AND `ansible_net_image != cisco_ios_facts.ansible_boot_image`)
- Schedule Reboot At a time if provisioned firmware does not match booted (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `':' in reload_time and doit_needsreboot`)
- Reboot in 2m and verfiy update if provisioned firmware does not match booted (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `':' not in reload_time and doit_needsreboot`)
  - NetCMS Check for unexpected config diff (Tags: [] [] ['make_check']) Looks for `WARN` or diff output in NetCMS make .check as a failure, should be no diff in text config
  
  FIXME: IOS-XE 16.x may show config diffs for embedded PKI certs if using `show archive config differences`
  FIXME: NetCMS Makefile .check target may be sensitive to CWD and should have improved path handling (with readlink/dirname or `${CMSDIR}`)
  
  - Define reload command for IOS/IOS-XE <= 16.x (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `':' not in reload_time and doit_needsreboot` AND `ansible_net_version is version('17.01.01', 'lt')`)
  - Define install activate command for IOS-XE >= 17.x (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `':' not in reload_time and doit_needsreboot` AND `ansible_net_version is version('17.01.01', 'gt') and ansible_net_version is version('18.01.01', 'lt')`)
  - Perform "reload in 2" for IOS <= 16.x and "install activate" for IOS > 17.x estimate 10-15 minutes (Tags: [] [] [])
  - WAIT FOR SWITCH TO RETURN (Tags: [] [] [])
  - Gather Facts post-reboot (Tags: [] [] [])
  - ASSERT THAT THE IOS VERSION IS CORRECT (Tags: [] [] [])
  - copy running-config startup-config (Tags: [] [] [])
  - NetCMS Check-in (Tags: [] [] [])
  - Commit new version and clean up old versions to free up flash (IOS-XE 17.x) (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `':' not in reload_time and doit_needsreboot` AND `ansible_net_version is version('17', 'gt') and ansible_net_version is version('18', 'lt') and ansible_net_model is regex('^(C9300X?-|WS-C3[68]50)')`)
  - Clean up old versions to free up flash (IOS-XE 16.x) (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `':' not in reload_time and doit_needsreboot` AND `ansible_net_version is version('16', 'gt') and ansible_net_version is version('17', 'lt') and ansible_net_model is regex('^(C9300X?-|WS-C3[68]50)')`)
  - Clean up old versions to free up flash (IOS-XE 15.x aka 3.x) (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `':' not in reload_time and doit_needsreboot` AND `ansible_net_version is version('16.01.01', 'lt') and ansible_net_model is regex('^(C9300X?-|WS-C3[68]50)')`)
  - Clean up BOOT vars and ROMMON on WS-4500X (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `':' not in reload_time and doit_needsreboot` AND `ansible_net_model is regex('^WS-4500')`)

## Play Nexus NXOS Install NXOS, BIOS, EPLD and reload devices with newer installed firmware

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `sn-*:rn-*:!tags_mgmt_vdc`
- Tags: []

Reboot NXOS into new Firmware after staging

Further documentation is found in [network-firmware](network-firmware.md) playbook

*NB*: Firmware updates do not apply to vDC guest OS instances, only the mangement vDC is updated
      additionally SSH connections are auto-enabled, Ansible network_cli nxos enable code
      will attempt to run `show` commands which don't exist in guest vDC and fail.
      Netbox Device inventory has a manually applied `mgmt_vdc` tag if the record is for a vDC
      so that they can be excluded when necessary.  We aren't yet using the newer Netbox
      vDC model, vDC instances are treated as if they were independant Devices when that isn't
      exactly accurate, but works well enough for most of our tooling.

Parallelization batch size set to `serial: [20, 100]` with `max_fail_percentage: 20`

`ansible_connect_timeout: 1800` set high as some firmware updates make the supervisor unresponsive
and take a long time but it should wait before treating this as a failure.

Many `wait_for` invocations will keep trying for up to an *hour* for the device to come back
as we've seen in practice that some firmware updates can take a _long_ time but are not failed.

- NB: This is a common style for Ansible IOS upgrade scripting
  - https://networkproguide.com/example-ansible-playbook-for-updating-cisco-ios-switches/
  - https://gdykeman.github.io/2018/06/26/ios-upgrades/
  - https://blog.sys4.de/ansible-upgrade-ios-en.html
- FIXME: move variables to shared `hosts.yml` inventory and not duplicated at play-local level


### Tasks Nexus NXOS Install NXOS, BIOS, EPLD and reload devices with newer installed firmware

- GATHER SWITCH FACTS (Tags: [] [])
- Nexus check running version against requested version (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version`)
  - show boot (Tags: [] [] [])
  - Check bootflash for NXOS (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version` AND `config_context[0].nxos_bin is defined`)
  - Check bootflash for Kickstart (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version` AND `config_context[0].nxos_kickstart_bin is defined`)
  - Check bootflash for EPLD (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version` AND `config_context[0].nxos_epld_bin is defined`)
  - Debug reboot flag Nexus NXOS (Tags: [] [] [])
  - Set reboot flag if staged firmware does not match running version (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version` AND `doit_check_firmware_nxos.failed is false`)
- Install NXOS, BIOS, EPLD now (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `doit_needsreboot`)
  - NetCMS Check for unexpected config diff (Tags: [] [] ['make_check']) NetCMS WARN when running-config does not match startup-config and '***************' which is part of the diff header
  FIXME: this calls .update target and is sensitive to CWD
  
  - Install NXOS Base OS and BIOS (Tags: [] [] []) FIXME: Only operating on N9K with staged installed firmware ready to boot
        we may need to break Nexus N[567][7K] into seperate play or block
        to ensure that we don't cut our legs off updating one platform
        that another device in the same play depends on.  I'm not sure
        the install command can be successfully staged on N[567][7K] so
        it might take a variable time to run, causing some hosts to reboot
        while others are still installing.
  
  - Install EPLD (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `doit_needsreboot` AND `config_context[0].nxos_epld_bin is defined`)
  - Gather Facts post-reboot (Tags: [] [] [])
  - Reload devices which haven't already reloaded from EPLD or install (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `doit_needsreboot` AND `ansible_net_version != config_context[0].nxos_version`)
  - ASSERT THAT THE NXOS VERSION IS CORRECT (Tags: [] [] [])
  - Set settle down timeout (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `doit_needsreboot` AND `ansible_net_platform is regex('^N9K-C95')`)
  - WAIT FOR SWITCH TO Settle Down (Tags: [] [] []) NXOS devices take a highly variable amount if time to initialize all hardware,
  and SSH can become available _long_ before the line-cards have fully booted,
  we wait so as not to commit a partially missing config
  
  - copy running-config startup-config (Tags: [] [] [])
  - NetCMS Check-in (Tags: [] [] [])

## Play Local User accounts setup

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `all`
- Tags: []

Convert to highest level of password hashing supported after new OS is applied (Useful for IOS 12 -> IOS 15 conversions) Play imported from [network-users.yml](network-users.md)

## Play Configure VTY stanzas

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `all`
- Tags: []

Configure added VTYs, sometimes the new OS version pre-creates more VTYs by default, ensure they have ACLs Play imported from [network-vty.yml](network-vty.md)
