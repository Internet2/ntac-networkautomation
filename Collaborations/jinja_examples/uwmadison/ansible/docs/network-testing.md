
# Playbook `network-testing.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-testing)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-testing.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-testing.yml)


## Play ArubaOS Test Playbook

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `cm-*:c-*`
- Tags: []

EXPERIMENTAL Ad-hoc playbook to `show datapath route-cache` finding issues with Aruba switching software.

FIXME: move variables from play-local to `hosts.yml` inventory file


### Tasks ArubaOS Test Playbook

- show route cache (Tags: [] [])
- debug route cache (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `show_datapath_routecache.stdout is regex(aruba_route_cache_regex)`)

## Play Test playbook

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `r-*:s-*`
- Tags: []

EXPERIMENTAL WIP and scratchpad playbook


### Tasks Test playbook

- GATHER SWITCH FACTS (Tags: [] [])
- show install summary (Tags: [] [])
- Debug reboot flag Catalyst IOS-XE (17.x) (Tags: [] [])
- Debug facts (Tags: [] [])
