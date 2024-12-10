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

    _onInputChange: function () {
      const searchInput = this.searchInput.val();
      const checkedCheckboxes = this.checkboxes.filter(":checked");
      const params = {
        q: searchInput || '',
      };

      checkedCheckboxes.each(function () {
        const field = $(this).data('field');
        if (!params[field]) {
          params[field] = [];
        }
        params[field].push($(this).data('value'));
      });

      this.submitButton.attr("href", this._getSearchUrl(params));
    },

    initialize: function () {
      jQuery.proxyAll(this, '_getSearchUrl');
      jQuery.proxyAll(this, '_onInputChange');

      this.root = $(this.el);
      this.submitButton = this.root.find("a.submit");
      this.searchInput = this.root.find("input[type='search']");
      this.checkboxes = this.root.find("input[type='checkbox']");

      this.searchInput.on("change", this._onInputChange);
      this.checkboxes.on("change", this._onInputChange);
    },
  };
});
