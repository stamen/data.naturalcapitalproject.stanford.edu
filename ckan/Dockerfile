FROM ckan/ckan-base:2.10.4

# Set up environment variables
ENV APP_DIR=/opt/ckan-catalog/data.naturalcapitalproject.stanford.edu
ENV TZ=UTC
RUN echo ${TZ} > /etc/timezone

# Make sure both files are not exactly the same
RUN if ! [ /usr/share/zoneinfo/${TZ} -ef /etc/localtime ]; then \
        cp /usr/share/zoneinfo/${TZ} /etc/localtime ;\
    fi ;

# Install package dependencies for ckanext-spatial
ENV PROJ_DIR=/usr
ENV PROJ_LIBDIR=/usr/lib
ENV PROJ_INCDIR=/usr/include
# Using latest commit from master branch to avoid having to compile PROJ from source
ENV CKANEXT_SPATIAL_GIT_REVISION=938308469892e4bcf7389cb4adee5ccdd5a0ccca
RUN apk add --no-cache geos geos-dev proj proj-dev proj-util
RUN pip3 install -e git+https://github.com/ckan/ckanext-spatial.git@$CKANEXT_SPATIAL_GIT_REVISION#egg=ckanext-spatial && \
    pip3 install -r https://raw.githubusercontent.com/ckan/ckanext-spatial/$CKANEXT_SPATIAL_GIT_REVISION/requirements.txt
RUN pip3 install -e 'git+https://github.com/ckan/ckanext-scheming.git@3af6056bbe16c3f8c6257f18cb2a0805370f85de#egg=ckanext-scheming'
RUN pip3 install "numpy<2"

ENV CKANEXT_GOOGLEANALYTICS_GIT_REV=44cb2844a1704bfd9a7a42164652aaf6826a1bc7
RUN pip3 install -e git+https://github.com/ckan/ckanext-googleanalytics.git@$CKANEXT_GOOGLEANALYTICS_GIT_REV#egg=ckanext.googleanalytics && \
    pip3 install -r https://raw.githubusercontent.com/ckan/ckanext-googleanalytics/$CKANEXT_GOOGLEANALYTICS_GIT_REV/requirements.txt
RUN pip3 install oauth2client

# NOTE: requires that the build context includes ./src/
COPY ./src/ckanext-natcap /tmp/ckanext-natcap
RUN pip3 install -r /tmp/ckanext-natcap/requirements.txt && pip3 install /tmp/ckanext-natcap

# Install any extensions needed by your CKAN instance
# See Dockerfile.dev for more details and examples

# Copy custom initialization scripts
COPY ./ckan/docker-entrypoint.d/* /docker-entrypoint.d/

# Apply any patches needed to CKAN core or any of the built extensions (not the
# runtime mounted ones)
COPY patches ${APP_DIR}/patches

RUN for d in $APP_DIR/patches/*; do \
        if [ -d $d ]; then \
            for f in `ls $d/*.patch | sort -g`; do \
                cd $SRC_DIR/`basename "$d"` && echo "$0: Applying patch $f to $SRC_DIR/`basename $d`"; patch -p1 < "$f" ; \
            done ; \
        fi ; \
    done
