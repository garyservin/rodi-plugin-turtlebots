#!/usr/bin/env python
# Copyright (c) 2013, Gary Servin <garyservin@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import sys
import commands

from gettext import gettext as _
from plugins.plugin import Plugin

from TurtleArt.tapalette import make_palette
from TurtleArt.tapalette import palette_name_to_index
from TurtleArt.tapalette import palette_blocks
from TurtleArt.tapalette import special_block_colors
from TurtleArt.talogo import logoerror
from TurtleArt.tautils import debug_output
from TurtleArt.taconstants import CONSTANTS
from TurtleArt.taprimitive import Primitive, ArgSlot, ConstantArg
from TurtleArt.tatype import TYPE_INT, TYPE_FLOAT, TYPE_STRING, TYPE_NUMBER

sys.path.insert(0, os.path.abspath('./plugins/rodi'))
import pyfirmata


VALUE = {_('HIGH'): 1, _('LOW'): 0}
MODE = {_('INPUT'): pyfirmata.INPUT, _('OUTPUT'): pyfirmata.OUTPUT,
        _('PWM'): pyfirmata.PWM, _('SERVO'): pyfirmata.SERVO}

MAX_SPEED = 90
DISTANCE_SENSOR = 0
LEFT_SERVO = 5
RIGHT_SERVO = 6

COLOR_NOTPRESENT = ["#A0A0A0","#808080"]
COLOR_PRESENT = ["#6A8DF6","#5A7DE6"]

ERROR = _('ERROR: Check the connection with the robot.')
ERROR_SPEED = _('ERROR: The speed must be a value between 0 and %d' %(MAX_SPEED))
ERROR_SPEED_ABS = _('ERROR: The speed must be a value between -%d and %d' %(MAX_SPEED, MAX_SPEED))

class Rodi(Plugin):

    def __init__(self, parent):
        Plugin.__init__(self);
        self.tw = parent
        self._baud = 57600
        self.active_rodi = 0
        self._rodis = []
        self._rodis_it = []
        self._rodis_pines = []
        self.actualSpeed = [50, 50]

    def setup(self):
        """ Setup is called once, when the Turtle Window is created. """
        palette = make_palette('rodi', COLOR_NOTPRESENT,
                             _('Palette for Rodi bots using Arduino'))

        palette.add_block('refresh_Rodi',
                     style='basic-style',
                     label=_('refresh Rodi'),
                     prim_name='refresh_Rodi',
                     help_string=_('refresh the state of the Rodi palette and blocks'))
        self.tw.lc.def_prim('refresh_Rodi', 0,
            Primitive(self.refresh_Rodi))
        special_block_colors['refresh_Rodi'] = COLOR_PRESENT[:]

        palette.add_block('move_Rodi',
                     style='basic-style-2arg',
                     label=[_('move Rodi'), _('left'), _('right')],
                     prim_name='move_Rodi',
                     default=[50, 50],
                     help_string=_('moves the Rodi motors at the specified speed'))
        self.tw.lc.def_prim('move_Rodi', 2,
            Primitive(self.move_Rodi, arg_descs=[ArgSlot(TYPE_NUMBER), ArgSlot(TYPE_NUMBER)]))
        special_block_colors['move_Rodi'] = COLOR_NOTPRESENT[:]

        palette.add_block('stop_Rodi',
                     style='basic-style',
                     label=_('stop Rodi'),
                     prim_name='stop_Rodi',
                     help_string=_('stop the Rodi robot'))
        self.tw.lc.def_prim('stop_Rodi', 0,
            Primitive(self.stop_Rodi))
        special_block_colors['stop_Rodi'] = COLOR_NOTPRESENT[:]

        palette.add_block('forward_Rodi',
                     style='basic-style',
                     label=_('forward Rodi'),
                     prim_name='forward_Rodi',
                     help_string=_('move the Rodi robot forward'))
        self.tw.lc.def_prim('forward_Rodi', 0,
            Primitive(self.forward_Rodi))
        special_block_colors['forward_Rodi'] = COLOR_NOTPRESENT[:]

        palette.add_block('left_Rodi',
                     style='basic-style',
                     label=_('left Rodi'),
                     prim_name='left_Rodi',
                     help_string=_('turn the Rodi robot at left'))
        self.tw.lc.def_prim('left_Rodi', 0,
            Primitive(self.left_Rodi))
        special_block_colors['left_Rodi'] = COLOR_NOTPRESENT[:]

        palette.add_block('right_Rodi',
                     style='basic-style',
                     label=_('right Rodi'),
                     prim_name='right_Rodi',
                     help_string=_('turn the Rodi robot at right'))
        self.tw.lc.def_prim('right_Rodi', 0,
            Primitive(self.right_Rodi))
        special_block_colors['right_Rodi'] = COLOR_NOTPRESENT[:]

        palette.add_block('backward_Rodi',
                     style='basic-style',
                     label=_('backward Rodi'),
                     prim_name='backward_Rodi',
                     help_string=_('move the Rodi robot backward'))
        self.tw.lc.def_prim('backward_Rodi', 0,
            Primitive(self.backward_Rodi))
        special_block_colors['backward_Rodi'] = COLOR_NOTPRESENT[:]

        palette.add_block('distanced_Rodi',
                     style='box-style',
                     label=_('distance Rodi'),
                     prim_name='distance_Rodi',
                     help_string=_('returns the distance as a value between 0 and 1'))
        self.tw.lc.def_prim('distance_Rodi', 0,
            Primitive(self.distance_Rodi, TYPE_FLOAT))
        special_block_colors['distance_Rodi'] = COLOR_NOTPRESENT[:]

    ############################### Turtle signals ############################

    def stop(self):
        self.stopRodis()

    def quit(self):
        self.closeRodis()

    ################################ Refresh process ################################

    def _check_init(self):
        n = len(self._rodis)
        if (self.active_rodi > n) and (self.active_rodi < 0):
            r = self._rodis[sef.active_rodi]
        else:
            raise logoerror(_('Not found Rodi %s') % (self.active_rodi + 1))

    def change_color_blocks(self):
        if len(self._rodis) > 0:
            rodi_present = True
        else:
            rodi_present = False
        index = palette_name_to_index('rodi')
        if index is not None:
            rodi_blocks = palette_blocks[index]
            for block in self.tw.block_list.list:
                if block.type in ['proto', 'block']:
                    if block.name in rodi_blocks:
                        if (rodi_present) or (block.name == 'refresh_Rodi'):
                            special_block_colors[block.name] = COLOR_PRESENT[:]
                        else:
                            special_block_colors[block.name] = COLOR_NOTPRESENT[:]
                        block.refresh()
            self.tw.regenerate_palette(index)

    def refresh_Rodi(self):
        #Close actual Rodis
        self.closeRodis()
        self._rodis = []
        self._rodis_it = []

        #Search for new Rodis
        #status,output_usb = commands.getstatusoutput("ls /dev/ | grep ttyUSB")
        #output_usb_parsed = output_usb.split('\n')
        #status,output_acm = commands.getstatusoutput("ls /dev/ | grep ttyACM")
        #output_acm_parsed = output_acm.split('\n')

        # add rfcomm to the list of rodis
        status,output_rfc = commands.getstatusoutput("ls /dev/ | grep rfcomm")
        output_rfc_parsed = output_rfc.split('\n')

        #output = output_usb_parsed
        #output.extend(output_acm_parsed)
        output = output_rfc_parsed

        for dev in output:
            if not(dev == ''):
                n = '/dev/%s' % dev
                try:
                    r = pyfirmata.Arduino(n, baudrate=self._baud)
                    it = pyfirmata.util.Iterator(r)
                    it.start()
                    self._rodis.append(r)
                    self._rodis_it.append(it)
                except:
                    raise logoerror(_('Error loading %s board') % n)

        self.change_color_blocks()

    ################################ Movement calls ################################

    def set_vels(self, left, right):
        try:
            r = self._rodis[self.active_rodi]
            lMode = r.digital[LEFT_SERVO]._get_mode()
            rMode = r.digital[RIGHT_SERVO]._get_mode()
            if left == 0:
                r.digital[LEFT_SERVO]._set_mode(MODE['OUTPUT'])
            else:
                r.digital[LEFT_SERVO]._set_mode(MODE['SERVO'])
                r.digital[LEFT_SERVO].write(MAX_SPEED + left)

            if right == 0:
                r.digital[RIGHT_SERVO]._set_mode(MODE['OUTPUT'])
            else:
                r.digital[RIGHT_SERVO]._set_mode(MODE['SERVO'])
                r.digital[RIGHT_SERVO].write(MAX_SPEED - right)
        except:
            raise logoerror(ERROR)

    def move_Rodi(self, left, right):
        try:
            left = int(left)
        except:
            left = 0
        if (left < -MAX_SPEED) or (left > MAX_SPEED):
            raise logoerror(ERROR_SPEED_ABS)
        try:
            right = int(right)
        except:
            right = 0
        if (right < -MAX_SPEED) or (right > MAX_SPEED):
            raise logoerror(ERROR_SPEED_ABS)
        self.set_vels(left, right)

    def forward_Rodi(self):
        self.set_vels(self.actualSpeed[0], self.actualSpeed[1])

    def backward_Rodi(self):
        self.set_vels(-self.actualSpeed[0], -self.actualSpeed[1])

    def left_Rodi(self):
        self.set_vels(-self.actualSpeed[0], self.actualSpeed[1])

    def right_Rodi(self):
        self.set_vels(self.actualSpeed[0], -self.actualSpeed[1])

    def stop_Rodi(self):
        self.set_vels(0, 0)

    ################################ Sensors calls ################################

    def distance_Rodi(self):
        res = -1
        try:
            r = self._rodis[self.active_rodi]
            r.analog[DISTANCE_SENSOR].enable_reporting()
            r.time_pass(0.05)
            res = r.analog[DISTANCE_SENSOR].read()
            r.analog[DISTANCE_SENSOR].disable_reporting()
        except:
            pass
        return res

    def closeRodis(self):
        for dev in self._rodis:
            try:
                dev.exit()
            except:
                pass

    def stopRodis(self):
        for dev in self._rodis:
            try:
                dev.digital[LEFT_SERVO]._set_mode(MODE['OUTPUT'])
                dev.digital[RIGHT_SERVO]._set_mode(MODE['OUTPUT'])
            except:
                pass

