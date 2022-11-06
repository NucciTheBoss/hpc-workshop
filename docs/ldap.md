# Who is going to use our cluster?

Obviously, we cannot let `root` be the sole user of our cluster - that would create a disaster. Therefore, to create a user, and have that user exists across all nodes within our micro-HPC cluster. To accomplish this, we will use [OpenLDAP](https://www.openldap.org), an open-source implementation of the *Lightweight Directory Access Protocol* (LDAP).

## Enabling the LDAP server on `ldap-0`

Before we can add our user to the cluster, we need to start the OpenLDAP server. Let us start a shell session inside the `ldap-0` node:

```text
$ lxc shell ldap-0
```

Now inside the `ldap-0` node, execute the following commands to start the OpenLDAP server:

```text
~# systemctl enable slapd
~# systemctl start slapd
```

We are not done yet, however, for we need to also configure the OpenLDAP server. Luckily, `dpkg-reconfigure` can handle most of the legwork for us:

```text
~# dpkg-reconfigure -f readline slapd
```

You will be taken through an interactive dialog to set up your server. Answer the prompts with the same answers as below:

```test
Omit OpenLDAP server configuration? [yes/no] no
DNS domain name: micro-hpc.org
Organization name: micro-hpc
Administrator password: test
Confirm password: test
Do you want your database to be removed when slapd is purged? [yes/no] yes
Move old database? [yes/no] yes
```

> __Note:__ For the password prompts, GNU readline will hide your inputs. Do not freak out when you do not see any characters appearing in the terminal when you are creating the adminstrator password.

## Creating user `test` and group `research` on the server

In a seperate terminal window on your system, open a text editor window. I used `nano` in my case:

```text
$ nano add_test_user.ldif
```

With the editor open, populate the file with the following LDIF (*LDAP Data Interchange Format*) content, and then save and close the file:

```text
dn: ou=People,dc=micro-hpc,dc=org
objectClass: organizationalUnit
ou: People

dn: ou=Groups,dc=micro-hpc,dc=org
objectClass: organizationalUnit
ou: Groups

dn: uid=test,ou=People,dc=micro-hpc,dc=org
uid: test
objectClass: inetOrgPerson
objectClass: posixAccount
cn: Test
sn: Test
givenName: Test
mail: test@example.com
userPassword: test
uidNumber: 10000
gidNumber: 10000
loginShell: /bin/bash
homeDirectory: /home/test

dn: cn=test,ou=Groups,dc=micro-hpc,dc=org
cn: test
objectClass: posixGroup
gidNumber: 10000
memberUid: nucci

dn: cn=research,ou=Groups,dc=micro-hpc,dc=org
cn: research
objectClass: posixGroup
gidNumber: 10100
memberUid: test
```

> __Important:__ Make sure the content in your LDIF file is exactly the same as the code block above.

With your LDIF file created, upload it into your `ldap-0` node using the following command:

```text
$ lxc file push add_test_user.ldif ldap-0/root/add_ldif_default.ldif
```

Go back into your terminal window with the activate shell session on `ldap-0`, and use the following command to add user `test` and group `research` to the OpenLDAP server:

```text
~# ldapadd -x -D "cn=admin,dc=micro-hpc,dc=org" -w test -f /root/add_test_user.ldif -H ldap:///
```

## Letting everyone else know about user `test`

Now we need to set up all the other nodes so that they know about user `test`. To accomplish this, we will use the *System Security Services Daemon*, also known as SSSD. First, we need to grab the IPv4 address of the `ldap-0` node. Execute the following command on your system:

```text
$ lxc list -c n4 -f compact | grep ldap
```

The output from the above command should look similar to the following output:

```text
ldap-0            10.5.1.44 (eth0)
```

With the IPv4 address of `ldap-0` in hand, open a text editor window:

```text
$ nano sssd.conf
```

Now populate the *sssd.conf* file with the following content:

```text
[sssd]
config_file_version = 2
domains = micro-hpc.org

[domain/micro-hpc.org]
id_provider = ldap
auth_provider = ldap
ldap_uri = ldap://10.5.1.44
cache_credentials = True
ldap_search_base = dc=micro-hpc,dc=org
```

> __Important:__ You should replace where I have my IPv4 address for `ldap-0` with the IPv4 adress of your `ldap-0` node.


We are almost there! One thing to note with SSSD is that it requires the *sssd.conf* file to have very specific access permissions. Also, these permissions need to be the same across all nodes connecting to the OpenLDAP server. Let us use some fancy bash scripting to make the set up a little easier on ourselves:

```text
$ nodes=( nfs-0 head-0 compute-0 )
$ for i in ${nodes[@]}; do
    lxc file push sssd.conf $i/etc/sssd/sssd.conf
    lxc exec $i -- chmod 0600 /etc/sssd/sssd.conf
    lxc exec $i -- chown root:root /etc/sssd/sssd.conf
    lxc exec $i -- pam-auth-update --enable mkhomedir
    lxc exec $i -- systemctl enable sssd
    lxc exec $i -- systemctl start sssd
  done
```

This for loop will save us a lot of copy, pasting, and changing a couple characters. Now onto setting up our shared file system!
