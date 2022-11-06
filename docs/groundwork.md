# So what will we be doing?

We are going to be building an HPC cluster with LXD! Well... not really. We will be building a psuedo-HPC cluster, or as I like to call it, a *micro-HPC cluster*. I got the idea for the name from another popular project: [Microstack](https://microstack.run). True HPC clusters can fill an entire building; ours will just be a few LXD containers on your laptop.

## Setting up LXD on your system

LXD will serve as the undercloud for our HPC cluster. If you do not already have LXD installed on your system, use the following command to install the LXD snap package:

```text
$ sudo snap install lxd
```

With the snap installed, set up LXD on your system with the following configuration options:

```text
$ lxd init

Would you like to use LXD clustering? (yes/no) [default=no]: 
Do you want to configure a new storage pool? (yes/no) [default=yes]: 
Name of the new storage pool [default=default]: micro-hpc 
Name of the storage backend to use (lvm, zfs, ceph, btrfs, dir) [default=zfs]: 
Create a new ZFS pool? (yes/no) [default=yes]: 
Would you like to use an existing empty block device (e.g. a disk or partition)? (yes/no) [default=no]: 
Size in GB of the new loop device (1GB minimum) [default=27GB]: 60GB
Would you like to connect to a MAAS server? (yes/no) [default=no]: 
Would you like to create a new local network bridge? (yes/no) [default=yes]: 
What should the new bridge be called? [default=lxdbr0]: 
What IPv4 address should be used? (CIDR subnet notation, “auto” or “none”) [default=auto]: 
What IPv6 address should be used? (CIDR subnet notation, “auto” or “none”) [default=auto]: 
Would you like the LXD server to be available over the network? (yes/no) [default=no]: 
Would you like stale cached images to be updated automatically? (yes/no) [default=yes]: 
Would you like a YAML "lxd init" preseed to be printed? (yes/no) [default=no]:
```

## Getting the `hpc-workshop` pip package

To make things go a "faster", I have written a small program to handle setting up what you will need for the micro-HPC cluster to work. It can be installed as pip package from PyPI:

```text
$ pip install hpc-workshop
```

After installing the package, you should be able to access the `hpc-workshop` command.

> __Note:__ You may have to run the command `export PATH=$HOME/.local/bin:$PATH` to access the `hpc-workshop` executable.

## Bootstrapping your cluster

With `hpc-workshop` installed, all you to do is execute the following command:

```text
$ hpc-workshop init
```

Yes, really, it is that simple! Now onto creating our cluster's user.
