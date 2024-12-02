ckan.module("natcap-facet-collapse", function ($, _) {
  "use strict";
  return {
    options: {
      debug: false,
    },

    initialize: function () {
      const header = $(this.el).find('.search-filters-section-header');
      const root = $(this.el);

      header.click(() => {
        root.toggleClass('collapsed');
      });
    },
  };
});
