FROM ckan/ckan-solr:2.10-solr9-spatial

USER root 

ENV SOLR_SCHEMA_FILE="/opt/solr/server/solr/configsets/ckan/conf/managed-schema"

ENV SOLR_MULTI_FIELDS='<field name="sources_res_formats" type="string" indexed="true" stored="true" multiValued="true"/> \
  <field name="placenames" type="string" indexed="true" stored="true" multiValued="true"/>'
RUN sed -i "/<fields>/a $SOLR_MULTI_FIELDS" $SOLR_SCHEMA_FILE

USER solr

CMD ["sh", "-c", "solr-precreate ckan $SOLR_CONFIG_DIR/ckan"]
