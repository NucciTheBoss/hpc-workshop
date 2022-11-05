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

if not sys.warnoptions:
    warnings.simplefilter("ignore")


class _DestroyHandler:
    ...


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
        ...
