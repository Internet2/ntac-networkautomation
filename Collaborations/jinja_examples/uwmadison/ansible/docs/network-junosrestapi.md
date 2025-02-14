
# Playbook `network-junosrestapi.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-junosrestapi)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-junosrestapi.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-junosrestapi.yml)


## Play JunOS REST API Enable

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `rj-cssclabqa-*`
- Tags: []

EXPERIMENTAL JunOS REST API for OpenNMS PoC

Demonstration of enabling REST API for OpenNMS PoC environment to gather
performance the same performance metrics as `ns-scraper` does with CLI and `jlogin`
using OpenNMS XmlCollector

NB: only junos_command supports network_cli, junos_config and others require netconf
which needs to be configured as the first step

FIXME: move variables from play-local to `hosts.yml` inventory file


### Tasks JunOS REST API Enable

- enable netconf (Tags: [] []) (Notify: `commit config`)
- check if https cert is created (Tags: [] []) NB: Using `network_cli` instead of `netconf` to run `show` command
  
  `wait_for` only supports netconf and doesn't seem to work with this show command
      so we register the output and check it in a when clause in the next task
  
- create https self-signed cert manually (Tags: [] []) ([When](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html): `show_cert.stdout[0].find(junos_rest_https_cert) == -1`) `when` clauses are an `if` statement and basically eval() a python/jinja2 expression
  
  FIXME: running command over netconf to use wait_for to check output hasn't been tested,
     comment out the connection override and failed_when and uncomment wait_for to test.
  
  I prefer to have automation fail if the state is not known and verified and punt
  to an operator than proceed in an untested state, potentially causing errors
  
  `failed_when` also evaluates and expression and provides custom failure detection
  
- Enable system service rest (Tags: [] []) (Notify: `commit config`) Setting `confirm` in minutes in `junos_config` and notifying handler to confirm the commit at the end
  
  `notify` raises a flag for a handler to catch, handlers only run once
   at the end no matter how many times they are flagged.  can be a list
   of handlers to notify
  
- Add REST API ports to remote access firewall rules (Tags: [] []) (Notify: `commit config`)

### Handlers JunOS REST API Enable

- commit config  (Notify: `NetCMS Check-in`) Confirm change made in previous `junos_config` task which uses `commit confirm 5`
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
  
