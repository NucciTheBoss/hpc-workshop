# Put a pin in using debs or snaps

On HPC clusters, there are typically thousands if not tens of thousands of daily users who all have their own custom
software stacks. Reproducibility crucial in scientific research, even down to the point of having the same version of 
the programming language. Updating the software stack on a whim quickly leads to a bunch of unhappy researchers.

Luckily, we have some nice software to help us manage everyone's custom software deployment: 
[Lmod](https://lmod.readthedocs.io/en/latest/)! Lmod is a Lua-based module system that enables you to dynamically
load software as defined in Lua module files.

## Creating a Lua module file

If you look in the `/opt/sw` directory on `nfs-0`, you will see the directory *apptainer*:

```text
~# ls /opt/sw
```

This is the first program on our cluster that we will make available to our user `test`. To get started, open a text
editor window using the following command:

```text
~# nano 1.1.3.lua
```

Inside the text editor window, populate the *1.1.3.lua* file with the content below:

```lua
help([[Apptainer is a container management software for HPC gurus like you and me]])

local root = "/opt/sw/apptainer"

app_bin = pathJoin(root, "bin")
app_libexec_bin = pathJoin(root, "libexec/apptainer/bin")
app_libexec_cni = pathJoin(root, "libexec/apptainer/cni")
app_libexec_lib = pathJoin(root, "libexec/apptainer/lib")
app_man = pathJoin(root, "share/man")

prepend_path("PATH", app_bin)
prepend_path("PATH", app_libexec_bin)
prepend_path("PATH", app_libexec_cni)
prepend_path("LIBRARY_PATH", app_libexec_lib)
prepend_path("LD_LIBRARY_PATH", app_libexec_lib)
prepend_path("MANPATH", app_man)
```

Save and close the file once you are done populating the file.

## Setting up the module file

To set up the module file up on `nfs-0`, use the following commands:

```text
~# echo /opt/sw/modules > /opt/apps/lmod/lmod/init/.modulespath
~# mkdir -p /opt/sw/modules/apptainer
~# mv 1.1.3.lua /opt/sw/modules/apptainer
```

## Accessing `apptainer`

With the module file set in place, let us test that it works. Log into `nfs-0` as user `test`, and then load the
apptainer module:

```text
~# sudo -i -u test
$ module load apptainer
```

To test that apptainer works, use the following command to print the version number:

```text
$ apptainer version
```

If you see the version number printed out to the terminal, then it is time to move on to building a container image
with apptainer!
