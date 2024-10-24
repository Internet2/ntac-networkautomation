#! /bin/bash
#
# Set up environment for Ansible Netbox integration
#
#source /usr/local/ns/etc/netcms
FULLPATH=$(readlink -f "$0")
DIRNAME=$(dirname "${FULLPATH}")
NETBOX_DEVINFO="${NETBOX_DEVINFO:-netbox-prod}"
export ANSIBLE_HOST_KEY_AUTO_ADD=true
export ANSIBLE_NETWORK_IMPORT_MODULES=true
export ANSIBLE_PIPELINING=true
#export ANSIBLE_LOG_PATH=~/ansible.log
#export ANSIBLE_PERSISTENT_LOG_MESSAGES=true
NETBOX_API=$(/usr/local/ns/bin/devinfo -j "$NETBOX_DEVINFO" | jq -r '.connection_method + "://" + .attributes.host + ":" + .attributes.port + "/"')
NETBOX_TOKEN=$(/usr/local/ns/bin/devinfo -p "$NETBOX_DEVINFO")
export NETBOX_API NETBOX_TOKEN

exec /usr/bin/ansible-inventory --inventory "${DIRNAME}/netbox_inventory_voip.yml" --inventory "${DIRNAME}/hosts.yml" "${@}"
