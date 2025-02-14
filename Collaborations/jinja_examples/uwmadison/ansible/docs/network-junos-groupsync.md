
# Playbook `network-junos-groupsync.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-junos-groupsync)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-junos-groupsync.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-junos-groupsync.yml)


## Play JunOS Sync Config Groups

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `rj-cssclabqa-*`
- Tags: []

EXPERIMENTAL JunOS Configuration

Demonstration of method to sync config from `/usr/local/uwsysnet-iptrack/etc/configdata/juniper/juniper-groups`
using Ansible instead of jlogin

NB: only junos_command supports network_cli, junos_config and others require netconf
which is presumed to already be configured

FIXME: move variables from play-local to `hosts.yml` inventory file


### Tasks JunOS Sync Config Groups

- Sync Config groups from uwsysnet-iptrack (Tags: [] []) (Notify: `commit config`) `notify: commit config` raises a flag for a handler to catch, handlers only run once
   at the end if they are flagged no matter how many times they are flagged.
  
   `notify` can be a string of the `name` of a handler or a list of handler
   names to notify, and handlers can `listen` for more than one notification
   name.
  

### Handlers JunOS Sync Config Groups

- commit config  (Notify: `NetCMS Check-in`)
- NetCMS Check-in  you can have a list of `notify` flags, or have multipler handlers listen
  for the same flag, or have handlers notify other handlers to chain them,
  when handlers need to have more than one step.  I suppose a handler could
  also import a playbook or use the `block` module to have multiple tasks.
  eg. `listen: "commit config"`
  
  task modules are ususally run against the target host `inventory_hostname`
  but can be delegated to other hosts, eg enabling a service on one host may
  need to push a command to the load balancer on another host, or in this
  case we run the CMS check-in command on the ansible control node (ie where
  we are running the playbook from).
  
  we use `failed_when` here to check the output text for `WARN` and not just for a non-zero exit code
  
