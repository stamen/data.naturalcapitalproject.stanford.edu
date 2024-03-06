FROM ckan/ckan-base:2.10.1

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

# NOTE: requires that the build context includes ./src/
COPY ./src/ckanext-natcap /tmp/ckanext-natcap
RUN pip3 install -r /tmp/ckanext-natcap/requirements.txt && pip3 install /tmp/ckanext-natcap