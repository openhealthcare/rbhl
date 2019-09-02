### Set up:

```
pip install -r requirements-dev.txt
```

### Deployment

Please ensure you have the correct pem file for the instances you hope to manage.
You will need to modify your working copy of deployment/ansible.cfg to set the location
of the pem file with the stanza:

```
[defaults]
private_key_file = ~/RBHL.pem
```

To create an set up a dev server
```
ansible-playbook setup_dev.yml
```

To create an set up a prod server
```
ansible-playbook setup_prod.yml
```

To restore from a back up. (Back ups run everyday at 20:00)
```
ansible-playbook restore.yml --extra-vars "S3_KEY={{LATEST S3 KEY}}"
```

To deploy to prod
```
ansible-playbook deploy_prod.yml
```

To deploy to dev
```
ansible-playbook deploy_dev.yml
```


## Cheatsheat: Incantations you may not remember

In this section we record various useful terminal incantations related to working
with these deployment scripts that you may find helpful.

### Encrypting variables

```
ansible-vault encrypt_string "my cool string"
```

### Viewing encrypted variables

Adjust the value of var= for the variable you want to view

```
ansible localhost -m debug -a var='DB_USER' -e "@group_vars/all"
```

### Generating random strings

```
openssl rand -base64 32
```
