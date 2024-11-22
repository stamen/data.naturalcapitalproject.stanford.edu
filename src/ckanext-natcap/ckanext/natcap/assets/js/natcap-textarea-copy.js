ckan.module("natcap-textarea-copy", function ($, _) {
  "use strict";
  return {
    options: {
      debug: false,
      content: '',
    },

    initialize: function () {
      const copyButton = $(this.el).find('.package-textarea-copy-button');
      const textarea = $(this.el).find('.package-textarea-copy-content textarea');
      const messageArea = $(this.el).find('.package-textarea-copy-message-area');

      copyButton.click(() => {
        navigator.clipboard.writeText(this.options.content).then(() => {
          messageArea.text('Copied!');
        });
      });
    },
  };
});
