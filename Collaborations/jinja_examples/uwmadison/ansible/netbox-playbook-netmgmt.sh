#! /bin/bash
#
# Set up environment for Ansible Netbox integration
#

WORKERS="$(( $(nproc) * 2 ))"
FULLPATH=$(readlink -f "$0")
DIRNAME=$(dirname "${FULLPATH}")
NETBOX_DEVINFO="${NETBOX_DEVINFO:-netbox-prod}"

export ANSIBLE_HOST_KEY_AUTO_ADD=true
export ANSIBLE_PARAMIKO_LOOK_FOR_KEYS=false
export ANSIBLE_NETWORK_IMPORT_MODULES=yes
export ANSIBLE_PIPELINING=true
export ANSIBLE_DISPLAY_ARGS_TO_STDOUT=true
#export ANSIBLE_LOG_PATH=~/ansible.log
#export ANSIBLE_PERSISTENT_LOG_MESSAGES=true

DEVINFORC="${DIRNAME}/secrets/devinforc"
export DEVINFORC
NETBOX_API=$(/usr/local/ns/bin/devinfo -j "$NETBOX_DEVINFO" | jq -r '.connection_method + "://" + .attributes.host + ":" + .attributes.port + "/"')
export NETBOX_API
NETBOX_TOKEN=$(/usr/local/ns/bin/devinfo -p "$NETBOX_DEVINFO")
export NETBOX_TOKEN

exec ansible-playbook --inventory "${DIRNAME}/netbox_inventory_netmgmt.yml" --inventory "${DIRNAME}/hosts.yml" --forks "${WORKERS}" --diff "${@}"
