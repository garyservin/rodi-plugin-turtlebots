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
from TurtleArt.taprimitive import Primitive, ArgSlot
from TurtleArt.tatype import TYPE_INT, TYPE_FLOAT, TYPE_STRING, TYPE_NUMBER

sys.path.insert(0, os.path.abspath('./plugins/rodi'))
from rodi_py import rodi


VALUE = {_('HIGH'): 1, _('LOW'): 0}

MAX_SPEED = 100

COLOR_NOTPRESENT = ["#A0A0A0","#808080"]
COLOR_PRESENT = ["#6A8DF6","#5A7DE6"]

ERROR = _('ERROR: Check the connection with the robot.')
ERROR_SPEED = _('ERROR: The speed must be a value between 0 and %d' %(MAX_SPEED))
ERROR_SPEED_ABS = _('ERROR: The speed must be a value between -%(max)d and %(max)d') % {'max': MAX_SPEED}

class Rodi(Plugin):

    def __init__(self, parent):
        Plugin.__init__(self);
        self.tw = parent
        self.active_rodi = 0
        self._rodis = []
        self.actualSpeed = [100, 100]

    def setup(self):
        """ Setup is called once, when the Turtle Window is created. """
        palette = make_palette('rodi', COLOR_NOTPRESENT,
                             _('Palette for RoDI bots using Arduino'))

        palette.add_block('refresh_Rodi',
                     style='basic-style',
                     label=_('refresh RoDI'),
                     prim_name='refresh_Rodi',
                     help_string=_('refresh the state of the RoDI palette and blocks'))
        self.tw.lc.def_prim('refresh_Rodi', 0,
            Primitive(self.refresh_Rodi))
        special_block_colors['refresh_Rodi'] = COLOR_PRESENT[:]

        palette.add_block('select_Rodi',
                          style='basic-style-1arg',
                          default = 1,
                          label=_('RoDI'),
                          help_string=_('set current RoDI robot'),
                          prim_name = 'select_Rodi')
        self.tw.lc.def_prim('select_Rodi', 1,
            Primitive(self.select_Rodi, arg_descs=[ArgSlot(TYPE_NUMBER)]))

        palette.add_block('count_Rodi',
                          style='box-style',
                          label=_('number of RoDIs'),
                          help_string=_('number of RoDI robots'),
                          prim_name = 'count_Rodi')
        self.tw.lc.def_prim('count_Rodi', 0,
            Primitive(self.count_Rodi, TYPE_INT))

        palette.add_block('name_Rodi',
                  style='number-style-1arg',
                  label=_('RoDI name'),
                  default=[1],
                  help_string=_('Get the name of a RoDI robot'),
                  prim_name='name_Rodi')
        self.tw.lc.def_prim('name_Rodi', 1,
            Primitive(self.name_Rodi, TYPE_STRING, [ArgSlot(TYPE_NUMBER)]))

        palette.add_block('move_Rodi',
                     style='basic-style-2arg',
                     label=[_('move RoDI'), _('left'), _('right')],
                     prim_name='move_Rodi',
                     default=[100, 100],
                     help_string=_('moves the RoDI motors at the specified speed'))
        self.tw.lc.def_prim('move_Rodi', 2,
            Primitive(self.move_Rodi, arg_descs=[ArgSlot(TYPE_NUMBER), ArgSlot(TYPE_NUMBER)]))
        special_block_colors['move_Rodi'] = COLOR_NOTPRESENT[:]

        palette.add_block('stop_Rodi',
                     style='basic-style',
                     label=_('stop RoDI'),
                     prim_name='stop_Rodi',
                     help_string=_('stop the RoDI robot'))
        self.tw.lc.def_prim('stop_Rodi', 0,
            Primitive(self.stop_Rodi))
        special_block_colors['stop_Rodi'] = COLOR_NOTPRESENT[:]

        palette.add_block('forward_Rodi',
                     style='basic-style',
                     label=_('forward RoDI'),
                     prim_name='forward_Rodi',
                     help_string=_('move the RoDI robot forward'))
        self.tw.lc.def_prim('forward_Rodi', 0,
            Primitive(self.forward_Rodi))
        special_block_colors['forward_Rodi'] = COLOR_NOTPRESENT[:]

        palette.add_block('left_Rodi',
                     style='basic-style',
                     label=_('left RoDI'),
                     prim_name='left_Rodi',
                     help_string=_('turn the RoDI robot at left'))
        self.tw.lc.def_prim('left_Rodi', 0,
            Primitive(self.left_Rodi))
        special_block_colors['left_Rodi'] = COLOR_NOTPRESENT[:]

        palette.add_block('right_Rodi',
                     style='basic-style',
                     label=_('right RoDI'),
                     prim_name='right_Rodi',
                     help_string=_('turn the RoDI robot at right'))
        self.tw.lc.def_prim('right_Rodi', 0,
            Primitive(self.right_Rodi))
        special_block_colors['right_Rodi'] = COLOR_NOTPRESENT[:]

        palette.add_block('backward_Rodi',
                     style='basic-style',
                     label=_('backward RoDI'),
                     prim_name='backward_Rodi',
                     help_string=_('move the RoDI robot backward'))
        self.tw.lc.def_prim('backward_Rodi', 0,
            Primitive(self.backward_Rodi))
        special_block_colors['backward_Rodi'] = COLOR_NOTPRESENT[:]

        palette.add_block('see_Rodi',
                     style='box-style',
                     label=_('RoDI see'),
                     prim_name='see_Rodi',
                     help_string=_('returns the distance as a value between 0 and 100 cm'))
        self.tw.lc.def_prim('see_Rodi', 0,
            Primitive(self.see_Rodi, TYPE_NUMBER))
        special_block_colors['see_Rodi'] = COLOR_NOTPRESENT[:]

        palette.add_block('sense_left_Rodi',
                     style='box-style',
                     label=_('RoDI sense left'),
                     prim_name='sense_left_Rodi',
                     help_string=_('returns the left line sensor as a value between 0 and 1023'))
        self.tw.lc.def_prim('sense_left_Rodi', 0,
            Primitive(self.sense_left_Rodi, TYPE_NUMBER))
        special_block_colors['sense_left_Rodi'] = COLOR_NOTPRESENT[:]

        palette.add_block('sense_right_Rodi',
                     style='box-style',
                     label=_('RoDI sense right'),
                     prim_name='right_sensor_Rodi',
                     help_string=_('returns the right line sensor as a value between 0 and 1023'))
        self.tw.lc.def_prim('right_sensor_Rodi', 0,
            Primitive(self.sense_right_Rodi, TYPE_NUMBER))
        special_block_colors['right_sensor_Rodi'] = COLOR_NOTPRESENT[:]

        palette.add_block('sense_light_Rodi',
                     style='box-style',
                     label=_('RoDI sense light'),
                     prim_name='sense_light_Rodi',
                     help_string=_('returns the ambient light as a value between 0 and 1023'))
        self.tw.lc.def_prim('sense_light_Rodi', 0,
            Primitive(self.sense_light_Rodi, TYPE_NUMBER))
        special_block_colors['sense_light_Rodi'] = COLOR_NOTPRESENT[:]

        palette.add_block('play_Rodi',
                     style='basic-style-2arg',
                     label=[_('RoDI play'), _('note'), _('duration')],
                     prim_name='play_Rodi',
                     default=[31, 250],
                     help_string=_('make RoDI play a not for a specified duration'))
        self.tw.lc.def_prim('play_Rodi', 2,
            Primitive(self.play_Rodi, arg_descs=[ArgSlot(TYPE_NUMBER), ArgSlot(TYPE_NUMBER)]))
        special_block_colors['play_Rodi'] = COLOR_NOTPRESENT[:]

        palette.add_block('pixel_Rodi',
                     style='basic-style-3arg',
                     label=[_('RoDI pixel'), _('red'), _('green'), _('blue')],
                     prim_name='pixel_Rodi',
                     default=[0, 0, 0],
                     help_string=_('set the color of the pixel'))
        self.tw.lc.def_prim('pixel_Rodi', 3,
            Primitive(self.pixel_Rodi, arg_descs=[ArgSlot(TYPE_NUMBER), ArgSlot(TYPE_NUMBER), ArgSlot(TYPE_NUMBER)]))
        special_block_colors['pixel_Rodi'] = COLOR_NOTPRESENT[:]

        palette.add_block('led_Rodi',
                     style='basic-style-1arg',
                     label=[_('RoDI led'), _('state')],
                     prim_name='led_Rodi',
                     default=[1],
                     help_string=_('set the state of the led (on = 1 | off = 0'))
        self.tw.lc.def_prim('led_Rodi', 1,
            Primitive(self.led_Rodi, arg_descs=[ArgSlot(TYPE_NUMBER)]))
        special_block_colors['led_Rodi'] = COLOR_NOTPRESENT[:]

    ############################## Turtle signals ##############################

    def stop(self):
        self.stopRodis()

    def quit(self):
        pass

    ############################ Select functions ##############################

    def select_Rodi(self, i):
        n = len(self._rodis)
        try:
            i = int(i)
        except:
            raise logoerror(_('The device must be an integer'))
        i = i - 1
        if (i < n) and (i >= 0):
            self.active_arduino = i
        else:
            raise logoerror(_('Not found Rodi %s') % (i + 1))

    def count_Rodi(self):
        return len(self._rodis)

    def name_Rodi(self, i):
        n = len(self._rodis)
        try:
            i = int(i)
        except:
            raise logoerror(_('The device must be an integer'))
        i = i - 1
        if (i < n) and (i >= 0):
            a = self._arduinos[i]
            return a.name
        else:
            raise logoerror(_('Not found Rodi %s') % (i + 1))

    ############################## Refresh process #############################

    def _check_init(self):
        n = len(self._rodis)
        if (self.active_rodi > n) or (self.active_rodi < 0):
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
        try:
            r = rodi.RoDI()
            self._rodis.append(r)
            if r.see() is not None:
                self.change_color_blocks()
            else:
                del self._rodis[-1]
        except:
            raise logoerror(_('Error connecting to RoDI'))


    def closeRodis(self):
        pass

    ############################ Action calls ################################

    def set_vels(self, left, right):
        try:
            r = self._rodis[self.active_rodi]
            r.move(left, right)
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

    def stopRodis(self):
        for rodi in self._rodis:
            try:
                rodi.stop()
            except:
                pass

    def blink_Rodi(self, period):
        try:
            r = self._rodis[self.active_rodi]
            r.blink(period)
        except:
            raise logoerror(ERROR)

    def play_Rodi(self, note, duration):
        try:
            r = self._rodis[self.active_rodi]
            r.sing(note, duration)
        except:
            raise logoerror(ERROR)

    def pixel_Rodi(self, red, green, blue):
        try:
            r = self._rodis[self.active_rodi]
            r.pixel(red, green, blue)
        except:
            raise logoerror(ERROR)

    def led_Rodi(self, state):
        try:
            r = self._rodis[self.active_rodi]
            r.led(state)
        except:
            raise logoerror(ERROR)

    ################################ Sensors calls ################################

    def see_Rodi(self):
        res = -1
        try:
            r = self._rodis[self.active_rodi]
            res = r.see()
        except:
            pass
        return res

    def sense_left_Rodi(self):
        res = -1
        try:
            r = self._rodis[self.active_rodi]
            res = r.sense()[0]
        except:
            pass
        return res

    def sense_right_Rodi(self):
        res = -1
        try:
            r = self._rodis[self.active_rodi]
            res = r.sense()[1]
        except:
            pass
        return res

    def sense_light_Rodi(self):
        res = -1
        try:
            r = self._rodis[self.active_rodi]
            res = r.light()
        except:
            pass
        return res

