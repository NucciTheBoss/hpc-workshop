#!/usr/bin/env python3
# Copyright 2022 Jason C. Nucciarone
# See LICENSE file for licensing details.

"""Init command for bootstrapping the HPC cluster."""

from __future__ import annotations

import subprocess
import sys
import textwrap
import warnings
from typing import Optional

from craft_cli import BaseCommand, CraftError, emit
from pylxd import Client

if not sys.warnoptions:
    warnings.simplefilter("ignore")


class _InitHandler:
    def __init__(self, compute: int) -> None:
        self.client = Client()
        self.base_name = "base"
        self.base_config = {
            "name": self.base_name,
            "source": {
                "type": "image",
                "mode": "pull",
                "server": "https://images.linuxcontainers.org",
                "protocol": "simplestreams",
                "alias": "ubuntu/jammy",
            },
            "project": "default",
        }
        self.nodes = ["ldap-0", "nfs-0", "head-0"]
        self.nodes.extend([f"compute-{i}" for i in range(0, compute)])

    def bootstrap(self) -> None:
        """Bootstrap cluster for end-users."""
        emit.progress("Booting base image...", permanent=True)
        self.client.instances.create(self.base_config, wait=True)
        instance = self.client.instances.get(self.base_name)
        instance.start(wait=True)
        instance.execute(["apt", "update"])
        instance.execute(["apt", "upgrade", "-y"])

        emit.progress("Installing SLURM inside base image...", permanent=True)
        instance.execute(["apt", "install", "-y", "slurmd", "slurmctld"])
        instance.execute(["systemctl", "disable", "slurmctld", "slurmd", "munge"])

        emit.progress("Installing LDAP and SSSD inside base image...", permanent=True)
        instance.execute(
            ["apt", "install", "-y", "slapd", "ldap-utils", "sssd-ldap"],
            environment={"DEBIAN_FRONTEND": "noninteractive"},
        )
        instance.execute(["systemctl", "disable", "slapd", "sssd-ldap"])

        emit.progress("Installing NFS inside base image...", permanent=True)
        instance.execute(["apt", "install", "-y", "nfs-kernel-server", "nfs-common"])
        instance.execute(["systemctl", "disable", "nfs-kernel-server"])

        emit.progress("Installing Lmod inside base image...", permanent=True)
        instance.execute(
            [
                "apt",
                "install",
                "-y",
                "wget",
                "build-essential",
                "lua5.3",
                "lua-bit32:amd64",
                "lua-posix:amd64",
                "lua-posix-dev",
                "liblua5.3-0:amd64",
                "liblua5.3-dev:amd64",
                "tcl",
                "tcl-dev",
                "tcl8.6",
                "tcl8.6-dev:amd64",
                "libtcl8.6:amd64",
            ]
        )
        instance.execute(
            [
                "wget",
                "https://github.com/TACC/Lmod/archive/refs/tags/8.7.13.tar.gz",
                "-P",
                "/root",
            ]
        )
        instance.execute(["tar", "-xzf", "/root/8.7.13.tar.gz", "-C", "/root"])
        instance.execute(["./configure", "--prefix=/opt/apps"], cwd="/root/Lmod-8.7.13")
        instance.execute(["make", "-C", "/root/Lmod-8.7.13", "install"])
        instance.execute(
            [
                "ln",
                "-s",
                "/opt/apps/lmod/lmod/init/profile",
                "/etc/profile.d/z00_lmod.sh",
            ]
        )
        instance.execute(["echo", "/opt/sw/modules", ">", "/opt/apps/lmod/lmod/init/.modulespath"])
        instance.execute(["chmod", "-R", "ugo+rx", "/opt/apps/lmod"])
        instance.execute(["chmod", "-R", "u+w", "/opt/apps/lmod"])

        emit.progress("Installing Apptainer inside base image...", permanent=True)
        instance.execute(
            [
                "wget",
                "https://dl.google.com/go/go1.19.2.linux-amd64.tar.gz",
                "-P",
                "/root",
            ]
        )
        instance.execute(["tar", "-xzf", "/root/go1.19.2.linux-amd64.tar.gz", "-C", "/usr/local"])
        instance.execute(["ln", "-s", "/usr/local/go/bin/go", "/usr/local/bin/go"])
        instance.execute(["ln", "-s", "/usr/local/go/bin/gofmt", "/usr/local/bin/gofmt"])
        instance.execute(
            [
                "apt",
                "install",
                "-y",
                "build-essential",
                "libseccomp-dev",
                "pkg-config",
                "uidmap",
                "squashfs-tools",
                "squashfuse",
                "fuse2fs",
                "fuse-overlayfs",
                "fakeroot",
                "cryptsetup",
                "curl",
                "git",
            ]
        )
        instance.execute(
            [
                "git",
                "clone",
                "https://github.com/apptainer/apptainer.git",
                "/root/apptainer",
            ]
        )
        instance.execute(["git", "checkout", "v1.1.3"], cwd="/root/apptainer")
        instance.execute(["./mconfig", "--prefix=/opt/sw/apptainer"], cwd="/root/apptainer")
        instance.execute(["make"], cwd="/root/apptainer/builddir")
        instance.execute(["make", "install"], cwd="/root/apptainer/builddir")

        emit.progress("Setting up LXD profiles...", permanent=True)
        self.client.profiles.create("micro-hpc", config={"security.privileged": "true"})
        self.client.profiles.create(
            "nfs",
            config={"raw.apparmor": "mount fstype=nfs*, mount fstype=rpc_pipefs,"},
        )

        emit.progress("Creating nodes for the HPC cluster...", permanent=True)
        for node in self.nodes:
            try:
                subprocess.run(
                    ["lxc", "copy", self.base_name, node, "--instance-only"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True,
                )
                instance = self.client.instances.get(node)
                instance.start(wait=True)
                self._apply_profiles(node)
            except subprocess.CalledProcessError as e:
                emit.error(f"Failed to create node {node}. Reason {e}")

        instance = self.client.instances.get(self.base_name)
        instance.stop(wait=True)
        instance.delete(wait=True)

    def _apply_profiles(self, node: str) -> None:
        def add_micro_hpc(node_name: str) -> None:
            subprocess.run(
                ["lxc", "profile", "add", node_name, "micro-hpc"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )

        def add_micro_hpc_and_nfs(node_name: str) -> None:
            add_micro_hpc(node_name)
            subprocess.run(
                ["lxc", "profile", "add", node_name, "nfs"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )

        dispatch = {
            "ldap": add_micro_hpc,
            "nfs": add_micro_hpc_and_nfs,
            "head": add_micro_hpc_and_nfs,
            "compute": add_micro_hpc_and_nfs,
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
