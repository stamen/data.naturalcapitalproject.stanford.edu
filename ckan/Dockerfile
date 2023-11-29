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
ENV CKANEXT_SPATIAL_GIT_REVISION=e59a295431247fcd605fe55bb4fd9a2ecfc28d2b
RUN apk add --no-cache geos geos-dev proj proj-dev proj-util
RUN pip3 install -e git+https://github.com/ckan/ckanext-spatial.git@$CKANEXT_SPATIAL_GIT_REVISION#egg=ckanext-spatial && \
    pip3 install -r https://raw.githubusercontent.com/ckan/ckanext-spatial/$CKANEXT_SPATIAL_GIT_REVISION/requirements.txt

# Install ckanext-natcap
RUN pip3 install -r $APP_DIR/src/ckanext-natcap/requirements.txt && \
        pip3 install -e $APP_DIR/src/ckanext-natcap
