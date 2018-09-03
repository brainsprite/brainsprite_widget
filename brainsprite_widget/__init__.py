from ._version import version_info, __version__

from .widget import BrainspriteWidget

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'brainsprite_widget',
        'require': 'brainsprite_widget/extension'
    }]
