version= '0.0.1'
about_text = """
copyright 2016 Petras Jokubauskas <klavishas@gmail.com>

Cam_overlap_manager is utility to read, generate, merge, and re-use the
overlap files generated by Cameca(TM) Peaksight(TM) software.

Cam_overlap_manager is developed independantly from Cameca or
Ametek inc.
Development is based on the RE of binary data formats which
is Fair Use.

Full copy of source code can be obtained at
www.github.com/sem-geologist/cam-overlap-manager

The software is writen in python 3 and Qt5 libraries.

LICENSE:

Cam_overlap_manager is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Cam_overlap_manager is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with source code of this program,
or see <http://www.gnu.org/licenses/>.
"""

import struct
import numpy as np
from io import BytesIO
import os

from datetime import datetime, timedelta


def filetime_to_datetime(filetime):
    """Return recalculated windows filetime to unix time."""
    return datetime(1601, 1, 1) + timedelta(microseconds=filetime / 10)

def mod_date(filename):
    """Return datetime of file last moddification"""
    t = os.path.getmtime(filename)
    return datetime.fromtimestamp(t)

def get_xtal(full_xtal_name):
    """get basic crystal name.
       example: get_xtal('LLIF') -> 'LIF'
    """
    for i in ['PC0', 'PC1', 'PC2', 'PC3', 'PET', 'TAP', 'LIF']:
        if i in full_xtal_name:
            return i

def read_c_hash_string(stream):
    str_len = struct.unpack('<i', stream.read(4))[0]
    return str(stream.read(str_len))


class CamecaBase(object):
    value_map = {
                 1: 'WDS setup',
                 2: 'Image/maping setup',
                 3: 'Calibration setup',
                 4: 'Quanti setup',
                 5: 'unknown',  # What is this???
                 6: 'WDS results',
                 7: 'Image/maping results',
                 8: 'Calibration results',
                 9: 'Quanti results',
                 10: 'Peak overlap table'
                }
    cameca_lines = {
                    1: 'Kβ', 2: 'Kα',
                    3: 'Lγ4', 4:'Lγ3', 5: 'Lγ2', 6: 'Lγ',
                    7: 'Lβ9', 8: 'Lβ10', 9: 'Lβ7', 10: 'Lβ2',
                    11: 'Lβ6', 12: 'Lβ3', 13: 'Lβ4', 14: 'Lβ',
                    15: 'Lα', 16: 'Lν', 17: 'Ll',
                    18: 'Mγ', 19: 'Mβ', 20: 'Mα', 21: 'Mζ', 22: 'Mζ2',
                    23: 'M1N2', 24: 'M1N3', 25: 'M2N1', 26: 'M2N4',
                    27: 'M2O4', 28: 'M3N1', 29: 'M3N4', 30: 'M3O1',
                    31: 'M3O4', 32: 'M4O2'
                   }
    
    #it could be used lists, however, dict is much faster to lookup
    element_table = {
                     0: 'n', 1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B',
                     6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne', 11: 'Na',
                     12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S',
                     17: 'Cl', 18: 'Ar', 19: 'K', 20: 'Ca', 21: 'Sc',
                     22: 'Ti', 23: 'V', 24: 'Cr', 25: 'Mn', 26: 'Fe',
                     27: 'Co', 28: 'Ni', 29: 'Cu', 30: 'Zn', 31: 'Ga',
                     32: 'Ge', 33: 'As', 34: 'Se', 35: 'Br', 36: 'Kr',
                     37: 'Rb', 38: 'Sr', 39: 'Y', 40: 'Zr', 41: 'Nb',
                     42: 'Mo', 43: 'Tc', 44: 'Ru', 45: 'Rh', 46: 'Pd',
                     47: 'Ag', 48: 'Cd', 49: 'In', 50: 'Sn', 51: 'Sb',
                     52: 'Te', 53: 'I', 54: 'Xe', 55: 'Cs', 56: 'Ba',
                     57: 'La', 58: 'Ce', 59: 'Pr', 60: 'Nd', 61: 'Pm',
                     62: 'Sm', 63: 'Eu', 64: 'Gd', 65: 'Tb', 66: 'Dy',
                     67: 'Ho', 68: 'Er', 69: 'Tm', 70: 'Yb', 71: 'Lu',
                     72: 'Hf', 73: 'Ta', 74: 'W', 75: 'Re', 76: 'Os',
                     77: 'Ir', 78: 'Pt', 79: 'Au', 80: 'Hg', 81: 'Tl',
                     82: 'Pb', 83: 'Bi', 84: 'Po', 85: 'At', 86: 'Rn',
                     87: 'Fr', 88: 'Ra', 89: 'Ac', 90: 'Th', 91: 'Pa',
                     92: 'U', 93: 'Np', 94: 'Pu', 95: 'Am', 96: 'Cm',
                     97: 'Bk', 98: 'Cf', 99: 'Es', 100: 'Fm', 101: 'Md',
                     102: 'No', 103: 'Lr'
                    }
    
    @classmethod
    def to_type(cls, sx_type):
        """return the string representation of cameca file type
        from given integer code"""
        return cls.value_map[sx_type]
        
    @classmethod
    def to_element(cls, number):
        """return atom name for given atom number"""
        return cls.element_table[number]
  
    @classmethod
    def to_line(cls, number):
        """ return stringof x-ray line from given cameca int code"""
        return cls.cameca_lines[number]
    
    def _read_the_header(self, fbio):
        """parse the header data into base cameca object atributes
        arguments:
        fbio -- file BytesIO object
        """
        fbio.seek(0)
        a, b, c, d = struct.unpack('<B3sii', fbio.read(12))
        if b != b'fxs':
            raise IOError('The file is not a cameca peaksight software file')
        self.cameca_bin_file_type = a
        self.file_type = self.to_type(a)
        self.file_version = c
        self.file_comment = fbio.read(d).decode()
        fbio.seek(0x1C, 1)  # some spacer with unknown values
        n_changes = struct.unpack('<i', fbio.read(4))[0]
        self.changes = []
        for i in range(n_changes):
            filetime, change_len = struct.unpack('<Qi',fbio.read(12))
            comment = fbio.read(change_len).decode()
            self.changes.append([filetime_to_datetime(filetime),
                                 comment])

class CamecaWDS(CamecaBase):
    def __init__(self, filename):
        self.filename = filename
        with open(filename, 'br') as fn:
            #file bytes 
            self.fbio = BytesIO()
            self.fbio.write(fn.read())
        self.file_basename = os.path.basename(filename).rsplit('.', 1)[0]
        self._read_the_header(self.fbio)
        if self.cameca_bin_file_type != 6:
            raise IOError(' '.join(['The file header shows it is not WDS',
                                    'file, but',
                                    self.file_type]))
        data_type, _, self.number_of_items = struct.unpack('<i20si', self.fbio.read(28))
        if data_type != 11:
            raise RuntimeError(''.join(['unexpected value of WDS struct: ',
                                        'instead of expected 0x0B, the value ',
                                        str(data_type), ' at the address ',
                                        str(self.fbio.tell())]))
        self.datasets = []
        for i in range(self.number_of_items):
            self.datasets.append(WDSDatasetItem(self.fbio))
        
    

class WDSDatasetItem(CamecaBase):
    def __init__(self, fbio):
        struct_type = struct.unpack('<i', fbio.read(4))[0]
        if struct_type != 0x11:
            raise IOError(' '.join(['The file readed expected the item with',
                                    'struct 0x11, not',
                                    str(struct_type)]))
        fbio.seek(4, 1)  # skip unknown
        field_names = ['x_axis', 'y_axis', 'beam_x', 'beam_y',
                       'resolution_x', 'resolution_y', 'width', 'height']
        values = struct.unpack('<4i2f2i', fbio.read(32))
        self.metadata = dict(zip(field_names, values))
        fbio.seek(12, 1) # skip some unknown values
        field_names = ['accumulation_times', 'dwell_time']
        values = struct.unpack('<if', fbio.read(8))
        self.metadata.update(dict(zip(field_names, values)))
        fbio.seek(4, 1) # skip some unknown values
        self.metadata['z_axis'] = list(struct.unpack('<49i', fbio.read(49*4)))
        fbio.seek(40, 1) # skip some unknown flags
        self.metadata['condition_file'] = read_c_hash_string(fbio)
        n_of_items = struct.unpack('<i', fbio.read(4))[0]
        self.data = []
        for i in range(n_of_items):
            self.data.append(self.read_item(fbio))
        self.name = read_c_hash_string(fbio)
        fbio.seek(316, 1)  # skip unknown flags
    
    
    def read_item(self, fbio):
        field_names = ['struct_type', 'unk_type', 'atom_number',
                       'line', 'unknw3', 'spect_no',
                       'spect_name', '2D', 'K', 'unkwn4',
                       'kV', 'current', 'peak_pos',
                       'bias', 'gain', 'dtime', 'blin',
                       'window', 'mode']
        values = struct.unpack('<7i2fi2f7i', fbio.read(76))
        item = dict(zip(field_names, values))
        fbio.seek(24, 1)  # skip some unknown values
        field_names = ['wds_start_pos', 'steps', 'step_size',
                       'dwell_time', 'beam_size?', 'data_array_size']
        values = struct.unpack('<2i2f2i', fbio.read(24))
        item.update(dict(zip(field_names, values)))
        size = item['data_array_size']
        item['data'] = np.fromstring(fbio.read(size), dtype=np.float32)
        fbio.seek(124, 1)  # skip some unknown values
        return item
                       


