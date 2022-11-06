# Workload Manager? Who needs it?

You do! Imagine if a thousand people requested all request resources at the same time. Without any way to delegate responsibility across all the nodes in cluster, it would be a complete dumpster fire. Nodes with 1 TB of RAM would be going to tasks that maybe only need a few megabytes. Folks would get upset very fast; no one wants to own the cluster with so much promise but wasted potential. To avoid this problem, we will be using [SLURM](https://slurm.schedmd.com/overview.html), also know as *Simple Linux Utility for Resource Management*.

## Setting up authentication with MUNGE

Before we can use SLURM on our cluster, we need to set up [MUNGE](https://dun.github.io/munge/), SLURM's companion authentication program. They MUNGE key file `munge.key` needs to be __exactly__ the same across all nodes being managed by SLURM. To synchronize the keys, first download `munge.key` from `head-0`:

```text
$ lxc file pull head-0/etc/munge/munge.key
```

With the `munge.key` file downloaded from `head-0`, use the following commands to set up the key file on `compute-0`:

```text
$ lxc file push munge.key compute-0/etc/munge/munge.key
$ lxc exec compute-0 -- chown munge:munge /etc/munge/munge.key
$ lxc exec compute-0 -- chmod 0600 /etc/munge/munge.key
```

Now start the MUNGE authentication services on both `compute-0` and `head-0`:

```text
$ lxc exec compute-0 -- systemctl enable munge
$ lxc exec compute-0 -- systemctl start munge
$ lxc exec head-0 -- systemctl enable munge
$ lxc exec head-0 -- systemctl start munge
```

## Getting groovy with node configuration

Now that we have MUNGE set up, grab the IPv4 address of both `compute-0` and `head-0` using the following command:

```text
$ lxc list -c n4 -f compact | grep -E "compute|head"
```

The output will look something similar to the output below:

```text
  compute-0         10.5.1.149 (eth0)  
  head-0            10.5.1.66 (eth0)
```

Now on your system, open a text editor window in your terminal:

```text
$ nano slurm.conf
```

Populate the file *slurm.conf* with the following information:

```text
SlurmctldHost=head-0(10.5.1.66)
ClusterName=micro-hpc

AuthType=auth/munge
FirstJobId=65536
InactiveLimit=120
JobCompType=jobcomp/filetxt
JobCompLoc=/var/log/slurm/jobcomp
ProctrackType=proctrack/linuxproc
KillWait=30
MaxJobCount=10000
MinJobAge=3600
ReturnToService=0
SchedulerType=sched/backfill
SlurmctldLogFile=/var/log/slurm/slurmctld.log
SlurmdLogFile=/var/log/slurm/slurmd.log
SlurmctldPort=7002
SlurmdPort=7003
SlurmdSpoolDir=/var/spool/slurmd.spool
StateSaveLocation=/var/spool/slurm.state
SwitchType=switch/none
TmpFS=/tmp
WaitTime=30

# Node Configurations
#
NodeName=compute-0 NodeAddr=10.5.1.149 CPUs=1 RealMemory=2000 TmpDisk=10000

# Partition Configurations
#
PartitionName=all Nodes=compute-0 MaxTime=30 MaxNodes=3 State=UP
```

> __Note:__ Ensure that you replace the IPv4 addresses I have above for both `compute-0` and `head-0` with the IPv4 addresses of the `compute-0` and `head-0` nodes on your system.

Save and close the file and then use the following commands to upload the *slurm.conf* file to both `compute-0` and `head-0`:

```text
$ lxc file push slurm.conf compute-0/etc/slurm/slurm.conf
$ lxc file push slurm.conf head-0/etc/slurm/slurm.conf
```

Now use the following commands to start the *slurmd* service on `compute-0` and the *slurmctld* service on `head-0`:

```text
$ lxc exec compute-0 -- systemctl enable slurmd
$ lxc exec compute-0 -- systemctl start slurmd
$ lxc exec head-0 -- systemctl enable slurmctld
$ lxc exec head-0 -- systemctl start slurmctld
```

Now onto making our software stack!
