
# Playbook `network-logfetch.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-logfetch)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-logfetch.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-logfetch.yml)


## Play Fetch Cisco Catalyst logs

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `r-*:s-*:t-*`
- Tags: []

EXPERIMENTAL

Ad-hoc method to run `show logging` on a selected list of hosts
similar to LookingGlass, used during NetLOG migration to ensure
logs from OOB devices were safely archived


### Tasks Fetch Cisco Catalyst logs

- catalyst show logging (Tags: [] [])
- catalyst output (Tags: [] [])

## Play Fetch Cisco Nexus logs

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `rn-*:sn-*`
- Tags: []

EXPERIMENTAL

Ad-hoc method to run `show logging` on a selected list of hosts
similar to LookingGlass, used during NetLOG migration to ensure
logs from OOB devices were safely archived


### Tasks Fetch Cisco Nexus logs

- nexus show logging (Tags: [] [])
- nexus output (Tags: [] [])
