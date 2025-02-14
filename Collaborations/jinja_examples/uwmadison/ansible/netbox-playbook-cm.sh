#! /bin/bash
#
# Set up environment for Ansible Netbox integration
#
#source /usr/local/ns/etc/netcms
WORKERS="$(( $(nproc) * 2 ))"

NETBOX_DEVINFO="${NETBOX_DEVINFO:-netbox-prod}"
export ANSIBLE_HOST_KEY_AUTO_ADD=true
export ANSIBLE_PARAMIKO_LOOK_FOR_KEYS=false 
export ANSIBLE_NETWORK_IMPORT_MODULES=yes
export ANSIBLE_LOG_PATH=~/ansible.log
export ANSIBLE_PERSISTENT_LOG_MESSAGES=true
export NETBOX_API=$(/usr/local/ns/bin/devinfo -j "$NETBOX_DEVINFO" | jq -r '.connection_method + "://" + .attributes.host + ":" + .attributes.port + "/"')
export NETBOX_TOKEN=$(/usr/local/ns/bin/devinfo -p "$NETBOX_DEVINFO")

if [ -x /usr/bin/ansible-playbook-3 ]
then
ansible_playbook=/usr/bin/ansible-playbook-3
else
ansible_playbook=/usr/bin/ansible-playbook
fi

exec ${ansible_playbook} --inventory netbox_inventory_cm.yml --forks "${WORKERS}" --diff "${@}"
