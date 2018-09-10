import re
import six

from traitlets import TraitType


class Point3D(TraitType):
    default_value = {'x': 0, 'y': 0, 'z': 0}
    info_text = 'a 3D point'

    def validate(self, obj, value):
        if isinstance(value, dict):
            if all(a in value for a in ['x', 'y', 'z']) and \
               all(isinstance(value[a], int) in value for a in ['x', 'y', 'z']):
                return value
        self.error(obj, value)


class Color(TraitType):
    """A trait for unicode strings."""

    default_value = '#000000'
    info_text = 'a hex color string'

    def validate(self, obj, value):

        decoded = value
        if isinstance(value, bytes):
            try:
                decoded = value.decode('ascii', 'strict')
            except UnicodeDecodeError:
                self.error(obj, value)
            
        if isinstance(decoded, six.text_type) and \
           re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', decoded):
            return decoded

        self.error(obj, value)