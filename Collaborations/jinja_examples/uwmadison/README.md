# Automation tools and templates from University of Wisconsin-Madison

## NEXT-GEN-RADIAL-ACCESS-BUILDER-TEMPLATES.lib

Templates used by current Perl CGI rendered with Template Toolkit.  The CGI has forms which collect data over a couple of pages for how many of what kind of switch should be provisioned in a stack for access (IDF, edge) or radial (MDF, aggregation) along with its mangement IPs, uplink port descriptions and a minimal template for what the default building-facing port config on the node router should look like. We use the same basic template for an access and radial switch of the same device family as there are only a few config differences between them.

Configuration in `config.yaml` is used to populate form elements in the CGI, including duplicating some Netbox config_context, Device Type and Module Type data (which never changes after initial creation). Using Netbox data formats allows a straightforward translation to Python/Jinja2 if desired.  Eventually we will transition from building initial configs with a standalone tool, to saving that data in Netbox and rendering the initial config from Netbox data, which can be regenerated at any time to audit post-install config changes from the standard.  

## Ansible

We have a few Ansible playbooks which operate on network devices, for auditing and remediating AAA issues and for updating firmware, and a number of proof-of-concept playbooks/templates as we tried to evaluate whether Ansible was a good fit for overall config management of network devices, as we've invested in Ansible for our Linux management/monitoring servers.  We also have different tooling for radial/access devices which have a very regular and standardized config over thousands of devices, and node/core routers/firewalls which have a much more variable config over tens of devices with only some parts standardized.  You may also notices a preexisting local password vault tool called `devinfo` which is sprinkled around to populate sensitive variables.  Actively used playbooks will have a handler which can check-in the device into RCS (like RANCID) after making changes so we always have the current config state backed up and attribution on who made what changes.

- `network-firmware-stage.yml` Uploads an stages firmware on IOS/IOS-XE/NXOS devices based on the Netbox Platform and Config Context data, we define a platform for every firmware version so that the context with specific file info can be associated with it.
- `network-firmware-reload.yml` Validate firmware is ready and reboot into new version during maintenance window, verifying the reboot successfully upgraded the device. Try not to saw our legs off or brick the device.
- `network-users.yml` and `user-audit.sh` verifies the correct local user accounts are present on manged devices and remediates to bring them into alignment.  The user-audit.sh wraps Ansible and configures JSON output which is filtered with `jq` to provide an audit list of devices out of alignment which integrates with preexisting reporting tools.  This maybe a bit convoluted but is a PoC using the same process to audit as to remediate, it's easy to write a regex, it's hard to know to update the regex years later when something changes.
- `network-radius.yml` Validate IOS AAA configuration using a newer style, which needed to be updated on some older Catalyst devices to allow firmware updates some time ago.
- `network-opennms.yml` and `network-entuity.yml` Provisioning test for monitoring platform PoC, makes some use of GraphQL to list all IPs on a manged network device efficiently.

Various others.
