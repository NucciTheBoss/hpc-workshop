#!/usr/bin/env python3
# Copyright 2022 Jason C. Nucciarone
# See LICENSE file for licensing details.

"""Init command for bootstrapping the HPC cluster."""

from __future__ import annotations

import textwrap
from typing import Optional

from craft_cli import BaseCommand, CraftError


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
            print("This is a test for craft-cli.")
        except Exception as e:
            raise CraftError(f"A problem occurred when initializing the cluster: {e}")
