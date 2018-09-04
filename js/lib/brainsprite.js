var widgets = require('@jupyter-widgets/base');
var _ = require('lodash');

var BrainSpriteModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend(widgets.DOMWidgetModel.prototype.defaults(), {
        _model_name : 'BrainSpriteModel',
        _view_name : 'BrainSpriteView',
        _model_module : 'brainsprite_widget',
        _view_module : 'brainsprite_widget',
        _model_module_version : '0.1.0',
        _view_module_version : '0.1.0',
        sprite : null
    })
});


var BrainSpriteView = widgets.DOMWidgetView.extend({
    render: function() {
        this.value_changed();
        this.model.on('change:sprite', this.value_changed, this);
    },

    value_changed: function() {
        var unique_id = this.model.model_id;
        var elem = this.model.el;
        var sprite = this.model.get('sprite');
        var tempUrl = URL.createObjectURL(
            new Blob(
                [ sprite.buffer ],
                { type: 'image/png' }
            )
        );

        this.img = jQuery('<img />').attr('src', tempUrl)[0]

        // TODO call brainsprite into elem, using this.img
    }
});


module.exports = {
    BrainSpriteModel: BrainSpriteModel,
    BrainSpriteView: BrainSpriteView
};
