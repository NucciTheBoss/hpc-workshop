#!/usr/bin/env python3
# Copyright 2022 Jason C. Nucciarone
# See LICENSE file for licensing details.

"""Init command for bootstrapping the HPC cluster."""

from __future__ import annotations

import subprocess
import sys
import textwrap
import warnings
from time import sleep
from typing import Any, Optional

from craft_cli import BaseCommand, CraftError, emit

if not sys.warnoptions:
    warnings.simplefilter("ignore")


def _execute(command: str | list) -> None:
    command = command.split(" ") if type(command) == str else command
    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


class _InitHandler:
    def __init__(self, compute: int) -> None:
        self.base_name = "base"
        self.nodes = ["ldap-0", "nfs-0", "head-0"]
        self.nodes.extend([f"compute-{i}" for i in range(0, compute)])

    def bootstrap(self) -> None:
        """Bootstrap cluster for end-users."""
        emit.progress("Booting base image...", permanent=True)
        _execute(f"lxc launch images:ubuntu/jammy {self.base_name} --vm")
        sleep(10)
        _execute(f"lxc exec {self.base_name} -- apt update")
        _execute(f"lxc exec {self.base_name} -- apt upgrade -y")

        emit.progress("Installing SLURM inside base image...", permanent=True)
        _execute(f"lxc exec {self.base_name} -- apt install -y slurmd slurmctld")
        _execute(f"lxc exec {self.base_name} -- systemctl disable slurmctld slurmd munge")

        emit.progress("Installing LDAP and SSSD inside base image...", permanent=True)
        _execute(
            f"lxc exec --env DEBIAN_FRONTEND=noninteractive {self.base_name} -- apt install -y slapd ldap-utils "
            f"sssd-ldap"
        )
        _execute(f"lxc exec {self.base_name} -- systemctl disable slapd sssd")

        emit.progress("Installing NFS inside base image...", permanent=True)
        _execute(f"lxc exec {self.base_name} -- apt install -y nfs-kernel-server nfs-common")
        _execute(f"lxc exec {self.base_name} -- systemctl disable nfs-kernel-server")

        emit.progress("Installing Lmod inside base image...", permanent=True)
        _execute(
            f"lxc exec {self.base_name} -- apt install -y wget build-essential nano lua5.3 lua-bit32:amd64 "
            f"lua-posix:amd64 lua-posix-dev liblua5.3-0:amd64 liblua5.3-dev:amd64 tcl tcl-dev tcl8.6 "
            f"tcl8.6-dev:amd64 libtcl8.6:amd64"
        )
        _execute(
            f"lxc exec {self.base_name} -- wget https://github.com/TACC/Lmod/archive/refs/tags/8.7.13.tar.gz -P "
            f"/root"
        )
        _execute(f"lxc exec --cwd /root {self.base_name} -- tar -xzf 8.7.13.tar.gz")
        _execute(
            f"lxc exec --cwd /root/Lmod-8.7.13 {self.base_name} -- ./configure --prefix=/opt/apps"
        )
        _execute(f"lxc exec {self.base_name} -- make -C /root/Lmod-8.7.13 install")
        _execute(
            f"lxc exec {self.base_name} -- ln -s /opt/apps/lmod/lmod/init/profile /etc/profile.d/z00_lmod.sh"
        )
        _execute(f"lxc exec {self.base_name} -- chmod -R ugo+rx /opt/apps/lmod")
        _execute(f"lxc exec {self.base_name} -- chmod -R u+w /opt/apps/lmod")
        # instance.execute(["echo", "/opt/sw/modules", ">", "/opt/apps/lmod/lmod/init/.modulespath"])

        emit.progress("Installing Apptainer inside base image...", permanent=True)
        _execute(
            f"lxc exec {self.base_name} -- wget https://dl.google.com/go/go1.19.2.linux-amd64.tar.gz -P /root"
        )
        _execute(
            f"lxc exec {self.base_name} -- tar -xzf /root/go1.19.2.linux-amd64.tar.gz -C /usr/local"
        )
        _execute(f"lxc exec {self.base_name} -- ln -s /usr/local/go/bin/go /usr/local/bin/go")
        _execute(
            f"lxc exec {self.base_name} -- ln -s /usr/local/go/bin/gofmt /usr/local/bin/gofmt"
        )
        _execute(
            f"lxc exec {self.base_name} -- apt install -y build-essential libseccomp-dev pkg-config uidmap "
            f"squashfs-tools squashfuse fuse2fs fuse-overlayfs fakeroot cryptsetup curl git"
        )
        _execute(
            f"lxc exec {self.base_name} -- git clone https://github.com/apptainer/apptainer.git /root/apptainer"
        )
        _execute(f"lxc exec {self.base_name} --cwd /root/apptainer -- git checkout v1.1.3")
        _execute(
            f"lxc exec --cwd /root/apptainer {self.base_name} -- ./mconfig --prefix=/opt/sw/apptainer"
        )
        _execute(f"lxc exec {self.base_name} -- make -C /root/apptainer/builddir")
        _execute(f"lxc exec {self.base_name} -- make -C /root/apptainer/builddir install")

        emit.progress("Setting up LXD profiles...", permanent=True)
        _execute("lxc profile create micro-hpc")
        _execute("lxc profile set micro-hpc limits.cpu 1")
        _execute("lxc profile set micro-hpc limits.memory 2GB")
        _execute("lxc profile create nfs")
        _execute("lxc profile set nfs security.privileged true")
        _execute(["lxc", "profile", "set", "nfs", "raw.apparmor", "mount fstype=nfs*, mount fstype=rpc_pipefs,"])

        emit.progress("Creating nodes for the HPC cluster...", permanent=True)
        _execute(f"lxc stop {self.base_name}")
        for node in self.nodes:
            try:
                _execute(f"lxc copy {self.base_name} {node} --instance-only")
                self._apply_rules(node)
            except subprocess.CalledProcessError as e:
                emit.error(f"Failed to create node {node}. Reason {e}")

        _execute(f"lxc delete {self.base_name}")

    def _apply_rules(self, node: Any) -> None:
        """Rules to apply to specific nodes"""

        def start(node: str) -> None:
            _execute(f"lxc start {node}")
            sleep(10)
            _execute(f"lxc exec {node} -- rm -rf /root/8.7.13.tar.gz")
            _execute(f"lxc exec {node} -- rm -rf /root/Lmod-8.7.13")
            _execute(f"lxc exec {node} -- rm -rf /root/go1.19.2.linux-amd64.tar.gz")
            _execute(f"lxc exec {node} -- rm -rf /root/apptainer")

        def ldap_rules(node: str) -> None:
            _execute(f"lxc profile add {node} micro-hpc")
            start(node)
            _execute(f"lxc exec {node} -- rm -rf /opt/sw")
            _execute(f"lxc exec {node} -- rm -rf /opt/apps")

        def nfs_rules(node: str) -> None:
            _execute(f"lxc profile add {node} micro-hpc")
            _execute(f"lxc profile add {node} nfs")
            start(node)
            _execute(f"lxc exec {node} -- mkdir -p /data")
            _execute(f"lxc exec {node} -- mkdir -p /opt/sw/modules")

        def slurm_rules(node: Any) -> None:
            _execute(f"lxc profile add {node} micro-hpc")
            _execute(f"lxc profile add {node} nfs")
            start(node)
            _execute(f"lxc exec {node} -- rm -rf /opt/sw")
            _execute(f"lxc exec {node} -- rm -rf /opt/apps")
            _execute(f"lxc exec {node} -- mkdir -p /data")
            _execute(f"lxc restart {node}")

        dispatch = {
            "ldap": ldap_rules,
            "nfs": nfs_rules,
            "head": slurm_rules,
            "compute": slurm_rules,
        }
        dispatch[node.split("-")[0]](node)


class InitCommand(BaseCommand):
    """Initialize the micro-HPC cluster using LXD."""

    name = "init"
    help_msg = "Initialize micro-HPC cluster on localhost."
    overview = textwrap.dedent(
        """
        Initialize micro-HPC cluster on localhost.

        An LXD hypervisor will need to be set up on localhost before
        the cluster can be initialized or `init` will fail.

        The command will return successfully after the cluster has
        been initialized.
        """
    )

    def fill_parser(self, parser) -> None:
        """Arguments for init command."""
        parser.add_argument(
            "--compute",
            type=int,
            default=1,
            help="Number of compute nodes cluster should have.",
        )

    def run(self, parsed_args) -> Optional[int]:
        """Run steps to bootstrap cluster."""
        try:
            handler = _InitHandler(parsed_args.compute)
            handler.bootstrap()
            emit.ended_ok()
        except Exception as e:
            raise CraftError(f"A problem occurred when initializing the cluster: {e}")
