var brainsprite_widget = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'brainsprite_widget',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'brainsprite_widget',
          version: brainsprite_widget.version,
          exports: brainsprite_widget
      });
  },
  autoStart: true
};

