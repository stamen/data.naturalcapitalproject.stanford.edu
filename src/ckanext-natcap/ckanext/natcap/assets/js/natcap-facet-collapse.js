ckan.module("natcap-facet-collapse", function ($, _) {
  "use strict";
  return {
    options: {
      debug: false,
    },

    initialize: function () {
      const header = $(this.el).find('.search-filters-section-header');
      const content = $(this.el).find('.search-filters-section-content');

      // TODO open if any active
      header.click(() => {
        content.toggle();
        header.toggleClass('collapsed');
      });
    },
  };
});
