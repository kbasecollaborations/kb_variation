FROM kbase/sdkbase2:python
MAINTAINER pranjan77
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.


RUN apt-get update \
    && apt-get install -y --no-install-recommends bioperl wget

RUN apt-get update \
   && apt-get install -y make gcc libbz2-dev zlib1g-dev libncurses5-dev libncursesw5-dev liblzma-dev

RUN cd /usr/bin \
   && wget https://github.com/samtools/htslib/releases/download/1.9/htslib-1.9.tar.bz2 \
   && tar -vxjf htslib-1.9.tar.bz2 \
   && cd htslib-1.9 \
   && make \
   && cd .. \
   && wget https://github.com/samtools/samtools/releases/download/1.9/samtools-1.9.tar.bz2  \
   && tar -vxjf samtools-1.9.tar.bz2 \
   && cd samtools-1.9 \
   && make \
   && cd .. \
   && wget https://github.com/samtools/bcftools/releases/download/1.9/bcftools-1.9.tar.bz2 \
   && tar -vxjf bcftools-1.9.tar.bz2 \
   && cd bcftools-1.9 \
   && make \
   && export PATH="$PATH:/usr/bin/bcftools-1.9:/usr/bin/samtools-1.9:/usr/bin/htslib-1.9"

ENV PATH="$PATH:/usr/bin/bcftools-1.9:/usr/bin/samtools-1.9:/usr/bin/htslib-1.9"

# -----------------------------------------

COPY ./ /kb/module


RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
