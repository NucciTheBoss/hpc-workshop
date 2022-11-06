#!/usr/bin/env python3
# Copyright 2022 Jason C. Nucciarone
# See LICENSE file for licensing details.

"""Destroy command for cleaning up micro-HPC cluster."""

from __future__ import annotations

import sys
import textwrap
import warnings
from typing import Optional

from craft_cli import BaseCommand, CraftError, emit
from pylxd import Client

if not sys.warnoptions:
    warnings.simplefilter("ignore")


class _DestroyHandler:
    def __init__(self) -> None:
        self.client = Client()
        self.whitelist = ["ldap", "nfs", "head", "compute"]

    def teardown(self) -> None:
        """Steps to teardown micro-HPC cluster."""
        emit.progress("Destroying micro-HPC cluster...")
        instances = self.client.instances.all()
        for instance in instances:
            if instance.name.split("-")[0] in self.whitelist:
                instance.stop(wait=True)
                instance.delete(wait=True)

        if self.client.profiles.exists("micro-hpc"):
            self.client.profiles.get("micro-hpc").delete()

        if self.client.profiles.exists("nfs"):
            self.client.profiles.get("nfs").delete()


class DestroyCommand(BaseCommand):
    """Destroy your micro-HPC cluster."""

    name = "destroy"
    help_msg = "Destroy your micro-HPC cluster."
    overview = textwrap.dedent(
        """
        Destroy your micro-HPC cluster.
        
        This command can be used to destroy your micro-HPC cluster for
        if something goes wrong, or if you are just not interested in keeping the images up.
        """
    )

    def run(self, _) -> Optional[int]:
        """Run steps to destroy micro-HPC cluster."""
        try:
            handler = _DestroyHandler()
            handler.teardown()
            emit.ended_ok()
        except Exception as e:
            raise CraftError(f"A problem occurred when destroying the cluster: {e}")
