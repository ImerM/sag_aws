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


def upload_results(target_folder, local_folder_path):
    """
    Uploads results folder containing the bam file (and associated output)
    :param bam_s3_path: S3 path to upload the alignment results to
    :param local_folder_path: local path containing the alignment results
    """

    upload_folder(target_folder, local_folder_path)

def run_kraken(cmd_args, input_files, working_dir):
    """
    Runs the preprocessing steps
    :param cmd_args: arguments to be passed as is to the programm
    :param input_files: formatted string with filenames for preprocessing
    :param working_dir: working_directory
    :return: path to results
    """
    print(working_dir)
    os.chdir(working_dir)
    kraken_folder = os.path.join(working_dir, 'kraken')

    try:
        os.makedirs(kraken_folder)
    except Exception as e:
        print('couldnt make kraken folder')
    
    output_file_path = os.path.join(kraken_folder, 'kraken_report.txt')
    output_file = open(output_file_path,"w+")
    
    cmd = 'kraken2 --db /kraken_db {0} {1}'.format(cmd_args, input_files)
    print ("Running: %s" % cmd)
    subprocess.check_call(shlex.split(cmd), stdout=output_file)
    output_file.close()

    return kraken_folder

def generate_input_string(input_string, working_dir):

    input_files = input_string.split(',')
    print(input_files)
    downloaded_files = []
    for file in input_files:
        try:
            print(file)
            downloaded_files.append(download_fastq_file(file.strip(), working_dir))
        except Exception as e:
            print('error while dowloading file at: {0}'.format(file))
            print(e)
    input_filestring = ' '.join(downloaded_files)
    formatted_filestring = input_filestring.strip()
    return formatted_filestring

def main():
    argparser = ArgumentParser()

    file_path_group = argparser.add_argument_group(title='File paths')
    file_path_group.add_argument('--input_files', type=str, help='S3 paths for input files', required=True)

    run_group = argparser.add_argument_group(title='Run command args')
    run_group.add_argument('--cmd_args', type=str, help='Arguments for preprocessing', default=' ')

    argparser.add_argument('--working_dir', type=str, default='/scratch')
    argparser.add_argument('--results_path', type=str, default='/scratch')

    args = argparser.parse_args()

    working_dir = generate_working_dir(args.working_dir)
    
    # Download fastq files and reference files
    print ('Downloading FASTQs')
    fastq_files = generate_input_string(args.input_files, working_dir)

    print ('Running Kraken')
    kraken_folder = run_kraken(args.cmd_args, fastq_files, working_dir)
    
    print ('Uploading results to %s' % args.results_path)
    upload_folder(args.results_path, kraken_folder)
    print('Cleaning up working dir')
    delete_working_dir(working_dir)
    print ('Completed')

if __name__ == '__main__':
    main()
