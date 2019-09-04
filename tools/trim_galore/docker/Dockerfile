FROM openjdk:7

ARG VERSION="06.19"

# Metadata
LABEL container.base.image="openjdk:3"
LABEL software.name="trimgalore"
LABEL software.license="GPLv3"
LABEL tags="Genomics"

RUN apt-get -y update && \ 
    apt-get -y install zlib1g-dev libsparsehash-dev git curl python3 && \
    apt-get clean

RUN apt-get -y install unzip

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python get-pip.py

RUN pip install boto3 awscli cutadapt

RUN curl -fsSl https://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.8.zip -o fastqc_v0.11.8.zip

RUN unzip fastqc_v0.11.8.zip && \
    chmod 755 /FastQC/fastqc && \
    ln -s /FastQC/fastqc /usr/local/bin/fastqc

RUN curl -fsSL https://github.com/FelixKrueger/TrimGalore/archive/0.6.0.tar.gz -o trim_galore.tar.gz
RUN tar xvzf trim_galore.tar.gz

ENV PATH="/TrimGalore-0.6.0:$PATH"

COPY trim_galore/src/run_trimgalore.py /
COPY common_utils /common_utils

ENTRYPOINT ["python", "/run_trimgalore.py"]