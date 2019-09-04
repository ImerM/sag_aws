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


def upload_bam(bam_s3_path, local_folder_path):
    """
    Uploads results folder containing the bam file (and associated output)
    :param bam_s3_path: S3 path to upload the alignment results to
    :param local_folder_path: local path containing the alignment results
    """

    upload_folder(bam_s3_path, local_folder_path)

def run_trim_galore(cmd_args, input_files, working_dir):
    """
    Runs the preprocessing steps
    :param cmd_args: arguments to be passed as is to the programm
    :param input_files: formatted string with filenames for preprocessing
    :param output_file: name of the output file in use
    :param working_dir: working_directory
    :return: path to results
    """
    print(working_dir)
    os.chdir(working_dir)
    trimmed_folder = os.path.join(working_dir, 'trimmed')

    try:
        os.makedirs(trimmed_folder)
    except Exception as e:
        print('couldnt make trimmed folder')


    
    cmd = 'trim_galore {0} -o {2} {1}'.format(cmd_args, input_files, trimmed_folder)
    print ("Running: %s" % cmd)
    subprocess.check_call(shlex.split(cmd))

    return trimmed_folder

def main():
    argparser = ArgumentParser()

    file_path_group = argparser.add_argument_group(title='File paths')
    file_path_group.add_argument('--fastq1_s3_path', type=str, help='FASTQ1 s3 path', required=True)
    file_path_group.add_argument('--fastq2_s3_path', type=str, help='FASTQ2 s3  path', required=True)

    run_group = argparser.add_argument_group(title='Run command args')
    run_group.add_argument('--cmd_args', type=str, help='Arguments for preprocessing', default=' ')

    argparser.add_argument('--working_dir', type=str, default='/scratch')
    argparser.add_argument('--results_path', type=str, default='/scratch')

    args = argparser.parse_args()

    working_dir = generate_working_dir(args.working_dir)
    
    # Download fastq files and reference files
    print ('Downloading FASTQs')
    fastq_files = '{0} {1}'.format(download_fastq_file(args.fastq1_s3_path, working_dir), download_fastq_file(args.fastq2_s3_path, working_dir))

    print ('Running trim_galore')
    trimmed_folder = run_trim_galore(args.cmd_args, fastq_files, working_dir)
    
    print ('Uploading results to %s' % args.results_path)
    upload_bam(args.results_path, trimmed_folder)
    print('Cleaning up working dir')
    delete_working_dir(working_dir)
    print ('Completed')
    """
    docker run -v /home/imer/docker_share:/docker_share trimgalore:latest --fastq1_s3_path="/docker_share/ecoli_mda_lane1_left.fastq.gz" --fastq2_s3_path="/docker_share/ecoli_mda_lane1_right.fastq.gz" --cmd_args="--gzip -q 10 --paired --retain_unpaired" --working_dir="/docker_share"
    
    docker run -v /home/imer/docker_share:/docker_share preqc:latest --fastq1_s3_path="/docker_share/ecoli_1K_1.fq.gz" --fastq2_s3_path="/docker_share/ecoli_1K_2.fq.gz" --preproc_cmd_args="--phred64 --pe-mode 1" --index_cmd_args="--no-reverse -t 2" --preqc_cmd_args="-t 2 --force-EM" --preqc_report_cmd_args="--page_per_plot" --working_dir="/docker_share"

docker run -v /home/imer/docker_share:/docker_share preqc:latest --fastq1_s3_path="/docker_share/ecoli_mda_lane1_left.fastq.gz" --fastq2_s3_path="/docker_share/ecoli_mda_lane1_right.fastq.gz" --preproc_cmd_args="--phred64 --pe-mode 1" --index_cmd_args="--no-reverse -t 12" --preqc_cmd_args="-t 12 --force-EM" --preqc_report_cmd_args="--page_per_plot" --working_dir="/docker_share"

    print ('Uploading results to %s' % args.bam_s3_folder_path)
    upload_bam(args.bam_s3_folder_path, bam_folder_path)
    print('Cleaning up working dir')
    delete_working_dir(working_dir)
    print ('Completed')
    """

if __name__ == '__main__':
    main()
