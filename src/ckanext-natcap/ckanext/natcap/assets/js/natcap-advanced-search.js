ckan.module("natcap-advanced-search", function ($, _) {
  "use strict";
  return {
    options: {
      debug: false,
      base_url: '',
    },

    _getSearchUrl: function (params) {
      return this.options.base_url + "?" + $.param(params, true);
    },

    _onBboxDrawn: function (bbox) {
      this.bboxInput.val(bbox);
      this._onInputChange();
    },

    _onInputChange: function () {
      const bbox = this.bboxInput.val();
      const searchInput = this.searchInput.val();
      const checkedCheckboxes = this.checkboxes.filter(":checked");
      const params = {
        q: searchInput || '',
      };

      if (bbox) {
        params.ext_bbox = bbox;
      }

      checkedCheckboxes.each(function () {
        const field = $(this).data('field');
        if (!params[field]) {
          params[field] = [];
        }
        params[field].push($(this).data('value'));
      });

      this.submitButton.attr("href", this._getSearchUrl(params));
    },

    _onModalShown: function () {
      this.sandbox.publish('natcapMapShown', this.root.find('.dataset-map-container').attr('id'));
    },

    initialize: function () {
      jQuery.proxyAll(this, '_getSearchUrl');
      jQuery.proxyAll(this, '_onBboxDrawn');
      jQuery.proxyAll(this, '_onInputChange');
      jQuery.proxyAll(this, '_onModalShown');

      this.root = $(this.el);
      this.submitButton = this.root.find("a.submit");
      this.bboxInput = this.root.find("input[name='adv_search_ext_bbox']");
      this.searchInput = this.root.find("input[type='search']");
      this.modal = $('#advancedSearchModal');

      this.checkboxes = this.root.find("input[type='checkbox']");

      this.searchInput.on("change", this._onInputChange);
      this.checkboxes.on("change", this._onInputChange);

      this.modal.on("shown.bs.modal", this._onModalShown);
      this.sandbox.subscribe('natcapSpatialQueryBboxDrawn', this._onBboxDrawn);
    },
  };
});
