
# Playbook `network-opennms-test.yml`

[TOC]

- [DoIT NS Internal KB https://kb.wisc.edu/ns/internal](https://kb.wisc.edu/ns/internal/network-opennms-test)
- [Gitlab Documentation Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/docs/network-opennms-test.md)
- [Gitlab Playbook Source https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master](https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master/ansible/network-opennms-test.yml)


## Play OpenNMS Dummy Testhosts

- [Hosts](https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html): `localhost`
- Tags: []

Create large number of dummy test hosts for OpenNMS PoC

Make a range of OpenNMS Node records that have the same ip-addr
as a ping target, so we can validate performance of large numbers
of alarm events happening in a short time frame, simulating a large
network outage or partition from the monitoring system network.

Enable HTTP-APITest service to check performance of polling when
a large number of TCP services timeout, does it fill up queues/threads
and create performance problems for the rest of the monitoring?

Edit the range in the loop to change the number of nodes created

NB: requisitions responds with 202 Accepted when adding new nodes

Using the `uri` module with `force_basic_auth: true` so we don't
waste resources following the HTTP 401 with a second request with credentials.

Delete the `Test` requisition when finished testing


### Tasks OpenNMS Dummy Testhosts

- Provision Test Requisitoin (Tags: [] [])
