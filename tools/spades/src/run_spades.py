from __future__ import print_function

import os
import shlex
import subprocess
import uuid, shutil, json

from argparse import ArgumentParser

from common_utils.s3_utils import download_file, upload_file, download_folder, upload_folder
from common_utils.job_utils import generate_working_dir, delete_working_dir

def copy_fastq_file(file_path, working_dir):
    """
    testing function, instead of download_fastq_file
    :param file_path: local filepath to file we copying
    :param working_dir: our working directory
    :return: local path to file with the fastq
    """
    path_to_put_in = os.path.join(working_dir, str(uuid.uuid4()))
    filename = os.path.split(file_path)[1]
    try:
        os.mkdir(path_to_put_in)
    except Exception as e:
        return e

    shutil.copy(file_path, path_to_put_in)
    local_fastq_path = os.path.join(path_to_put_in, filename)

    print("returned local fastq path is: " + local_fastq_path)
    return local_fastq_path 
def download_fastq_file(fastq1_s3_path, working_dir):
    """
    Downlodas the fastq files
    :param fastq1_s3_path: S3 path containing FASTQ with read1
    :param fastq2_s3_path: S3 path containing FASTQ with read2
    :param working_dir: working directory
    :return: local path to the folder containing the fastq
    """
    fastq_folder = os.path.join(working_dir, 'fastq')

    try:
        os.mkdir(fastq_folder)
    except Exception as e:
        pass

    local_fastq_path = download_file(fastq1_s3_path, fastq_folder)

    return local_fastq_path

def upload_results(folder_s3_path, local_folder_path):
    """
    Uploads results folder (and associated output)
    :param folder_s3_path: S3 path to upload the assembly results to
    :param local_folder_path: local path containing the assembly results
    """

    upload_folder(folder_s3_path, local_folder_path)

def generate_input_string(input_files, input_flags, working_dir):
    """
    Generates the input string
    :param input_flags: the SPAdes input_flags without dashes
    :param input_files: the S3 locations of the input files
    :return input string
    """
    outstring = ""
    input_files = input_files.split(',')
    input_flags = input_flags.split(',')
    for i in range(0, len(input_flags)):
        print(input_files[i])
        print(input_flags[i])
        outstring = outstring + "--" + str(input_flags[i].strip()) + " " + download_fastq_file(input_files[i].strip(), working_dir) + " "
    outstring = outstring[:-1] #remove last character in string (blank space)
    return outstring


def run_spades(input_arguments, cmd_args, working_dir):
    """
    Runs SPAdes
    :param input_arguments: string with properly formatted input arguments
    :param flags: additional SPAdes flags
    :param working_dir: working directory
    :return: path to results
    """

    # Change to working directory
    os.chdir(working_dir)
    results_folder = os.path.join(working_dir, 'results')

    try:
        os.mkdir(results_folder)
    except Exception as e:
        pass
    
    cmd = 'spades.py %s %s -o %s' % \
    (input_arguments, cmd_args, results_folder)
    
    print ("Running: %s" % cmd)
    subprocess.check_call(shlex.split(cmd))
    return results_folder

def main():
    argparser = ArgumentParser()

    file_path_group = argparser.add_argument_group(title='File paths')
    file_path_group.add_argument('--input_flags', type=str, help='All the flags for the files, in correct order', required=True)
    file_path_group.add_argument('--input_files', type=str, help='All the S3 file locations, in correct order', required=True)

    run_group = argparser.add_argument_group(title='Run command args')
    run_group.add_argument('--cmd_args', type=str, help='Arguments for preprocessing', default=' ')

    argparser.add_argument('--working_dir', type=str, default='/scratch')
    argparser.add_argument('--results_path', type=str, default='/scratch')

    args = argparser.parse_args()

    working_dir = generate_working_dir(args.working_dir)
    
    print ('Downloading files and forming input parameters')
    print ('input flags', args.input_flags)
    print ('input_files', args.input_files)
    
    input_arguments = generate_input_string(args.input_files, args.input_flags, working_dir)


    
    #Download to container the fastq files
    try:
        print ('Running SPAdes')
        results_folder_path = run_spades(input_arguments, args.cmd_args, working_dir)
    except Exception as e:
        upload_results(args.results_path, working_dir)

    upload_results(args.results_path, results_folder_path)
    print('Cleaning the working dir')
    delete_working_dir(working_dir)
    print ('Completed')

    """
    
    docker run -v /home/imer/docker_share:/docker_share spades:latest --input_files="/docker_share/ecoli_mda_lane1_left_val_1.fq.gz","/docker_share/ecoli_mda_lane1_right_val_2.fq.gz" --input_flags="pe1-1","pe1-2" --working_dir="/docker_share" --cmd_args="--only-assembler --sc -t 8"


   --input_files=["/docker_share/rb1_1.fastq.gz","/docker_share/rb1_1.fastq.gz"] --working_dir="/docker_share" --input_flags=["pe1-1","pe1-2"]
    "--input_flags", "pe1-1", "pe1-2",
    "--input_files", "s3://imer-test-genomics/SRR_both_trimmomatic_results/paired_1.fq", "s3://imer-test-genomics/SRR_both_trimmomatic_results/paired_2.fq",
    print ('Uploading results to %s' % args.output_s3_folder_path)
    upload_results(args.output_s3_folder_path, results_folder_path)
    print('Cleaning the working dir')
    delete_working_dir(working_dir)
    print ('Completed')

    
    



    print ('Uploading results to %s' % args.bam_s3_folder_path)
    upload_bam(args.bam_s3_folder_path, bam_folder_path)
    print('Cleaning up working dir')
    delete_working_dir(working_dir)
    print ('Completed')
    """

if __name__ == '__main__':
    main()
