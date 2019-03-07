Next Steps to explore OpenConfig as a group...

1. Identify on data model for each group to experiment with for their data and automation implementation. Maybe the OpenConfig [VLAN model](https://github.com/openconfig/public/tree/master/release/models/vlan) or [ACL model](https://github.com/openconfig/public/tree/master/release/models/acl), or something similar.
5. Each group report on how easy/hard it is to express their data with the chosen model.
6. Use chosen model to implement config changes on devices (using, for example the [Ansible netconf\_config module](https://docs.ansible.com/ansible/latest/modules/netconf_config_module.html), [[confd]{.underline}](https://www.tail-f.com/confd-basic/), or something with [gNMI](https://github.com/openconfig/gnmi)).
7.  Compare notes on the best way to apply models to devices (netconf vs confd vs gNMI).

Other thoughts...

- If OpenConfig YANG does what it promises, that will hopefully make the Automation tool part of the flow more common between groups, or just not matter that much if it's different.
- The netconf / confd / gNMI parts of this is where we are doing the most hand waving. It could be we're on the wrong track with these ideas; we're just not that familiar with that yet.
- Each group has deep roots with their sources of authority. Trying to find a common database for that is probably a losing battle.
- What does the interface between a YANG data model and a device's native configuration look like? i.e., when presented with a YANG model, how does a device map that model to its own specific configuration syntax?
- Do we have to rely on vendor-specific packages to update YANG model definitions on each individual device?
- Even without a native YANG implementation on the network device, there seems to be a lot of value in choosing YANG as a common modelling language.
- Umich is looking at OpenConfig for modeling certain objects, e.g. ACLs, for which we're trying to avoid designing our own schemas. However, with our current automation model, we still need an intermediary step to render data into a device-specific configuration syntax, so we're investigating whether or not this extra step is worth the effort.
