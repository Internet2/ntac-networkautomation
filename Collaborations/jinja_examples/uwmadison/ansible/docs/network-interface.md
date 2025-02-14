
# Playbook `network-interface.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-interface)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-interface.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-interface.yml)


## Play Interface Builder

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `device_roles_core:device_roles_node`
- Tags: []

EXPERIMENTAL Managed network Interface configuration


FIXME: how do we filter defaults so we don't build all interfaces on all hosts
we will probalby need to have the user specify something to limit without needing
them to lookup and enter the ... what?


### Tasks Interface Builder

- Provision Interfaces (Tags: [] []) Render `network/interfaces/*.j2` templates into `/var/local/tftp/ansible/interfaces/{{ inventory_hostname }}.conf`
  for testing
  
  FIXME: make tftp dir a variable that matches NetCMS config generation
  
  FIXME: do we have a way to sanity check with `validate`?
  
