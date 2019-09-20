FROM python:3

# Metadata
LABEL container.base.image="python:3"
LABEL software.name="Busco"
LABEL tags="Genomics"

RUN apt-get -y update && \ 
    apt-get -y install zlib1g-dev libsparsehash-dev git curl hmmer augustus augustus-data augustus-doc && \
    apt-get clean

RUN pip install boto3 awscli

RUN curl -fsSL https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ncbi-blast-2.9.0+-x64-linux.tar.gz -o ncbi-blast.tar.gz && \
    tar xvzf ncbi-blast.tar.gz && \
    mv /ncbi-blast-2.9.0+ /blast     
 
RUN git clone https://gitlab.com/ezlab/busco.git

COPY busco/src/config.ini /busco/config/config.ini

RUN cd busco && \
    python setup.py install

COPY busco/src/run_busco.py /
COPY common_utils /common_utils
COPY busco/etc/datasets_list.sh /datasets_list.sh

RUN cd /
RUN bash datasets_list.sh

ENV PATH="/blast/bin:$PATH" \
    PATH="/usr/share/augustus/scripts:$PATH" \
    AUGUSTUS_CONFIG_PATH="/usr/share/augustus/config/"

ENTRYPOINT ["python", "/run_busco.py"]