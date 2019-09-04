FROM python:3

# Metadata
LABEL container.base.image="python:3"
LABEL software.name="kraken"
LABEL tags="Genomics"

RUN apt-get -y update && \ 
    apt-get -y install zlib1g-dev libsparsehash-dev git curl build-essential cmake && \
    apt-get clean

RUN pip install boto3 awscli
 
RUN git clone https://github.com/DerrickWood/kraken2.git
RUN mkdir /kraken_dir /kraken_db
RUN cd kraken2 &&  \
    ./install_kraken2.sh /kraken_dir

COPY kraken/src/run_kraken.py /
COPY common_utils /common_utils

ENV PATH="/kraken_dir:$PATH"
RUN apt-get -y install rsync

RUN kraken2-build --db /kraken_db --special silva
#RUN kraken2-build --standard --db /kraken_db
RUN ls -la /kraken_dir

ENTRYPOINT ["python", "/run_kraken.py"]