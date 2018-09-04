"""
Functions to create interactive 3D brain volume visualization,
either stand-alone html or embedded in a notebook.
The visualizations are powered by the brainsprite.js library.
"""

# Author: Pierre Bellec, Christian Dansereau, Sebastian Urchs
# License: MIT

import warnings
import numpy as np
import json
import os

from nilearn._utils.niimg import _safe_get_data
from nilearn._utils.extmath import fast_abs_percentile
import matplotlib.pyplot as plt
from matplotlib.image import imsave
from nilearn.plotting.img_plotting import _load_anat, _MNI152Template
from nilearn.plotting.js_plotting_utils import HTMLDocument
from nilearn._utils import check_niimg_3d
from nilearn import image
from io import BytesIO , StringIO
from base64 import encodebytes


def _resample_to_self(img,interpolation):
    u,s,vh = np.linalg.svd(img.affine[0:3,0:3])
    vsize = np.min(np.abs(s))
    img = image.resample_img(img,target_affine=np.diag([vsize,vsize,vsize]),interpolation=interpolation)
    return img

def _data2sprite(data):
    nx, ny, nz = data.shape
    nrows = int(np.ceil(np.sqrt(nx)))
    ncolumns = int(np.ceil(nx / float(nrows)))

    sprite = np.zeros((nrows * nz, ncolumns * ny))
    indrow, indcol = np.where(np.ones((nrows, ncolumns)))

    for xx in range(nx):
        # we need to flip the image in the x axis
        sprite[(indrow[xx] * nz):((indrow[xx] + 1) * nz),
        (indcol[xx] * ny):((indcol[xx] + 1) * ny)] = data[xx, :,::-1].transpose()

    return sprite

def save_sprite(img , output_sprite , output_cmap=None , output_json=None,
                vmax=None , vmin=None , cmap='Greys' , threshold=None ,
                n_colors=256 , format = 'png', resample=True ,
                interpolation = 'nearest') :
    """ Generate a sprite from a 3D Niimg-like object.

        Parameters
        ----------
        img :  Niimg-like object
            See http://nilearn.github.io/manipulating_images/input_output.html
        output_file : string or file-like
            Path string to a filename, or a Python file-like object.
            If *format* is *None* and *fname* is a string, the output
            format is deduced from the extension of the filename.
        output_cmap : string, file-like or None, optional (default None)
            Path string to a filename, or a Python file-like object.
            The color map will be saved in that file (unless it is None).
            If *format* is *None* and *fname* is a string, the output format is
            deduced from the extension of the filename.
        output_json : string, file-like or None, optional (default None)
            Path string to a filename, or a Python file-like object.
            The parameters of the sprite will be saved in that file
            (unless it is None): Y and Z sizes, vmin, vmax, affine transform.
        vmax : float, or None, optional (default None)
            max value for mapping colors.
        vmin : float, or None, optional (default None)
            min value for mapping color.
        cmap : name of a matplotlib colormap, optional (default 'Greys')
            The colormap for the sprite
        threshold : a number, None, or 'auto', optional (default None)
            If None is given, the image is not thresholded.
            If a number is given, it is used to threshold the image:
            values below the threshold (in absolute value) are plotted
            as transparent. If auto is given, the threshold is determined
            magically by analysis of the image.
        n_colors : integer, optional (default 256)
            The number of discrete colors to use in the colormap, if it is
            generated.
        format : string, optional (default 'png')
            One of the file extensions supported by the active backend.  Most
            backends support png, pdf, ps, eps and svg.
        resample : boolean, optional (default True)
            Resample to isotropic voxels, with a LR/AP/VD orientation.
            This is necessary for proper rendering of arbitrary Niimg volumes,
            but not necessary if the image is in an isotropic standard space.
        interpolation : string, optional (default nearest)
            The interpolation method for resampling
            See nilearn.image.resample_img
        black_bg : boolean, optional
            If True, the background of the image is set to be black.

        Returns
        ----------
        sprite : numpy array with the sprite
    """

    # Get cmap
    cmap = plt.cm.get_cmap(cmap)

    img = check_niimg_3d(img, dtype='auto')

    # resample to isotropic voxel with standard orientation
    if resample:
        img = _resample_to_self(img,interpolation)

    # Read data
    data = _safe_get_data(img, ensure_finite=True)
    if np.isnan(np.sum(data)):
        data = np.nan_to_num(data)

    # Deal with automatic settings of plot parameters
    if threshold == 'auto':
        # Threshold epsilon below a percentile value, to be sure that some
        # voxels pass the threshold
        threshold = fast_abs_percentile(data) - 1e-5

    # threshold
    threshold = float(threshold) if threshold is not None else None

    # Get vmin vmax
    show_nan_msg = False
    if vmax is not None and np.isnan(vmax):
        vmax = None
        show_nan_msg = True
    if vmin is not None and np.isnan(vmin):
        vmin = None
        show_nan_msg = True
    if show_nan_msg:
        nan_msg = ('NaN is not permitted for the vmax and vmin arguments.\n'
                   'Tip: Use np.nanmax() instead of np.max().')
        warnings.warn(nan_msg)

    if vmax is None:
        vmax = np.nanmax(data)
    if vmin is None:
        vmin = np.nanmin(data)

    # Create sprite
    sprite = _data2sprite(data)

    # Mask sprite
    if threshold is not None:
        if threshold == 0:
            sprite = np.ma.masked_equal(sprite, 0, copy=False)
        else:
            sprite = np.ma.masked_inside(sprite, -threshold, threshold,
                                           copy=False)
    # Save the sprite
    imsave(output_sprite,sprite,vmin=vmin,vmax=vmax,cmap=cmap,format=format)

    # Save the parameters
    if type(vmin).__module__ == 'numpy':
        vmin = vmin.tolist() # json does not deal with numpy array
    if type(vmax).__module__ == 'numpy':
        vmax = vmax.tolist() # json does not deal with numpy array

    if output_json is not None:
        params = {
                    'nbSlice': {
                        'X': data.shape[0],
                        'Y': data.shape[1],
                        'Z': data.shape[2]
                    },
                    'min': vmin,
                    'max': vmax,
                    'affine': img.affine.tolist()
                 }
        if isinstance(output_json,str):
            f = open(output_json,'w')
            f.write(json.dumps(params))
            f.close
        else:
            output_json.write(json.dumps(params))

    # save the colormap
    if output_cmap is not None:
        data = np.arange(0,n_colors)/(n_colors-1)
        data = data.reshape([1,n_colors])
        imsave(output_cmap,data,cmap=cmap,format=format)

    return sprite


def view_stat_map(stat_map_img, threshold=None, bg_img='MNI152',vmax=None,
                vmin=None, cmap='cold_hot', n_colors=256, opacity=1, colorbar=True,
                interpolation='nearest',black_bg='auto',dim='auto', draw_cross=True):
    """
    Insert a 3D overlay as a sprite into an HTML page.
    Parameters
    ----------
    stat_map_img : Niimg-like object
        See http://nilearn.github.io/manipulating_images/input_output.html
        The statistical map image. Should be 3D or
        4D with exactly one time point (i.e. stat_map_img.shape[-1] = 1)
    threshold : str, number or None, optional (default=None)
        If None, no thresholding.
        If it is a number only values of amplitude greater
        than threshold will be shown.
        If it is a string it must finish with a percent sign,
        e.g. "25.3%", and only values of amplitude above the
        given percentile will be shown.
    bg_img : Niimg-like object, optional (default='MNI152')
        See http://nilearn.github.io/manipulating_images/input_output.html
        The background image that the stat map will be plotted on top of.
        If nothing is specified, the MNI152 template will be used.
    vmax : float, or None, optional
        max value for mapping colors.
    vmin : float, or None, optional
        min value for mapping color.
    cmap : name of a matplotlib colormap, optional (default 'hot')
        The colormap for the sprite
    colorbar : boolean, optional (default True)
        If True, display a colorbar on the right of the plots.
    threshold : a number, None, or 'auto'
        If None is given, the image is not thresholded.
        If a number is given, it is used to threshold the image:
        values below the threshold (in absolute value) are plotted
        as transparent. If auto is given, the threshold is determined
        magically by analysis of the image.
    n_colors : integer, optional
        The number of discrete colors to use in the colormap, if it is
        generated.
    interpolation : string, optional (default nearest)
        The interpolation method for resampling
        See nilearn.image.resample_img
    black_bg : boolean, optional (default 'auto')
            If True, the background of the image is set to be black.
            Otherwise, a white background is used.
            If set to auto, an educated guess is made to find if the background
            is white or black.
    opacity : float in [0,1], optional (default 1)
            The level of opacity of the overlay (0: transparent, 1: opaque)
    dim : float, 'auto' (by default), optional
            Dimming factor applied to background image. By default, automatic
            heuristics are applied based upon the background image intensity.
            Accepted float values, where a typical scan is between -2 and 2
            (-2 = increase constrast; 2 = decrease contrast), but larger values
            can be used for a more pronounced effect. 0 means no dimming.
    draw_cross : boolean, optional (default true)
            If draw_cross is True, a cross is drawn on the plot to
            indicate the cut plosition.

    Returns
    -------
    StatMapView : plot of the stat map.
        It can be saved as an html page or rendered (transparently) by the
        Jupyter notebook.
    """
    # Load stat map
    stat_map_img = check_niimg_3d(stat_map_img, dtype='auto')

    # Load default background
    if bg_img == 'MNI152':
        bg_img = _MNI152Template()

    # load background image, and resample stat map
    if bg_img is not None and bg_img is not False :
        bg_img, black_bg, bg_min, bg_max = _load_anat(bg_img,dim=dim,black_bg = black_bg)
        # resample background image to isotropic, standard orientation
        bg_img = _resample_to_self(bg_img,interpolation=interpolation)
        stat_map_img = image.resample_to_img(stat_map_img, bg_img,
                            interpolation=interpolation)
    else:
        stat_map_img = _resample_to_self(stat_map_img,interpolation=interpolation)
        bg_img = image.new_img_like(stat_map_img,np.zeros(stat_map_img.shape),stat_map_img.affine)
        black_bg = False
        bg_min = 0
        bg_max = 0

    # Set color parameters
    if black_bg:
        cfont = '#FFFFFF'
        cbg = '#000000'
    else:
        cfont = '#000000'
        cbg = '#FFFFFF'

    # Create a base64 sprite for the background
    bg_sprite = BytesIO()
    save_sprite(bg_img, output_sprite=bg_sprite, cmap='gray',
                format='jpg', resample=False, vmin=bg_min, vmax=bg_max)
    bg_sprite.seek(0)
    bg_base64 = encodebytes(bg_sprite.read()).decode('utf-8')
    bg_sprite.close()

    # Create a base64 sprite for the stat map
    # Possibly, also generate a file with the colormap
    stat_map_sprite = BytesIO()
    stat_map_json = StringIO()
    if colorbar:
        stat_map_cm = BytesIO()
    else:
        stat_map_cm = None

    save_sprite(
        stat_map_img,
        stat_map_sprite,
        stat_map_cm,
        stat_map_json,
        vmax,
        vmin,
        cmap,
        threshold,
        n_colors,
        'png',
        False
    )

    # Convert the sprite and colormap to base64
    stat_map_sprite.seek(0)
    stat_map_base64 = stat_map_sprite.read()
    stat_map_sprite.close()

    if colorbar:
        stat_map_cm.seek(0)
        cm_base64 = encodebytes(stat_map_cm.read()).decode('utf-8')
        stat_map_cm.close()
    else:
        cm_base64 = ''

    return stat_map_base64
