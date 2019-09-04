FROM python:3

ARG VERSION="03.17.03.01"

# Metadata
LABEL container.base.image="python:3"
LABEL software.name="preQC"
LABEL software.description="preQC tools"
LABEL software.website="https://github.com/jts/sga"
LABEL software.license="GPLv3"
LABEL tags="Genomics"

RUN apt-get -y update && \ 
    apt-get -y install zlib1g-dev libsparsehash-dev git curl cmake bamtools && \
    apt-get clean

RUN pip install boto3 awscli numpy                        



RUN git clone git://github.com/pezmaster31/bamtools.git && \
    cd bamtools && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_INSTALL_PREFIX=/usr/local/bamtools .. && \
    make && \
    make install

RUN ls /usr/local/bamtools

RUN git clone git://github.com/jts/sga.git && \
    cd sga/src && \
    ./autogen.sh && \
    ./configure --with-bamtools=/usr/local/bamtools && \
    make && \
    make install 

COPY preQC/src/run_preQC.py /
COPY common_utils /common_utils

RUN pip install matplotlib

ENV PATH="/sga/src/bin:$PATH"

ENTRYPOINT ["python", "/run_preQC.py"]