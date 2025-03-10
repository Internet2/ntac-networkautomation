
# Playbook `network-firmware.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-firmware)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-firmware.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-firmware.yml)


## Play Network Device Firmware/Software Management

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `localhost`
- Tags: []


The network-firmware-stage.yml playbook will copy and install in a non-disruptive fasion
firmware for Cisco Catalyst and Nexus devices with commands for classic `IOS 12.2` on `WS-C3750`
newer `IOS 12.2(58)` and `IOS 15.2` on `WS-C3750E/X`, `IOS-XE 3.x` and `IOS-XE 16.x` on `WS-C3650/C3850`
with a work-in-progress for `WS-C4500X` devices which are much more delicate than the others
as well as a second playbook for `NXOS` on `N9K-C93xx/C95xx` with a work-in-progress for
`NXOS` on `N5/6/7K` family devices.

IOS platforms on Catalyst 3xxx series devices have commands
which will clean the boot flash filesystem of unneeded firmware files, the other Catalyst
4xxx and 6xxx as well as Nexus platform devices do not and the playbook does not manage
available space in the boot flash on those platforms, out of space conditions will likely
result in a failure of the file copy.

Inforamtion about what version should be installed on a particuler device is contained
within [Netbox Configuration Contexts](https://netbox.net.wisc.edu/extras/config-contexts/).
[Config Contexts](https://netbox.readthedocs.io/en/stable/models/extras/configcontext/) are a
way to associate user-defined configuration data in JSON format in a precedence hierarchy with
Netbox Device records based on properties of the Device such as Type, Role, Platform, Site, Tag,
etc. with an override mechanism in the Device record itself.

For the Ansible firmware management
playbook the [Device Platform](https://netbox.net.wisc.edu/dcim/platforms/) is the key, Platform
records are associated with a [Manufacturer](https://netbox.net.wisc.edu/dcim/manufacturers/) and
have a generic record for each firmware family as well as a specific record for `<family>-<version>`.
The version should be what is reported by SNMP in the NetCMS JSON file, eg `iosxe-Gibraltar 16.12.05b`
The Platform of a Device is initially provisioned using `update-netbox-db.pl` from NetCMS JSON data
gathered by `conf-update.sh` in the `make ${device_name}.update` process, by adding the following
arguemments `update-netbox-db.pl --json --devices --device-platform --device ${device_name}` to the
provisioning proces.  After provisioning the Platform information is mangaged in Netbox and should
reflect the version that the device is _desired_ to be running, that it will be audited against
for compliance.

Configuration Contexts are associated with Platforms, and can additionally be assocaited with
a list of Device Types, eg.
Config Context [iosxe_03_07_05E](https://netbox.net.wisc.edu/extras/config-contexts/17/)
is associated with Platform [iosxe-03.07.05E](https://netbox.net.wisc.edu/dcim/platforms/43/)
which is only applied to Catalyst 3650/3850 devices that this firmware is compatable with
and contains the name of the firmware image in `netcms:/var/local/tftp/cisco/{{ ios_bin }}`
as well as the MD5 for copy verification and the version string reported by `show version`

```json
{
    "ios_bin": "cat3k_caa-universalk9.SPA.03.07.05.E.152-3.E5.bin",
    "ios_md5": "d6f1f24a30dc67697a0c815661ba670c",
    "ios_version": "03.07.05E"
}
```

The information in a Config Context will show up as inherited on the
[Config Context tab of a Device record](https://netbox.net.wisc.edu/dcim/devices/66/config-context/)
along with sources and any precedence.

Precedence can be used with the same version of the same platform has different
firmware images for different Device Types, for example the [Platform iosxe-Gibraltar 16.12.05b](https://netbox.net.wisc.edu/dcim/platforms/117/)
is used on both Catalyst 3xxx and Catalyst 9xxx but with different firmware images, the default
[Config Context iosxe_16_12_05b-cat3k](https://netbox.net.wisc.edu/extras/config-contexts/3/) with a
precidence weight of `1000` associated with Platform `iosxe-Gibraltar 16.12.05b`

```json
{
    "ios_bin": "cat3k_caa-universalk9.16.12.05b.SPA.bin",
    "ios_md5": "9048edf018eb03cff526ad3c3e4bd9de",
    "ios_version": "16.12.05b"
}
```

and
[iosxe_16_12_05b-cat9k](https://netbox.net.wisc.edu/extras/config-contexts/32/)
with a higher precedence weight of `2000` associagted with Platform `iosxe-Gibraltar 16.12.05b`
and additionally associated with [Device Type C9300-48P](https://netbox.net.wisc.edu/dcim/device-types/302/)
among others.

```json
{
    "ios_bin": "cat9k_iosxe.16.12.05b.SPA.bin",
    "ios_md5": "9910bcc37a08cea74b595f9c998e24f4",
    "ios_version": "16.12.05b"
}
```

In doing so each Device will have a Config Context containing information about the correct
firmware file for that type/model/platform.  *Note* only some of the Config Contexts specify an
exhaustive list of Device Types they are associated with, when it is necessary as the same
supported version has different variants (eg. ipservices vs. ipbase not universal in Classic IOS)
so an Entineer is not technically prevented from assigning a very wrong platform and firmware
file to a device, however attempting to deploy that version may result in a number of
failures when attempting to stage it, as the install commands often check for compatability,
before the staging would be considered successful, but it is not recommended to rely on this.
Exhaustively defining the Device Types for each Configuration Context would resolve this issue,
so that assinging a wrong Platform would result in _no_ firmware Context data but has not yet been
accomplished.


### Netbox Platform/Config Management Workflow

To create a new firmware version configuration that is supported for upgrade first
find the files you want at the [Cisco Software Download](https://software.cisco.com/download/home)
site.  Some platforms just have a single OS image, like `ios_bin` on the Catalyst 3xxx, some have seperate
images for other firmware such as `ios_rommon_bin` on the Catalyst 4xxx or `nxos_epld_bin` on the Nexus
and some have a third firmware such as the `nxos_kickstart_bin` on Nexus N5/6/7K.  For each
in (`ios_bin`, `ios_rommon`, `nxos_bin`, `nxos_kickstart_bin`, `nxos_epld_bin`) there is
a cooresponding MD5 and Version (`ios_md5`, `ios_rommon_md5`, `nxos_version`, etc.) where
the Version is exactly what is reported in `show version` and parsed by Ansible
[ios_facts](https://docs.ansible.com/ansible/latest/collections/cisco/ios/ios_facts_module.html#ansible-collections-cisco-ios-ios-facts-module) and
[nxos_facts](https://docs.ansible.com/ansible/latest/collections/cisco/nxos/nxos_facts_module.html).

Download all of the releavnt files and place in `netcms:/var/local/tftp/cisco/` and not in any
subdirectories, as that would make some parsing and comparisons more difficult, but one can use
[ln](https://www.man7.org/linux/man-pages/man1/ln.1.html) hardlinks or softlinks to deduplicate
and organize firmware images, especially when also providing compatability with existing Builder tools.

Create a [Platform](https://netbox.net.wisc.edu/dcim/platforms/) with the relevant `<family>-<version>`
as reported by SNMP in the NetCMS JSON file, also used in AANTS/DeviceManager, in the same fashion
as other related entries.  If the version is Recommended by Cisco note it in the Description field
and remove from other Platform entries that are no longer Recommended.  eg.

```json
{
    "name": "nxos-9.3(7a)",
    "slug": "nxos-9-37a",
    "manufacturer": "Cisco",
    "napalm_driver": "nxos_ssh",
    "napalm_args": null,
    "description": "Recommended for N9K family"
}
```

Create a [Config Context](https://netbox.net.wisc.edu/extras/config-contexts/) with the name
`<family>_<version>-<device_type>` using underscores to match the naming convention of other
entries. The filenames, MD5 sums and Version information can be gathered from the file info
on the Cisco Software Download site. For a Nexus N3K/N9K device with a NXOS System Software
and NXOS EPLD Update file the JSON data in the Config Context can look like this

```json
{
    "nxos_bin": "nxos.9.3.7a.bin",
    "nxos_md5": "e52671c06cece1104eddab64e1c30517",
    "nxos_version": "9.3(7a)",
    "nxos_epld_bin": "n9000-epld.9.3.7.img",
    "nxos_epld_md5": "5c3c2877694796836fc94b36c787e9ad",
    "nxos_epld_version": "9.3(7)"
}
```
and the entire Config Context entry may look like this

```json
{
    "name": "nxos_9_3_7a-N9K",
    "weight": 1000,
    "description": "",
    "is_active": true,
    "regions": [],
    "site_groups": [],
    "sites": [],
    "device_types": [
        "Nexus 3232C",
        "Nexus9000 C93108LC-EX Chassis",
        "Nexus9000 C93108TC-EX Chassis",
        "Nexus9000 C93108TC-FX Chassis",
        "Nexus9000 C9336C-FX2 Chassis",
        "Nexus 93120TX",
        "Nexus 93180LC-EX",
        "Nexus 93180YC-EX",
        "Nexus 93180YC-FX",
        "Nexus 9332PQ",
        "Nexus 9348GC-FXP",
        "Nexus 9364C",
        "Nexus 9372PX",
        "Nexus 9372PX-E",
        "Nexus 9372TX",
        "Nexus 9396PX",
        "Nexus 9396TX",
        "Nexus 9504",
        "Nexus 9508"
    ],
    "roles": [],
    "platforms": "nxos-9.3(7a)",
    "cluster_groups": [],
    "clusters": [],
    "tenant_groups": [],
    "tenants": [],
    "tags": [],
    "data": {
        "nxos_bin": "nxos.9.3.7a.bin",
        "nxos_md5": "e52671c06cece1104eddab64e1c30517",
        "nxos_version": "9.3(7a)",
        "nxos_epld_bin": "n9000-epld.9.3.7.img",
        "nxos_epld_md5": "5c3c2877694796836fc94b36c787e9ad",
        "nxos_epld_version": "9.3(7)"
    }
}
```

Once the firmware files are in the NetCMS TFTP directory (which is also available
via HTTP with an Access List defined in the Apache `cms.net.wisc.edu` vHost config)
then you can Edit one or more Netbox Device records to change the Platform to the one
you want the Device to be audited against and changed to.  For example you could search
for [Devices with "b217" in their name in the "CSSC" Site with the Manufacturer of "Cisco" and the Platform of "nxos-9.3(7)" or "nxos-7.0(3)I7(8)"](https://netbox.net.wisc.edu/dcim/devices/?q=b217&site_id=504&manufacturer_id=5&asset_tag=&mac_address=&has_primary_ip=&local_context_data=&platform_id=129&platform_id=74&virtual_chassis_member=&console_ports=&console_server_ports=&power_ports=&power_outlets=&interfaces=&pass_through_ports=) and use the Select All check box in the upper left hand corner of the result table
or check/uncheck each device you want to edit then use the yellow Edit Selected button and
change the Platform for all the selected devices to `nxos-9.3(7a)` and Save.  You can search
by Model (eg. selecting all the Cat3750X variants) or Role (eg. selecting "radial" and "access" but not "node", "core" or "mgmt") or by physical Site (eg. "CSSC") and quickly assign the
desired Platorm to whatever population of devices you want to be eligible for new firmware.

As we are using the Config Context information to audit firmware versions using Ansible,
every version of IOS, IOS-XE, and NXOS on platforms supported by the playbook need
to be defined in Netbox so that we can compare the existing version against the desired version
and the firmware files should exist in the TFTP directory so that we can roll back to any
supported version should we ever wish to do so.

### Ansible Playbooks for Network Management

The Ansible playbooks the replicate the functionality of AANTS/CodePusher and NextGenAccessRadialBuilder
are split into two parts, staging and reload with a combined playbook `network-firmware.yml` that just includes the
others for cases where you want to do both steps immediately.  The `network-firmware-staging.yml` playbooks compare the
actual running network OS with the Netbox Platform the target device is configured to use
and perform the non-service-impacting steps to transfer and install the new firmware so that
the device will be running the new version on its next reload.  The `network-firmware-reload.yml` playbooks
compare the running network OS with the version provisioned on next boot and will perform the service-impacting
steps to install firmware and reload devices, verifying that they are running the intended version at the end.

Ansible for Network Management [includes utilities for connecting](https://docs.ansible.com/ansible/latest/collections/ansible/netcommon/network_cli_connection.html)
to a managed network device using its CLI or API and issuing commands
([ios_command](https://docs.ansible.com/ansible/latest/collections/cisco/ios/ios_command_module.html),
[nxos_command](https://docs.ansible.com/ansible/latest/collections/cisco/nxos/nxos_command_module.html))
or templating text confguration blocks
([ios_config](https://docs.ansible.com/ansible/latest/collections/cisco/ios/ios_config_module.html),
[nxos_config](https://docs.ansible.com/ansible/latest/collections/cisco/nxos/nxos_config_module.html))
with the an Ansible process per managed device running on the Control Node where the Playbook is running (NetCMS).
The logic of the playbooks is controlled by the Ansible
[conditional `when:` expressions](https://docs.ansible.com/ansible/latest/user_guide/playbooks_conditionals.html)
which use [jinja2 comparison and logic operators](https://jinja.palletsprojects.com/en/latest/templates/#comparisons)
eg. `when: "ansible_net_version != config_context[0].ios_version` to compare the current version info gathered by
parsing `show version` output in
([ios_facts](https://docs.ansible.com/ansible/latest/collections/cisco/ios/ios_facts_module.html),
[nxos_facts](https://docs.ansible.com/ansible/latest/collections/cisco/nxos/nxos_facts_module.html)) and the verion info
associated with a particular managed network device in a Netbox Confiugration Context through the Netbox Platform.

Ansible playbooks are
[limited to operate by network device families using patterns](https://docs.ansible.com/ansible/latest/user_guide/intro_patterns.html)
indicated by our naming convention in the device name
using the `hosts:` directive at the playbook level, eg. `hosts: s-*:r-*` to make the playbook only eligible for IOS and IOS-XE devices
or also using information in Netbox eg. `hosts: sn-*:rn-*:!tags_mgmt_vdc` to only operate on NXOS devices which are not a vDC.
Further limits can be added on the command line using the `--limit` using
[a colon separated list of common patterns](https://docs.ansible.com/ansible/latest/user_guide/intro_patterns.html#common-patterns)
such as `&` to require a certain group or `!` to exclude a certain group,
eg `--limit 'rn-*:sn-*:&sites_cssc:&*b217*:&device_roles_access:&*-pri*'` which will only run Ansible against Nexus devices
in the CSSC B217 NS Techlab with a role of `access` and `*-pri*` in their names, regex name patterns can also be used
eg. `~[rs]n-.*cssc.*-b217-.*-pri`.  The `netbox_inventory.yml` configuration
automatically creates groups based on a list of attributes including sites, device_roles, device_types, tags and platforms
in the format you see above matching [perlre `\w`](https://perldoc.perl.org/perlre#Character-Classes-and-other-Special-Escapes)
and all other characters replaced with underscore (`_`), eg. `sites_cssc`, `device_roles_mgmt`, `device_types_ws_c3850_24xs_s`,
`tags_mgmt_oob`, and `platforms_ios_15_24e10`.  Another way to limit based on a specific list of device names generated
by another script or by hand by specifying `--limit @filename` with a file containing one device name per line.

### Ansible Staging workflow

`network-firmware-stage.yml` Can operate on Catalyst and Nexus family devices, with playbook tasks written but
testing not complete for Catalyst 4500X and Nexus 5000, 6000, 7000 and 7700 family devices, the Catalyst 6500
may be similar to the 4500X but no support has been attempted.  The `network-firmware-stage.yml` playbook also
includes the [`network-radius.yml` playbook](network-radius.md) that operates on Catalyst family devices to support upgrades of
IOS 12.2(58) to IOS 15.2 on Catalyst 3750X devices where the older `radius-server host <ip>` style syntax is
no longer supported and needs to be converted to a newer IOS and IOS-XE syntax.  The first playbook will be for
Catalyst family devices using [network_cli ios](https://docs.ansible.com/ansible/latest/network/user_guide/platform_ios.html)
with credentials from `/usr/local/ns/bin/devinfo` a default SSH connection timeout of 1800s (30m) changed from the
default of 30s and a command timeout of 300s (5m) changed from the default of 30s.  The timeouts have been adjusted
as some commands take a long time to return (and timeouts are adjusted further upward for specific long-running commands)
with the long connection timeout preventing idle persistent SSH sessions from being closed too early when playbooks
have large batches of long-running commands that may not have work for all hosts in a particular task, the connection
shouldn't be considered failed for timeout in subsequent tasks.  The `netbox-playbook.sh` wrapper script sets
the `--forks` option to a maximum of 500 parallel instances of Ansible operating on hosts, in the playbook the
[serial keyword](https://docs.ansible.com/ansible/latest/user_guide/playbooks_strategies.html) is used to set a list
of batch sizes so that the play us run against a limited number of hosts before operating on larger batches to
provide an emergency stopping point using [`max_fail_percentage`](https://docs.ansible.com/ansible/latest/user_guide/playbooks_error_handling.html#setting-a-maximum-failure-percentage)
to halt all playbook activity if there are too many fatal errors in a batch, currently this is set to 20% but may
be adjusted up or down as we get more operational data as to what is reasonable.

`network-firmware-stage.yml` has three different sets of procedures for `WS-C4500X`, `WS-C3650, WS-3850, WS-C3560, C9300`
and `WS-C3750, WS-3560CX` family Catalyst devices and within those families there are differences based on platform
version eg. IOS-XE 16.x `request platform software package (install|clean)` commands vs. IOS-XE 3.x `software (install|clean)`.

* Parse `show version` and related commands using [ios_facts](https://docs.ansible.com/ansible/latest/collections/cisco/ios/ios_facts_module.html) or [nxos_facts](https://docs.ansible.com/ansible/latest/collections/cisco/nxos/nxos_facts_module.html)
* Catalyst 4K IOS-XE process if the running version does not match the Netbox Config Context `ios_version`
  * Parse `show bootvar` using `templates/cisco_ios_show_bootvar.yml` and save to `cisco_ios_facts`
  * Print out debug message showing intended change summary if Ansible in `--verbose` mode
  * Check `bootflash:` MD5 if `ios_bin` and `ios_rommon` files are already successfully deployed
  * Copy `ios_bin` and `ios_rommon` to `bootflash:`, verify the MD5 and copy files to `slavebootflash:` VSS partner (FIXME: will fail if device does not have an active VSS partner)
  * Remove existing `boot system` statements from confg and add ROMMON and IOS-XE images in that order, set `config-registers 0x2102` to respect the boot configuration.  copy running-config startup-config if changed. (FIXME: This may need to be changed to use ISSU procedure on VSS devices or `redundancy reload shelf` in the `network-firmware-reload.yml` playbook due to how touchy VSS is in causing errors that make devices fail to boot)
  * Use NetCMS Makefile to peforma a `make {{ inventory_hostname }}.update` to check in the config change to the boot statement
  * Print out debug messages showing output from commands if Ansible in `--verbose` mode
* Catalyst 3K 9k IOS-XE process if the running version does not match the Netbox Config Context `ios_version`
  * Clean old firmware files from flash to free space
  * Parse `show version provisioned` using `templates/cisco_ios_show_version_provisioned.yml` and save as `cisco_ios_facts`
  * Print out debug message showing intended change summary if Ansible in `--verbose` mode
  * Install new IOS directly over the network using HTTP (saving space on flash by not needing temporary copy of .bin file) set to be active on next boot, only if the provisioned version matches the currently running version, otherwise deployment has already been done and the reboot is pending, we don't need to install again.  Verfiy command output contains `SUCCESS: Finished install:` or `Finished installing software` and consider the install failed if this is not present.
  * Print out debug command output from install command if Ansible in `--verbose` mode
  * Use NetCMS Makefile to perform a `make {{ inventory_hostname }}.check` and fail if there are any unexpected config changes
* Catalyst 3K IOS process if the running version does not match the Netbox Config Context `ios_version`
  * Parse `show boot` using `templates/cisco_ios_show_boot` and save as `cisco_ios_facts`
  * Print out debug message showing intended change summary if Ansible in `--verbose` mode
  * Install and overwrite new IOS directly over the network using HTTP (flash is not large enough for more than one copy of IOS on many models) set to be active on next boot, only if the boot version matches the currently running version, otherwise deployment has already been done and the reboot is pending, we don't need to install again. Verify command output contains `All software images installed` and consider the install failed if this is not present.
  * Print out debug command output from archive command if Ansible in `--verbose` mode
  * Use NetCMS Makefile to perform a `make {{ inventory_hostname }}.check` and fail if there are any unexpected config changes
* Nexus NXOS if the running version does not match the Netbox Config Context `nxos_version` and `show boot` does not match `nxos_bin` filename showing that the intended `nxos_bin` is not already deployed
  * Parse `show_boot` using `template/cisco_nxos_show_boot.yml` and store in `cisco_nxos_facts` including number of supervisors
  * Check `bootflash:` and `bootflash://sup-standby/` MD5 if `nxos_bin`, `nxos_kickstart_bin` and `nxos_epld_bin` area already copied
  * Copy `nxox_bin`, `nxos_kickstart_bin` and `nxos_epld_bin` to `bootflash:` if those files are defined in the Netbox Configuration Context and don't already exist, copy `nxos_epld_bin` to `bootflash://sup-standby/` if a second supervisor exists
  * Install new NXOS from `bootflash:` with `no-reload` so it is set to be active on next boot.  Verify command output on N9K and N9K-C93xxx contains `Install has been successful.` or consider the install process a failure, do not check output on N9K-C95xx chassis as the output does not seem to include a final status msessage.
  * Copy running-config to startup-config as the install process changes the `boot` statement in the configuration if an install was performed, check output for `Copy complete`.
  * Use NetCMS Makefile to perform a `make {{ inventory_hostname }}.update` to check in the config change to the boot statement
  * Print out debug messages showing output from install commands if Ansible in `--verbose` mode


### Ansible Reload workflow

`network-firmware-reload.yml` Can operate on Catalyst and Nexus family devices, although testing is not complete on
Catalyst 4500X, Nexus 5000, 6000, 7000, 7700 family devices, and will reload the device if it has been provisioned
with different base OS firmware than it is currently running.  The `network-firmware-reload.yml` playbook also includes
the `network-users.yml` playbook which will set the local `emerg` account and `enable` credentials using the strongest
supported password hash available on the device, after the device reload completes.  On the Catalyst platform there are
two reload methods, the default which will `reload in 2`, scheduling a reload for two minutes in the future, to give
enough time for parallel Ansible workers to issue their reload commands if there are any aggregation devices in the same
batch before devices lose connectivty, and `reload at HH:MM` which has a prompt to input a time and will exit the
playbook without doing any of post-reboot checks.  On the Nexus platform there are seperate steps for updating EPLD
firmware, which can cause line cards to reload and drop connectivity on the management SSH connection and on some models
can induce a full system reload, as well as a `reload time 30` command to explicitly reload in 30s when the EPLD updates
are unnecessary or do not trigger a reload themselves.  After the devices reload they have their `show version` data
gathered again with [ios_facts](https://docs.ansible.com/ansible/latest/collections/cisco/ios/ios_facts_module.html) or
[nxos_facts](https://docs.ansible.com/ansible/latest/collections/cisco/nxos/nxos_facts_module.html and compared to the
configured Netbox Platform and Configuration Context data to make sure they are now running the correct version, if not
that is considered a failure.  Successfully upgraded devices are then checked in using NetCMS `make {{ inventory_hostname }}.update`.

* Set `doit_needsreboot` flag to False
* Parse `show version` and related commands using [ios_facts](https://docs.ansible.com/ansible/latest/collections/cisco/ios/ios_facts_module.html) or [nxos_facts](https://docs.ansible.com/ansible/latest/collections/cisco/nxos/nxos_facts_module.html)
* Catalyst 4K IOS-XE process if the running version does not match the Netbox Config Context `ios_version`
  * Verfiy MD5 of `bootflash:` files `ios_bin` and `ios_rommon`
  * Parse `show bootvar` using `templates/cisco_ios_show_bootvar.yml` and save to `cisco_ios_facts`
  * Print out debug message showing intended change summary if Ansible in `--verbose` mode
  * Set `doit_needsreboot` flag to True `when: "doit_check_firmware.failed is false and ansible_net_image not in cisco_ios_facts.ansible_boot_variable"` if the version it would boot on the next reload is not the version it is currently running then it is eligible to reload
* Catalyst 3K 9k IOS-XE process if the running version does not match the Netbox Config Context `ios_version`
  * Parse `show version provisioned` using `templates/cisco_ios_show_version_provisioned.yml` and save as `cisco_ios_facts`
  * Print out debug message showing intended change summary if Ansible in `--verbose` mode
  * Set `doit_needsreboot` flag to True `when: "ansible_net_version != cisco_ios_facts.ansible_provisioned_version"` if the version it would boot on the next reload is not the version it is currently running then it is eligible to reload.
* Catalyst 3K IOS process if the running version does not match the Netbox Config Context `ios_version`
  * Parse `show boot` using `templates/cisco_ios_show_boot` and save as `cisco_ios_facts`
  * Print out debug message showing intended change summary if Ansible in `--verbose` mode
  * Set `doit_needsreboot` flag to True ` when: "ansible_net_image != cisco_ios_facts.ansible_boot_image"` if the version it would boot on the next reload is not the version it is currently running then it is eligible to reload
* Nexus NXOS process if the running version does not match the Netbox Config Context `nxos_version`
  * Parse `show_boot` using `template/cisco_nxos_show_boot.yml` and store in `cisco_nxos_facts` including number of supervisors
  * Check `bootflash:` and `bootflash://sup-standby/` MD5 if `nxos_bin`, `nxos_kickstart_bin` and `nxos_epld_bin` area successfully copied
  * Print out debug message showing intended change summary if Ansible in `--verbose` mode
  * Set `doit_needsreboot` flag to True `when: "doit_check_firmware_nxos.failed is false"` if the new NXOS firmware is on the `bootflash:` instead of checking if a new version is provisioned to boot as installing firmware can be disruptive on this platform and some of the steps should occur during a maintenance window.
* Catalyst family if `reload_time` has a `HH:MM` timestamp and `doit_needsreboot` is True then issue `reload at {{ reload_time }}` and exit the playbook
* Catalyst family if `doit_needsreboot` is True and `reload_time` is not set then prepare to reload now
  * Use NetCMS Makefile to perform a `make {{ inventory_hostname }}.check` and fail if there are any unexpected config changes
  * Ensure config is saved with `write memory` (which should make no change as we already performed a make.check) and `reload in 2` with a templated reason to be syslogged
  * [`wait_for`](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/wait_for_module.html) the device to come back online, start checking port 22/tcp for connectivity after 180s (3m) and continue checking for up to 3600s (1h), proceeding with playbook after all hosts in the batch are back online and their management service (SSH) is reachable
  * Parse `show version` and related commands using [ios_facts](https://docs.ansible.com/ansible/latest/collections/cisco/ios/ios_facts_module.html)
  * Assert that the running version now matches the version in the Netbox Config Context `ios_version` or fail
  * Use NetCMS Makefile to perform a `make {{ inventory_hostname }}.update` to check in all the config syntax changes after successfully upgrading to a new version of code
  * Clean old firmware files from flash to free space, now that we have successfully booted onto a new version
  * On Catalyst 4500X remove the ROMMON installer from the boot variable
* Nexus family if `doit_needsreboot` is True
  * Use NetCMS Makefile to perform a `make {{ inventory_hostname }}.check` and fail if there are any unexpected config changes
  * Install new NXOS from `bootflash:` and allow the switch to reload, if the file in `nxos_bin` is not listed in the `show boot` output showing that the new version install process hasn't been completed yet, eg. the firmware was deployed by some other mechanism
  or the install process during the staging playbook wasn't successful, which should be unlikely in practice.
  * [`wait_for`](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/wait_for_module.html) the device to come back if the `nxos_bin` file is not listed in the `show boot` output, start checking port 22/tcp for connectivity after 60s (1m) and continue checking for up to 3600s (1h), which should not occur if the install process was already run during the staging playbook.
  * IF `nxos_epld_bin` is defined for this device then `install all epld` from `bootflash:` answering `y\ry` to the multiple prompts issued by the install process with a command timeout of 900s (15m) as it is possible on some models for EPLD install to interrupt the SSH session, causing Ansible to not see the command prompt return and be able to tell whether the command sucessfully completed, it has to wait for the timeout to expire to know the persistent SSH management connection has failed, and to ensure that the EPLD update has completed in the background. The playbook task then needs to ignore that failure to proceed with the rest of the steps.
  * [`wait_for`](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/wait_for_module.html) the device to come back, start checking port 22/tcp for connectivity after 60s (1m) and continue checking for up to 3600s (1h), which should not have to wait unless the EPLD update was required and caused a traffic interruption in our path to SSH management
  * If `nxos_epld_bin` is defined for this device then `install all epld module all golden` from `bootflash:` with a command timeout of 600s (10m) as it is likely on many models for the EPLD golden update to cause the device to reload, causing Ansible to not see the command prompt return and be able to tell whether the command sucessfully completed, it has to wait for the timeout to expire to know the persistent SSH management connection has failed, and to ensure that the EPLD golden update has completed in the background.  The playbook task then needs to ignore that failure to proceed with the rest of the steps.
  * [`wait_for`](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/wait_for_module.html) the device to come back, start checking port 22/tcp for connectivity after 60s (1m) and continue checking for up to 3600s (1h), which is likely to be necessary if the golden EPLD were in need of update and the device reloads.
  * Parse `show version` and related commands using [nxos_facts](https://docs.ansible.com/ansible/latest/collections/cisco/nxos/nxos_facts_module.html)
  * Check `when: "ansible_net_version != config_context[0].nxos_version"` to find devices that have not yet reloaded due to one of the previous EPLD updates and issue `reload timer 30`, devices should only need to be reloaded once to boot into a new NXOS image
  * [`wait_for`](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/wait_for_module.html) the device to come back, start checking port 22/tcp for connectivity after 60s (1m) and continue checking for up to 3600s (1h), if it was issued an explicit reload
  * Parse `show version` and related commands using [nxos_facts](https://docs.ansible.com/ansible/latest/collections/cisco/nxos/nxos_facts_module.html) if it was issued an explicit relaod
  * Assert that the running version now matches the version in the Netbox Config Context `nxos_version` or fail
  * Settle dowm timeout, [`wait_for`](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/wait_for_module.html) the device for 120s (2m) by default or 600s (10m) for Nexus 9500 Chassis family devices to ensure that all modules and line cards are active, the mangement plane can be accessible long before all the data plane has initialized on this platform
  * Copy running-config to startup-config to save any config syntax changes after successfully upgrading to a new version of code, requires all installed modules to be active before this command can be issued
  * Use NetCMS Makefile to perform a `make {{ inventory_hostname }}.update` to check in all the config syntax changes after successfully upgrading to a new version of code

Organizing the devices needing a reboot into groups using `--limit` directives (by model, location, name, etc.) or
manually curated lists can be a mechanism for an engineer to limit disruption and reduce risk of failure in the datacenter
Nexus devices by reloading HA Primary devices first then HA Active/Standby,
ensuring that the Primary device will be in charge of HA after updates copmlete, and reloading radial aggregation devices
successfully before attempting to reload the access devices that rely on the radial aggregation devices for management connectivity.
In our practice this lead to organizing the devices into four (4) batches, primary first-in-building devices, secondary
first-in-building devices, primary next-in-building devices and secondary next-in-building devices, with the
[serial keyword](https://docs.ansible.com/ansible/latest/user_guide/playbooks_strategies.html) in the playbook set large
enough that all devices in a batch would be operated on at the same time, so that the total time needed in a maintenance
window was 4x the time it took to upgrade the slowest device model eligible for reload.  In this example the device lists
are provided on the command line by joining with `:` but could also be provided in a file with `--limit @filename`.

```bash
# Batch 1 Primary first-in
./netbox-playbook.sh ./network-firmware-reload.yml --verbose --limit 'sn-432nm-b3a-4-node-pri130n:sn-ddn1220cc-212b-2-access-pri114n:sn-ddnanimal-226-1-access-pri104n:sn-ddnbiochem-b1129-1-access-pri160n:sn-ddnchmbrln-3216-1-access-pri181n:sn-ddnedbldg-l296-1-access-pri127n:sn-ddnfemrite-113b-1-radial-pri210n:sn-ddngenbio-b1110-4-access-pri113n:sn-ddnhslc-2161-2-access:sn-ddnmemlib-541c-1-access-pri121n:sn-ddnrussl-b30-1-access-pri76n:sn-ddnwarfplat-b156vv11-1-radial-pri81n:sn-ddnwidmir-b1228-1-access-pri205n' --check
# Batch 2 Secondary first-in
./netbox-playbook.sh ./network-firmware-reload.yml --verbose --limit 'sn-animal-226-4-node-act130n:sn-ddn1220cc-212b-3-access-act114n:sn-ddnanimal-226-2-access-act104n:sn-ddnbiochem-b1129-2-access-act160n:sn-ddnchmbrln-3216-2-access-act181n:sn-ddnedbldg-l296-2-access-act127n:sn-ddnfemrite-113w-2-radial-act210n:sn-ddngenbio-b1110-5-access-act113n:sn-ddnmemlib-541c-2-access-act121n:sn-ddnrussl-b30-2-access-act76n:sn-ddnwarfplat-b156vv11-2-radial-act81n:sn-ddnwidmir-b1228-2-access-act205n' --check
# Batch 3 Primary internal
./netbox-playbook.sh ./network-firmware-reload.yml --verbose --limit 'sn-cssc-b380g12-8-node-pri132n:sn-cssc-b380g14-1-node-pri135n:sn-animal-226-7-node-pri110n:sn-ddnfemrite-113c-1-access-pri212n:sn-ddnfemrite-113d-1-access-pri211n:sn-ddnfemrite-113s-1-access-pri214n:sn-ddnfemrite-113u-1-access-pri213n:sn-ddnwarfplat-b156vv03-1-access-pri78n:sn-ddnwarfplat-b156vv05-1-access-pri79n:sn-ddnwarfplat-b156vv06-3-access-pri80n:sn-ddnwarfplat-b156vv10-1-access-pri82n' --check
# Batch 4 Secondary internal
./netbox-playbook.sh ./network-firmware-reload.yml --verbose --limit 'sn-432nm-b3a-8-node-act132n:sn-432nm-b3a-2-node-act135n:sn-cssc-b380g14-7-node-act110n:sn-ddnfemrite-113c-2-access-act212n:sn-ddnfemrite-113d-2-access-act211n:sn-ddnfemrite-113s-2-access-act214n:sn-ddnfemrite-113u-2-access-act213n:sn-ddnwarfplat-b156vv03-2-access-act78n:sn-ddnwarfplat-b156vv05-2-access-act79n:sn-ddnwarfplat-b156vv06-4-access-act80n:sn-ddnwarfplat-b156vv10-2-access-act82n' --check

```

A different approach may be needed for updates to Catalyst family devices, splitting the device name on `-` to get the number
and using a jinja filter to test if the `int is odd` to reload all odd numbered devices, then run through
the playbook again to reload all even numbered devices, to catch cases where there are multiple switch stacks in
an IDF and our downstream customers may, without the automation's ability to know, be expecting high availability between
the independant switch stacks.  Four batches would be had by reloading all odd-numbered radials, then all even-numbered
radials, then odd-numbered access and even-numbered access devices.

```bash
# Batch 1 first-in primary devices
./netbox-playbook.sh ./network-firmware-reload.yml --verbose --check --limit 'sites_cssc:&*-b217-*:&device_roles_radial' --extra-vars 'reload_time="" evenodd="odd"'
# Batch 2 first-in secondary devices
./netbox-playbook.sh ./network-firmware-reload.yml --verbose --check --limit 'sites_cssc:&*-b217-*:&device_roles_radial' --extra-vars 'reload_time="" evenodd="even"'
# Batch 3 internal primary devices
./netbox-playbook.sh ./network-firmware-reload.yml --verbose --check --limit 'sites_cssc:&*-b217-*:&device_roles_access' --extra-vars 'reload_time="" evenodd="odd"'
# Batch 4 internal secondary devices
./netbox-playbook.sh ./network-firmware-reload.yml --verbose --check --limit 'sites_cssc:&*-b217-*:&device_roles_access' --extra-vars 'reload_time="" evenodd="even"'
```


### Tasks Network Device Firmware/Software Management

- network-firmware placeholder (Tags: [] [])

## Play IOS Code Deployment

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `all`
- Tags: []

 Play imported from [network-firmware-stage.yml](network-firmware-stage.md)

## Play IOS Code Reload

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `all`
- Tags: []

 Play imported from [network-firmware-reload.yml](network-firmware-reload.md)
