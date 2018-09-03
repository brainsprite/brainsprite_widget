import ipywidgets as widgets
from traitlets import Unicode

@widgets.register
class BrainspriteWidget(widgets.DOMWidget):
    """An example widget."""
    _view_name = Unicode('BrainSpriteView').tag(sync=True)
    _model_name = Unicode('BrainSpriteModel').tag(sync=True)
    _view_module = Unicode('brainsprite_widget').tag(sync=True)
    _model_module = Unicode('brainsprite_widget').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)
    value = Unicode('BrainSprite World!').tag(sync=True)
