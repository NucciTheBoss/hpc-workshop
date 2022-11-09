# But I like having `apt` and `snap`

Yes, `apt` and `snap` are excellent package managers for Ubuntu, however, they are not commonly used for distributing
HPC software. Why? Because everyone has their own custom implementation that pre-built packages might not necessarily
meet. For example, some researchers may opt to compile their dependencies with `intel` or `pgi` compilers rather
than use GNU's compiler collection. As such, we need a package manager that allows researchers to role their own
custom software stacks. Luckily, there are a couple of options for this with one of the most popular being
[Spack](https://spack.io).

## Installing `spack`

To install Spack, start a shell session inside `head-0` and then log in as user `test`:

```text
$ lxc shell head-0
~# sudo -i -u test
```

Execute the following command as user `test` to install Spack inside their home directory:

```text
git clone -c feature.manyFiles=true https://github.com/spack/spack.git
```

> __Note:__ Spack is a rather beefy git repository, so the clone may take a few minutes

Once git has finished cloning the spack repository, execute the following command to set up inside user `test`'s
environment:

```text
. spack/share/spack/setup-env.sh
```

## Compiling a package

With spack set up inside user `test`'s environment, you can use the following command to install the `cowsay`
package:

```text
$ spack install cowsay
```

> __Note:__ Installing cowsay will also take a few minutes to install since spack installs almost every package
> from source.

## Making the package available to user `test`

Once `cowsay` has finished installing, the following commands can be used to make `cowsay` accessible to user `test`:

```text
$ spack load cowsay
$ cowsay 'HPC on LXD is great!'
```

If cowsay was installed correctly, your cow should say *HPC on LXD is great!* in the terminal window:

```text
 ______________________ 
< HPC on LXD is great! >
 ---------------------- 
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```

Now it is time to bring everything together and submit our first job!