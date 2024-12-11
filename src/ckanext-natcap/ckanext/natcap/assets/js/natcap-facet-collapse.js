ckan.module("natcap-facet-collapse", function ($, _) {
  "use strict";
  return {
    options: {
      map_container_id: '',
      debug: false,
    },

    _onClick: function () {
      this.collapsed = !this.collapsed;
      if (this.collapsed) {
        this.root.addClass('collapsed');
      } else {
        this.root.removeClass('collapsed');
        if (this.options.map_container_id) {
          this.sandbox.publish('natcapMapShown', this.options.map_container_id);
        }
      }
    },

    initialize: function () {
      jQuery.proxyAll(this, '_onClick');

      this.header = $(this.el).find('.search-filters-section-header');
      this.root = $(this.el);
      this.collapsed = this.root.hasClass('collapsed');

      this.header.click(this._onClick);
    },
  };
});
