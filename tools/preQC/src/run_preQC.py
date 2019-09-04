from __future__ import print_function

import os
import shlex
import subprocess
import uuid, shutil, json
import numpy as np
import time
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


def upload_results(results_path, working_dir):
    """
    Uploads results folder containing the bam file (and associated output)
    :param bam_s3_path: S3 path to upload the alignment results to
    :param local_folder_path: local path containing the alignment results
    """

    upload_folder(results_path, os.path.join(working_dir,'preqc'))
    upload_folder(results_path, os.path.join(working_dir,'fragsizes'))

def run_preprocess(cmd_args, input_files, working_dir):
    """
    Runs the preprocessing steps
    :param cmd_args: arguments to be passed as is to the programm
    :param input_files: formatted string with filenames for preprocessing
    :param output_file: name of the output file in use
    :param working_dir: working_directory
    :return: path to results
    """
    print("wrkdir je :")
    print(working_dir)
    os.chdir(working_dir)
    preproc_folder = os.path.join(working_dir, 'preproc')

    try:
        os.makedirs(preproc_folder)
    except Exception as e:
        print('couldnt make preproc folder')
    print(preproc_folder)
    
    output_file_path = os.path.join(preproc_folder, 'done.preqc.fastq')
    
    
    cmd = 'sga preprocess {0} {1} -o {2}'.format(cmd_args, input_files, output_file_path)
    print ("Running: %s" % cmd)
    subprocess.check_call(shlex.split(cmd))

    return output_file_path

def run_index(input_file, cmd_args, working_dir):
    #think I should add a os.chdir here
    os.chdir(os.path.join(working_dir,'preproc'))
    cmd = 'sga index -a ropebwt {0} {1}'.format(cmd_args, input_file)
    print ("Running: %s" % cmd)
    subprocess.check_call(shlex.split(cmd))
    
    return input_file

def run_preqc(input_file, preqc_cmd_args, preqc_report_cmd_args, working_dir):
    
    os.chdir(working_dir)
    
    preqc_folder = os.path.join(working_dir, 'preqc')
    
    try:
        os.makedirs(preqc_folder)
    except Exception as e:
        pass
    
    output_file_path = os.path.join(preqc_folder, 'done.preproc')
    
    output_file = open(output_file_path,"w+")

    output_report = os.path.join(preqc_folder, 'preqc_report')
    
    cmd = 'sga preqc {0} {1}'.format(preqc_cmd_args, input_file)
    print ("Running: %s" % cmd)
    subprocess.check_call(shlex.split(cmd), stdout=output_file)
    output_file.close()

    cmd = 'sga-preqc-report.py -o {0} {1} {2}'.format(output_report, preqc_report_cmd_args, output_file_path)
    print ("Running: %s" % cmd)
    subprocess.check_call(shlex.split(cmd))
    
    run_frag_size_tbl(output_file_path, working_dir)
    
    return output_file_path

def run_frag_size_tbl(input_file, working_dir):

    os.chdir(working_dir)
    frag_folder = os.path.join(working_dir, 'fragsizes')

    try:
        os.makedirs(frag_folder)
    except Exception as e:
        pass

    with open(input_file, 'r') as f:
        files_dict = json.load(f)
    
    frags = files_dict['FragmentSize']['sizes']
    summary = {
        'Min.' : min(frags),
        '1st Qu.' : np.quantile(frags, 0.25),
        'Median' : np.median(frags),
        'Mean' : np.mean(frags),
        '3rd Qu.' : np.quantile(frags, 0.75),
        'Max' : max(frags)
    }
    with open(os.path.join(frag_folder, 'fragsizes.json'), 'w') as json_file:  
        json.dump(summary, json_file, indent=4)

def main():
    argparser = ArgumentParser()

    file_path_group = argparser.add_argument_group(title='File paths')
    file_path_group.add_argument('--fastq1_s3_path', type=str, help='FASTQ1 s3 path', required=True)
    file_path_group.add_argument('--fastq2_s3_path', type=str, help='FASTQ2 s3  path', required=True)

    run_group = argparser.add_argument_group(title='Run command args')
    run_group.add_argument('--preproc_cmd_args', type=str, help='Arguments for preprocessing', default=' ')
    run_group.add_argument('--index_cmd_args', type=str, help='Arguments for preprocessing', default=' ')
    run_group.add_argument('--preqc_cmd_args', type=str, help='Arguments for preprocessing', default=' ')
    run_group.add_argument('--preqc_report_cmd_args', type=str, help='Arguments for preprocessing', default=' ')

    argparser.add_argument('--working_dir', type=str, default='/scratch')
    argparser.add_argument('--results_folder', type=str)

    args = argparser.parse_args()

    #working_dir = os.path.join(args.working_dir, 'fa534753-c43b-4591-8bd5-2ffdd1123a33')
    working_dir = generate_working_dir(args.working_dir)
    
    # Download fastq files and reference files
    print ('Downloading FASTQs')
    fastq_files = '{0} {1}'.format(download_fastq_file(args.fastq1_s3_path, working_dir), download_fastq_file(args.fastq2_s3_path, working_dir))

    print ('Running preprocess')
    preprocessed_file = run_preprocess(args.preproc_cmd_args, fastq_files, working_dir)
    time.sleep(10)
    print ('Running index')
    indexed_file = run_index(preprocessed_file, args.index_cmd_args, working_dir)
    #indexed_file = ''
    time.sleep(10)
    print ('Running preqc')
    preqc_file = run_preqc(indexed_file, args.preqc_cmd_args, args.preqc_report_cmd_args, working_dir)

    print ('Uploading results to %s' % args.results_folder)
    upload_results(args.results_folder, working_dir)
    print('Cleaning up working dir')
    delete_working_dir(working_dir)
    print ('Completed')

    """
    docker run -v /home/imer/docker_share:/docker_share preqc:latest 
    --fastq1_s3_path="/docker_share/ecoli_mda_lane1_left.fastq.gz" 
    --fastq2_s3_path="/docker_share/ecoli_mda_lane1_right.fastq.gz" 
    --preproc_cmd_args="--phred64 --pe-mode 1" 
    --index_cmd_args="--no-reverse -t 4" 
    --preqc_cmd_args="-t 12 --force-EM" 
    --preqc_report_cmd_args="--page_per_plot " 
    --working_dir="/docker_share"
    
    docker run -v /home/imer/docker_share:/docker_share preqc:latest --fastq1_s3_path="/docker_share/ecoli_1K_1.fq.gz" --fastq2_s3_path="/docker_share/ecoli_1K_2.fq.gz" --preproc_cmd_args="--phred64 --pe-mode 1" --index_cmd_args="--no-reverse -t 2" --preqc_cmd_args="-t 2 --force-EM" --preqc_report_cmd_args="--page_per_plot" --working_dir="/docker_share"

    docker run -v /home/imer/docker_share:/docker_share preqc:latest --fastq1_s3_path="/docker_share/ecoli_mda_lane1_left.fastq.gz" --fastq2_s3_path="/docker_share/ecoli_mda_lane1_right.fastq.gz" --preproc_cmd_args="--phred64 --pe-mode 1" --index_cmd_args="--no-reverse -t 12" --preqc_cmd_args="-t 14 --force-EM" --preqc_report_cmd_args="--page_per_plot" --working_dir="/docker_share"

    print ('Uploading results to %s' % args.bam_s3_folder_path)
    upload_bam(args.bam_s3_folder_path, bam_folder_path)
    print('Cleaning up working dir')
    delete_working_dir(working_dir)
    print ('Completed')
    """

if __name__ == '__main__':
    main()
