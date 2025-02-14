
# Playbook `network-base.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-base)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-base.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-base.yml)


## Play Base Config Builder

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `u-cssc-b116-1-*`
- Tags: []

Experimental early playbook to test initial setup on APC platform

Set `connection: local` so that all playbook tasks execute on control node,
not target node as we don't have a CLI module for the APC CLI capable of issuing
commands at this time.  We do use the `expect:` built-in module with `sshpass`
to create an interactive login and issue commands to it, which *does* work.

- FIXME: Needs to be refactored for current Ansible connection methods
  and available `hosts.yml` variables, removing playbook-local vars.
- FIXME: Linter complains about use of `ignore_errors: true` instead of `failed_when:`
  as well as commands without a `changed_when:`
- TODO: check in final config to NetCMS
- NB: we are skipping SSL cert signing and just using the built-in self-signed cert until we have a way
    to automate provisoining, LetsEncrypt won't work as long as local.net.wisc.edu is not accessible off-campus
    and getting individual CSRs signed by InCommon, along with yearly renewals, is too labor intensive for the value
- TODO: Fetch CSR /ssl/nmc.csr
  - Submit CSR for signing (right now servercertificates.wisc.edu to submit and email to receive)
  - Put signed cert in right filename, rerun playbook
  - Put Cert in /ssl/cert.crt (or /ssl/nmc.crt)
  - Interactively Expect "ssl cert -i /ssl/cert.crt"

```yaml
- name: Check for SSL CSR
  stat:
    path: /var/local/tftp/ansible/certificates/{{ inventory_hostname }}.csr
  register: aos_csr
- name: Check for SSL Cert
  stat:
    path: /var/local/tftp/ansible/certificates/{{ inventory_hostname }}.crt
  register: aos_cert

- name: Get SSL CSR (NMC3)
  when: "device_family in ['ap964'] and aos_csr.stat is defined"
  ignore_errors: True
  # failed_when: "'someerr' in result"
  environment:
    SSHPASS: "{{ security_user.password }}"
  expect:
    command: "sshpass -e ssh {{ security_user.username }}@{{ inventory_hostname }}"
    responses:
      'apc>':
        - "ssl csr -CN {{ inventory_hostname }} -O \"University of Wisconsin-Madison\" -C US -O OCIS"
        - "exit"
```


### Tasks Base Config Builder

- Debug (Tags: [] [])
- Provision Base Config (Tags: [] [])
- Provision APC (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'apc' in manufacturers and device_family in ['ap964', 'ap963']`) FIXME: variables can be shared in `hosts.yml` and not duplicated
  - Get Current AOS version (NMC3) (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'apc' in manufacturers and device_family in ['ap964', 'ap963']` AND `device_family in ['ap964']`)
  - Debug AOS about (Tags: [] [] [])
  - Parse AOS version (NMC3) (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'apc' in manufacturers and device_family in ['ap964', 'ap963']` AND `device_family in ['ap964']`)
  - Debug AOS get_facts (Tags: [] [] [])
  - Provision User CSR (NMC2 NMC3) (Tags: [] [] [])
  - Reset Config to Defaults (NMC2 NMC3) (Tags: [] [] [])
  - WAIT FOR APC TO RETURN (Tags: [] [] [])
  - Pull Default APC Config with SCP (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'apc' in manufacturers and device_family in ['ap964', 'ap963']` AND `device_family in ['ap964', 'ap963']`) FIXME: ansible.netcommon.net_get might be able to SCP
  - Pull Default APC Config with FTP (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'apc' in manufacturers and device_family in ['ap964', 'ap963']` AND `device_family in ['ap961']`)
  - Install AOS Firmware with SCP (NMS3) (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'apc' in manufacturers and device_family in ['ap964', 'ap963']` AND `device_family in ['ap964'] and apc_aos_facts.ansible_net_os.aos is version(config_context[0].aos_version, 'ne')`) FIXME: ansible.netcommon.net_get might be able to SCP
  - WAIT FOR APC TO RETURN (Tags: [] [] [])
  - Get Current AOS version (NMC3) (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'apc' in manufacturers and device_family in ['ap964', 'ap963']` AND `device_family in ['ap964']`)
  - Debug AOS about (Tags: [] [] [])
  - Parse AOS version (NMC3) (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'apc' in manufacturers and device_family in ['ap964', 'ap963']` AND `device_family in ['ap964']`)
  - Debug AOS get_facts (Tags: [] [] [])
  - ASSERT THAT THE AOS VERSION IS CORRECT (Tags: [] [] [])
  - Load AOS config.ini with SCP (NMC3) (Tags: [] [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `'apc' in manufacturers and device_family in ['ap964', 'ap963']` AND `device_family in ['ap964']`) FIXME: use ansible.netcommon.net_put instead if possible
  - WAIT FOR APC TO RETURN (Tags: [] [] [])
