#!/usr/bin/env python3
# Copyright 2022 Jason C. Nucciarone
# See LICENSE file for licensing details.

"""hpcworkshop program for the quick setup of an HPC cluster with LXD."""

from __future__ import annotations

import sys

from craft_cli import (
    ArgumentParsingError,
    CommandGroup,
    Dispatcher,
    EmitterMode,
    ProvideHelpException,
    emit,
)

from hpcworkshop.cmd.destroy import DestroyCommand
from hpcworkshop.cmd.init import InitCommand


def main() -> None:
    """Main entry point for hpc-workshop program."""
    emit.init(EmitterMode.BRIEF, "hpc-workshop", "Starting hpc-workshop.")
    command_groups = [
        CommandGroup(
            "Helpers",
            [
                InitCommand,
                DestroyCommand,
            ],
        )
    ]
    try:
        dispatcher = Dispatcher(
            "hpc-workshop",
            command_groups,
            summary="A helper program for the HPC workshop at the 2022 Ubuntu Summit - Prague",
        )
        dispatcher.pre_parse_args(sys.argv[1:])
        dispatcher.load_command(None)
        dispatcher.run()
    except (ArgumentParsingError, ProvideHelpException) as e:
        print(e, file=sys.stderr)
        emit.ended_ok()
    else:
        emit.ended_ok()
