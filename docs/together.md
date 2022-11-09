# Time to enjoy the fruits of your labor

We have gone through all this work to set up our cluster, so now it is time for us to enjoy the fruits of our labor.
We are going to use all the software we have set up to submit our first job.

## Writing a job

Log into the `head-0` as user `test`:

```text
$ lxc shell head-0
~# sudo -i -u nucci
```

Logged in as user `test`, open a text editor window:

```text
$ nano research.submit
```

With the file *research.submit* open, populate the file with the content below:

```text
#!/bin/bash
#SBATCH --job-name=research
#SBATCH --partition=all
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=500mb
#SBATCH --time=00:00:30
#SBATCH --error=research.%J.err
#SBATCH --output=research.%J.out

. spack/share/spack/setup-env.sh
spack load cowsay
module load apptainer

apptainer -s run cobol-runtime.sif
echo -e "\n\n"
cowsay 'Done'
```

Save and close the file once you are done populating the *research.job* file.

> __Important:__ If you notice that your SLURM compute node has the state of drained, you will need to *undrain* it.
> You can undrain the node by launching the scontrol interpreter and issuing the following commands:
> ```text
> ~# scontrol
> update NodeName=compute-0 State=DOWN Reason="undraining"
> update NodeName=compute-0 State=RESUME
> ```

## Submitting a job

You can use the following command to submit your job file to your micro-HPC cluster:

```text
$ sbatch research.submit
```

## Evaluating the results

After a few seconds, your job's results should be returned by SLURM. You can use the following command to browse
through the results of your job:

```text
$ less research.65539.out
```

> __Note:__ Your job ID number may defer from the one above.

You should see something like the following in your `less` window:

```text
1ST RESULT : +445.62
2ND RESULT : -123.45
3RD RESULT : XYZ   
4TH RESULT : M565$
SUMMARY: ATOMS CHEMICALS OH MY 



 ______ 
< Done >
 ------ 
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```

Congratulations! You successfully ran your first job. This is the end of the workshop, so the next page will discuss
where you can go from here!