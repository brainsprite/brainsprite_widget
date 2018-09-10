import nibabel as nb
import ipywidgets as widgets
from traitlets import Unicode, Bytes, Bool, Dict, Int, Float
from .brainsprite import view_stat_map
from .traits import Point3D, Color

@widgets.register
class BrainspriteWidget(widgets.DOMWidget):

    _view_name = Unicode('BrainSpriteView').tag(sync=True)
    _model_name = Unicode('BrainSpriteModel').tag(sync=True)
    _view_module = Unicode('brainsprite_widget').tag(sync=True)
    _model_module = Unicode('brainsprite_widget').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)
    sprite = Bytes(help='Sprite image').tag(sync=True)

    nan_values = Bool(help='NaN image values, i.e. unable to read values').tag(sync=True)
    smooth = Bool(help='Smoothing of the main slices').tag(sync=True)
    coordinates = Bool(help='Show slice numbers').tag(sync=True)
    origin = Point3D(help='Origin').tag(sync=True)
    voxel_size = Int(help='Voxel size').tag(sync=True)

    background = Color(help='Background color for the canvas').tag(sync=True)

    colorbar_height = Float(help='Colorbar size parameters').tag(sync=True)

    font_size = Float(help='Font size').tag(sync=True)
    font_color = Color(help='Font color').tag(sync=True)
    decimals = Int(help='Number of decimals displayed', min=0).tag(sync=True)

    crosshair = Bool(help='Show crosshair').tag(sync=True)
    crosshair_color = Color(help='Crosshair color').tag(sync=True)
    crosshair_size = Float(help='Crosshair size', min=0).tag(sync=True)

    def __init__(self, image, nan_values, smooth, coordinates, origin,
                 voxel_size, background, colorbar_height, font_size, font_color,
                 decimals, crosshair, crosshair_color, crosshair_size):

        super(BrainspriteWidget, self).__init__()

        self.sprite = view_stat_map(image)
        self.nan_values = nan_values
        self.smooth = smooth
        self.coordinates = coordinates
        self.origin = origin
        self.voxel_size = voxel_size
        self.background = background
        self.colorbar_height = colorbar_height
        self.font_size = font_size
        self.font_color = font_color
        self.decimals = decimals
        self.crosshair = crosshair
        self.crosshair_color = crosshair_color
        self.crosshair_size = crosshair_size