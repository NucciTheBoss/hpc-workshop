// Copyright 2022 Jason C. Nucciarone
// See LICENSE file for more information.

use std::process::Command;
use terminal_spinners::{SpinnerBuilder, BOUNCING_BAR};

/// Build the base LXD image needed for the cluster.
fn main() {
    let progress = SpinnerBuilder::new()
        .spinner(&BOUNCING_BAR)
        .text(" Launching base image...")
        .start();
    Command::new("lxc")
        .args(["launch", "ubuntu:22.04", "base"])
        .output()
        .expect("Failed to create base image");
    progress.stop();

    let progress = SpinnerBuilder::new()
        .spinner(&BOUNCING_BAR)
        .text(" Updating base image...")
        .start();
    Command::new("lxc")
        .args([
            "exec",
            "--env",
            "DEBIAN_FRONTEND=noninteractive",
            "base",
            "--",
            "apt",
            "update",
            "-y",
        ])
        .output()
        .expect("Failed to update sources");
    Command::new("lxc")
        .args([
            "exec",
            "--env",
            "DEBIAN_FRONTEND=noninteractive",
            "base",
            "--",
            "apt",
            "install",
            "-y",
            "build-essential",
            "wget",
        ])
        .output()
        .expect("Failed to install build dependencies");
    progress.stop();

    let progress = SpinnerBuilder::new()
        .spinner(&BOUNCING_BAR)
        .text(" Installing LDAP and SSSD into base...")
        .start();
    Command::new("lxc")
        .args([
            "exec",
            "--env",
            "DEBIAN_FRONTEND=noninteractive",
            "base",
            "--",
            "apt",
            "install",
            "-y",
            "slapd",
            "ldap-utils",
            "sssd-ldap",
        ])
        .output()
        .expect("Failed to install LDAP and SSSD");
    progress.stop();

    let progress = SpinnerBuilder::new()
        .spinner(&BOUNCING_BAR)
        .text(" Installing NFS into base...")
        .start();
    Command::new("lxc")
        .args([
            "exec",
            "--env",
            "DEBIAN_FRONTEND=noninteractive",
            "base",
            "--",
            "apt",
            "install",
            "-y",
            "nfs-kernel-server",
            "nfs-common",
        ])
        .output()
        .expect("Failed to install NFS");
    progress.stop();

    let progress = SpinnerBuilder::new()
        .spinner(&BOUNCING_BAR)
        .text(" SLURM and MUNGE into base...")
        .start();
    Command::new("lxc")
        .args([
            "exec",
            "--env",
            "DEBIAN_FRONTEND=noninteractive",
            "base",
            "--",
            "apt",
            "install",
            "-y",
            "slurmctld",
            "slurmd",
        ])
        .output()
        .expect("Failed to install SLURM");
    progress.stop();

    let progress = SpinnerBuilder::new()
        .spinner(&BOUNCING_BAR)
        .text(" Compiling Lmod inside base...")
        .start();
    Command::new("lxc").args([
        "exec",
        "--env",
        "DEBIAN_FRONTEND=noninteractive",
        "base",
        "--",
        "apt",
        "install",
        "-y",
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
    ]).output().expect("Failed to install Lua and/or TCL");
    // TODO: Compile Lua in /opt/apps
    progress.stop();

    let progress = SpinnerBuilder::new()
        .spinner(&BOUNCING_BAR)
        .text(" Compiling Apptainer inside base...")
        .start();
    Command::new("lxc");
    // TODO: Install Apptainer in /opt/sw
    progress.stop();

    let progress = SpinnerBuilder::new()
        .spinner(&BOUNCING_BAR)
        .text(" Installing spack into base...")
        .start();
    Command::new("lxc");
    progress.stop();

    let progress = SpinnerBuilder::new()
        .spinner(&BOUNCING_BAR)
        .text(" Deactivating all services...")
        .start();
    Command::new("lxc");
    progress.stop();

    let progress = SpinnerBuilder::new()
        .spinner(&BOUNCING_BAR)
        .text(" Creating image profiles...")
        .start();
    Command::new("lxc");
    progress.stop();

    let progress = SpinnerBuilder::new()
        .spinner(&BOUNCING_BAR)
        .text(" Creating system containers...")
        .start();
    Command::new("lxc");
    progress.stop();
}
