# Sharing is caring

Right now, all of the nodes in our micro-HPC cluster are relatively operating independently 
operating of one another; a file created on one node is not shared amongst the other nodes. This makes it difficult 
impossible to have many of thousands of nodes operating on the same data set. Luckily, we have 
*[Network File System](https://en.wikipedia.org/wiki/Network_File_System)*, also known as NFS, to help us sync our data
across the cluster.

## Setting up user `test`'s directories

First, we need to set up user `test`'s directories and keys so they can use our micro-HPC cluster. Start a shell session
on the `nfs-0` node:

```text
$ lxc shell nfs-0
```

Now, inside `nfs-0`, create a directory for `test` under `/data`. This is where `test` will store all their files and
code needed for their research. They will also need a home directory once they finally log onto the system:

```text
~# mkdir -p /data/test
~# mkdir -p /home/test
~# chown -R test:test /data/test
~# chown -R test:test /home/test
~# chmod 0755 /data
~# chmod -R 0750 /data/test
~# chmod -R 0740 /home/test
~# ln -s /data/test /home/test/data
```

## Configuring what is shared by `nfs-0`

With user `test` all set up on `nfs-0`, now it is time to configure how NFS exports directories on your system. 
Open a text editor window using the following command `nfs-0`, but make sure that you are logged in as user `root` 
rather than `test`:

```text
~# nano /etc/exports
```

Populate `/etc/exports` with the content below:

```text
/srv     *(ro,sync,subtree_check)
/home    *(rw,sync,no_subtree_check)
/data    *(rw,sync,no_subtree_check,no_root_squash)
/opt     *(rw,sync,no_subtree_check,no_root_squash)
```

Save and close the file and then start the NFS server:

```text
~# systemctl enable nfs-kernel-server
~# systemctl start nfs-kernel-server
~# exportfs -a
```


## Mounting the shared directories

With your NFS server all set to go, now it is time to mount the shared directories inside the instances that need to 
consume those directories. In our case, these nodes will be `compute-0` and `head-0`. To get started, grab the IPv4 
address of `nfs-0` using the following command:

```text
$ lxc list -c n4 -f compact | grep nfs
```

Now to save ourselves some grief, let us use a bash for loop to mount the shared drives in both `head-0` and 
`compute-0`:

```text
$ nodes=( compute-0 head-0 )
$ NFS_SERVER_IP=10.5.1.120
$ for i in ${nodes[@]}; do
    lxc exec $i -- mount $NFS_SERVER_IP:/home /home
    lxc exec $i -- mount $NFS_SERVER_IP:/data /data
    lxc exec $i -- mount $NFS_SERVER_IP:/opt /opt
  done
```

Now onto setting up our resource management software.
