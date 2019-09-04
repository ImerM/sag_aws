FROM python:3

ARG VERSION="3.13.1"

# Metadata
LABEL container.base.image="python:3"
LABEL software.name="trimgalore"
LABEL tags="Genomics"

RUN apt update
RUN apt-get install openssl libssl-dev  

RUN pip install boto3 awscli subprocess32
RUN wget http://cab.spbu.ru/files/release${VERSION}/SPAdes-${VERSION}-Linux.tar.gz && \
    tar -xzf SPAdes-${VERSION}-Linux.tar.gz && \
    mv SPAdes-${VERSION}-Linux spades && \
    rm -rf SPAdes-${VERSION}-Linux.tar.gz && \
    chmod -R +x /spades/bin

ENV PATH="/spades/bin:$PATH"

COPY spades/src/run_spades.py /
COPY common_utils /common_utils

ENTRYPOINT [ "python", "/run_spades.py" ]
