
# Playbook `network-firmware-stage.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-firmware-stage)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-firmware-stage.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-firmware-stage.yml)


## Play AAA RADIUS setup

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `all`
- Tags: []

Needed for IOS 12.2(58) upgrade to 15.2(4)E10 as older IOS 12 AAA config format no longer supported Play imported from [network-radius.yml](network-radius.md)

## Play Catalyst IOS Code Deployment

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `s-*:r-*`
- Tags: []

Prepare IOS devices for Firmware Update

Further documentation is found in [network-firmware](network-firmware.md) playbook

Commands for staging firmware vary between classic IOS 12.x and IOS-XE 3.x, 15.x, 16.x, 17.x

- Long timeout on SSH session to handle supervisor being unresponsive during slow
  firmware updates `ansible_connection_timeout: 1800` that are not failed.
- *WARN*: Catalyst 4500X firmware updates are *EXPERIMENTAL* and in our experience
  will break VSS, the only method that may work for Cat4k with VSS is ISSU, which
  we have _not_ tested.
- FIXME: move variables to `hosts.yml` and remove duplicates at play-local level
- NB: This is a common style for Ansible IOS upgrade scripting
  - https://networkproguide.com/example-ansible-playbook-for-updating-cisco-ios-switches/
  - https://gdykeman.github.io/2018/06/26/ios-upgrades/
  - https://blog.sys4.de/ansible-upgrade-ios-en.html


### Tasks Catalyst IOS Code Deployment

- GATHER SWITCH FACTS (Tags: [] [])
- Catalyst IOS-XE family code bundle (WS-C4500X) (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^WS-C4500X')`)
  - show bootvar (Tags: [] [] [])
  - Debug variables for IOS-XE (Tags: [] [] [])
  - Check bootflash for IOS-XE and ROMMON (Tags: [] [] [])
  - Copy IOS-XE and ROMMON to bootflash (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^WS-C4500X')` AND `doit_check_firmware.failed`) Using unauthenticated HTTP on `cms.net.wisc.edu` host and verifying MD5 checksum is faster and more reliable than TFTP. Depends on Apache `Require ip {{ address }}` ACL
  - Set boot variables (Tags: [] [] []) https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst4500/12-2/01xo/configuration/guide/config/supcfg.html#wp1051990
  the last digit of the config register is 0x0000=boot to rommon, 0x0001=boot first image found in flash, 0x0002=boot using boot variable order
  the first digit is 0x2000=load rommon if boot fails
  
  - show bootvar (Tags: [] [] [])
  - NetCMS Check-in (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^WS-C4500X')` AND `doit_stage_firmware.changed`)
  - Debug command output (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^WS-C4500X')` AND `doit_stage_firmware.stdout is defined`)
  - Debug bootvar (Tags: [] [] [])
- Catalyst IOS-XE family code install (WS-C3650, WS-3850, WS-C3560, C9300, C9300X) (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^(C9300X?-|WS-C3[68]50)')`)
  - Clean up old versions to free up flash (IOS-XE 16.x) (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^(C9300X?-|WS-C3[68]50)')` AND `ansible_net_version is version('16.01.01', 'gt') and ansible_net_version is version('17.01.01', 'lt')`) FIXME: Skipping cleanup on IOS-XE 17.x in case the inactive version is the one we are trying to install
  
  FIXME: Using `wait_for` with `result[0]` in `--check` mode fails when result isn't populated and the array doesn't exist
  Should ignore the error when in check mode `ignore_errors: "{{ check_mode }}"`
  
  - Clean up old versions to free up flash (IOS-XE 15.x aka 3.x) (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^(C9300X?-|WS-C3[68]50)')` AND `ansible_net_version is version('16.01.01', 'lt')`)
  - Refresh filesystem free space info (Tags: [] [] [])
  - show install summary (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^(C9300X?-|WS-C3[68]50)')` AND `ansible_net_version is version('17.01.01', 'gt')`)
  - show version provisioned (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^(C9300X?-|WS-C3[68]50)')` AND `ansible_net_version is version('17.01.01', 'lt')`)
  - Check file size for ios_bin (Tags: [] [] []) Skip `assert` that flash has enough free space, rely on cleanup instead
  - Debug variables for IOS-XE (17.x) (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^(C9300X?-|WS-C3[68]50)')` AND `ansible_net_version is version('17.01.01', 'gt')`)
  - Debug variables for IOS-XE (16.x) (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^(C9300X?-|WS-C3[68]50)')` AND `ansible_net_version is version('17.01.01', 'lt')`)
  - Install Process for IOS-XE 17.x (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^(C9300X?-|WS-C3[68]50)')` AND `ansible_net_version is version('17.01.01', 'gt') and ansible_net_version is version('18.01.01', 'lt') and config_context[0].ios_version not in cisco_ios_facts.ansible_installed_versions`) NB: skip deploy if it the intended version is already in the show install summary list
  - Install Process for IOS-XE 16.x (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^(C9300X?-|WS-C3[68]50)')` AND `ansible_net_version is version('16.01.01', 'gt') and ansible_net_version is version('17.01.01', 'lt') and ansible_net_version is version(cisco_ios_facts.ansible_provisioned_version, 'eq')`) NB: skip deploy if its already staged and provisioned version matches requested version
  - Install Process for IOS-XE 15.x (aka 3.x) (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^(C9300X?-|WS-C3[68]50)')` AND `ansible_net_version is version('16.01.01', 'lt') and ansible_net_version is version(cisco_ios_facts.ansible_provisioned_version, 'eq')`) NB: skip deploy if its already staged and provisioned version matches requested version
  - Debug command output (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^(C9300X?-|WS-C3[68]50)')` AND `doit_stage_firmware.stdout is defined`)
- Catalyst IOS family code install (WS-C3750, WS-3560CX) (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^WS-C3(750|560CX)')`)
  - show boot (Tags: [] [] [])
  - Check file size for ios_bin (Tags: [] [] []) Skipping `assert` that flash has enough free space, just overwrite image.
  - Debug variables for IOS (Tags: [] [] [])
  - Install process for IOS 12.x (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^WS-C3(750|560CX)')` AND `ansible_net_image == cisco_ios_facts.ansible_boot_image`) NB: skip deploy if its already staged and we already have set the boot image to the requested version
  - Debug command output (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].ios_version and ansible_net_model is regex('^WS-C3(750|560CX)')` AND `doit_stage_firmware.stdout is defined`)
- NetCMS Check for unexpected config diff (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `doit_stage_firmware.stdout is defined`) NB: this duplicates `show archive config differences` in reload playbook
      but the best time to find out an unexpected config change is when
      staging so it can be fixed before deployment
  
  FIXME: this calls .update target and is sensitive to CWD
  
  NetCMS WARN when running-config does not match startup-config and '***************' which is part of the diff header
  

## Play Nexus NXOS Code Deployment

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `sn-*:rn-*:!tags_mgmt_vdc`
- Tags: []

Prepare NXOS devices for Firmware Update

Further documentation is found in [network-firmware](network-firmware.md) playbook


- Long timeout on SSH session to handle supervisor being unresponsive during slow
  firmware updates `ansible_connection_timeout: 1800` that are not failed.
- FIXME: move variables to `hosts.yml` and remove duplicates at play-local level
- NB: This is a common style for Ansible IOS upgrade scripting
  - https://networkproguide.com/example-ansible-playbook-for-updating-cisco-ios-switches/
  - https://gdykeman.github.io/2018/06/26/ios-upgrades/
  - https://blog.sys4.de/ansible-upgrade-ios-en.html


### Tasks Nexus NXOS Code Deployment

- GATHER SWITCH FACTS (Tags: [] [])
- show boot (Tags: [] [])
- Nexus NXOS code bundle (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version and cisco_nxos_facts.ansible_boot_image != 'bootflash:/' + config_context[0].nxos_bin`) NB: skip provisioning steps entirely if provisioned filename in show boot
      matches the file we are attempting to deploy, it's already done.
  
  - Debug variables for NXOS (Tags: [] [] [])
  - Check bootflash for NXOS (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version and cisco_nxos_facts.ansible_boot_image != 'bootflash:/' + config_context[0].nxos_bin` AND `config_context[0].nxos_bin is defined`)
  - Check bootflash for Kickstart (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version and cisco_nxos_facts.ansible_boot_image != 'bootflash:/' + config_context[0].nxos_bin` AND `config_context[0].nxos_kickstart_bin is defined`)
  - Check bootflash for EPLD (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version and cisco_nxos_facts.ansible_boot_image != 'bootflash:/' + config_context[0].nxos_bin` AND `config_context[0].nxos_epld_bin is defined`)
  - Check sup-2 bootflash for EPLD (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version and cisco_nxos_facts.ansible_boot_image != 'bootflash:/' + config_context[0].nxos_bin` AND `config_context[0].nxos_epld_bin is defined and cisco_nxos_facts.ansible_sup_count == 2`)
  - Check file size for NXOS system image (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version and cisco_nxos_facts.ansible_boot_image != 'bootflash:/' + config_context[0].nxos_bin` AND `config_context[0].nxos_bin is defined`) FIXME: nxos_facts hardware does not get filesystem free space, we'd need
         to parse that out manually to do these checks, so skipping `assert` for now
  
  - Copy NXOS to bootflash (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version and cisco_nxos_facts.ansible_boot_image != 'bootflash:/' + config_context[0].nxos_bin` AND `config_context[0].nxos_bin is defined and doit_check_firmware_nxos.failed`)
  - Copy Kickstart to bootflash (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version and cisco_nxos_facts.ansible_boot_image != 'bootflash:/' + config_context[0].nxos_bin` AND `config_context[0].nxos_kickstart_bin is defined and doit_check_firmware_kickstart.failed`)
  - Copy EPLD to bootflash (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version and cisco_nxos_facts.ansible_boot_image != 'bootflash:/' + config_context[0].nxos_bin` AND `config_context[0].nxos_epld_bin is defined and doit_check_firmware_epld.failed`)
  - Copy EPLD to sup-standby bootflash (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version and cisco_nxos_facts.ansible_boot_image != 'bootflash:/' + config_context[0].nxos_bin` AND `config_context[0].nxos_epld_bin is defined and cisco_nxos_facts.ansible_sup_count == 2 and doit_check_firmware_epld2.failed`)
  - Install NXOS N9K-C93xx N3K (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version and cisco_nxos_facts.ansible_boot_image != 'bootflash:/' + config_context[0].nxos_bin` AND `ansible_net_platform is regex('^N9K-C93') or ansible_net_platform is regex('^N3K-')`) Only install on platforms which support `no-reload` install option,
  which does not exist on N[567]K, those can only be safely installed
  during maintenance window.
  
  - Install NXOS N9K-C95xx (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version and cisco_nxos_facts.ansible_boot_image != 'bootflash:/' + config_context[0].nxos_bin` AND `ansible_net_platform is regex('^N9K-C95')`) Missing `wait_for` check of command result.
  Install process does copy nxos.bin to the second supervisor, but not EPLD file
  
  - Copy running-config startup-config (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version and cisco_nxos_facts.ansible_boot_image != 'bootflash:/' + config_context[0].nxos_bin` AND `doit_stage_firmware_n9k_c93.changed or doit_stage_firmware_n9k_c95.changed`)
  - NetCMS Check-in (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version and cisco_nxos_facts.ansible_boot_image != 'bootflash:/' + config_context[0].nxos_bin` AND `doit_stage_firmware_n9k_c93.changed or doit_stage_firmware_n9k_c95.changed`)
  - Debug install command output N9K-C95 (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version and cisco_nxos_facts.ansible_boot_image != 'bootflash:/' + config_context[0].nxos_bin` AND `doit_stage_firmware_n9k_c95.stdout is defined`)
  - Debug install command output N9K-C93 (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `ansible_net_version != config_context[0].nxos_version and cisco_nxos_facts.ansible_boot_image != 'bootflash:/' + config_context[0].nxos_bin` AND `doit_stage_firmware_n9k_c93.stdout is defined`)
