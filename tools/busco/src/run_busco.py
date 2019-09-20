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
    A testing function, used on a local machine instead of download_fastq_file
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
    Downloads the input file
    :param fastq1_s3_path: S3 path containing our FASTQ file
    :param working_dir: working directory
    :return: local path to the folder containing the fastq
    """
    fastq_folder = os.path.join(working_dir, 'fastq')

    try:
        os.mkdir(fastq_folder)
    except Exception as e:
        print('Error occured while creating the fastq download folder')
        pass

    local_fastq_path = download_file(fastq1_s3_path, fastq_folder)

    return local_fastq_path

def upload_results(bam_s3_path, local_folder_path):
    """
    Uploads results folder containing the bam file (and associated output)
    :param bam_s3_path: S3 path to upload the alignment results to
    :param local_folder_path: local path containing the alignment results
    """

    upload_folder(bam_s3_path, local_folder_path)

def run_busco(cmd_args, input_file, working_dir):
    """
    Runs the preprocessing steps
    :param cmd_args: arguments to be passed as is to the programm
    :param input_file: formatted string with filenames for preprocessing
    :param working_dir: working_directory
    :return: path to results
    """
    
    os.chdir(working_dir)
    busco_folder = os.path.join(working_dir, 'run_busco')

    cmd = 'python3 /busco/scripts/run_BUSCO.py -i {0} {1} -o {2}'.format(input_file, cmd_args, 'busco')
    print ("Running: %s" % cmd)
    subprocess.check_call(shlex.split(cmd))
    
    return busco_folder

def main():
    argparser = ArgumentParser()

    file_path_group = argparser.add_argument_group(title='File paths')
    file_path_group.add_argument('--input_file', type=str, help='s3 path', required=True)
    

    run_group = argparser.add_argument_group(title='Run command args')
    run_group.add_argument('--cmd_args', type=str, help='Arguments for preprocessing', default=' ')

    argparser.add_argument('--working_dir', type=str, default='/docker_share')
    argparser.add_argument('--results_path', type=str, default='/scratch')

    args = argparser.parse_args()

    working_dir = generate_working_dir(args.working_dir)
    
    # Download fastq files and reference files
    print ('Downloading FASTQs')
    
    input_file = download_fastq_file(args.input_file, working_dir)
    print ('Running busco')
    busco_folder = run_busco(args.cmd_args, input_file, working_dir)
    
    print ('Uploading results to %s' % args.results_path)
    upload_results(args.results_path, busco_folder)
    
    print('Cleaning up working dir')
    delete_working_dir(working_dir)
    print ('Completed')

if __name__ == '__main__':
    main()
