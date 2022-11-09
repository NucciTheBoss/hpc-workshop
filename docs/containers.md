# Containers in HPC

We can just use Docker, right? No. Docker is rarely used at all in HPC due to the security risks that it can impose 
upon the cluster. Someone with the right knowledge can go into an unhardened Docker container and quickly wreak
havoc on the host system. To avoid these potential disasters, clusters use [Apptainer](https://apptainer.org) instead.
It is a read-only container system that only allows read operations, and you are the same user inside the container
as outside the container.

## Building a simple container

In our case, let us say that we have some ancient, mysterious COBOL code base that provides some critical calculations
for your research. Rather than forcing everyone who tries to reproduce your results to beg their system
administrator to install a COBOL compiler on the cluster, let us provide them a container they can pull instead.
First, start a shell session on `head-0`:

```text
$ lxc shell head-0
```

Now inside `head-0`, log in an user `test` and open a text editor window. We will use this text editor window to create our "ancient" COBOL
code base:

```text
~# sudo -i -u test
~# nano ancient_code.cbl
```

Populate the *ancient_code.cbl* file with the content below:

```cobol
            IDENTIFICATION DIVISION.
            PROGRAM-ID. VARS.

            DATA DIVISION.
              WORKING-STORAGE SECTION.
              01 FIRST-VAR PIC S9(3)V9(2) VALUE 445.62.
              01 SECOND-VAR PIC S9(3)V9(2) VALUE -123.45.
              01 THIRD-VAR PIC A(6) VALUE 'XYZ'.
              01 FOURTH-VAR PIC X(5) VALUE 'M565$'.
              01 GROUP-VAR.
                05 SUBVAR-2 PIC X(6) VALUE 'ATOMS'.
                05 SUBVAR-3 PIC X(10) VALUE 'CHEMICALS'.
                05 SUBVAR-4 PIC X(6) VALUE 'OH MY'.

            PROCEDURE DIVISION.
              DISPLAY "1ST RESULT : " FIRST-VAR.
              DISPLAY "2ND RESULT : " SECOND-VAR.
              DISPLAY "3RD RESULT : " THIRD-VAR.
              DISPLAY "4TH RESULT : " FOURTH-VAR.
              DISPLAY "SUMMARY: " GROUP-VAR.
              STOP RUN.
```

> __Important:__ Yes, this code file is formatted correctly. COBOL used to be written on punch cards where the first two
> "tabs" were dedicated to the line number. The styling convention was kept once COBOL migrated to being written
> on computers instead.

Save and close after populating *ancient_code.cbl* with the "ancient" code. Now open a new text editor window:

```text
~# nano cobol-runtime.def
```

*cobol-runtime.def* will serve as the definition file for our container. With the definition file open, populate it with
the content below:

```text
Bootstrap: docker
From: ubuntu:22.04

%runscript
  /opt/bin/simulation

%files
  ancient_code.cbl /opt/ancient_code.cbl

%post
  apt-get update -y
  apt-get upgrade -y
  apt-get install -y gnucobol
  
  mkdir -p /opt/bin
  cobc -x -o /opt/bin/simulation /opt/ancient_code.cbl
  rm /opt/ancient_code.cbl

%environment
  export PATH=/opt/bin:$PATH

%help
  Encapsulate old COBOL in a flashy new container
```

Save and close the definition file after you have populated the file, and then build an image using the following
command:

```text
~# apptainer build cobol-runtime.sif cobol-runtime.def
```

> __Note:__ It will take a few minutes for the container to build.

## Using the container to run our program

With the container image *cobol-realtime.sif* finally built, you can now run the simulation inside the apptainer
image:

```text
~# apptainer -s run cobol-runtime.sif
```

If the container has built successfully, you should see the following output below:

```text
1ST RESULT : +445.62
2ND RESULT : -123.45
3RD RESULT : XYZ   
4TH RESULT : M565$
SUMMARY: ATOMS CHEMICALS OH MY
```

Now onto adding more software with Spack!
