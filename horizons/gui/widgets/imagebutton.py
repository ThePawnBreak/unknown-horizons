# ###################################################
# Copyright (C) 2013 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.
#
# Unknown Horizons is free software; you can redistribute it and/or modify
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
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

from fife.extensions.pychan.widgets import ImageButton as FifeImageButton
from fife.extensions.pychan.widgets.common import Attr


class ImageButton(FifeImageButton):
	"""Extends ImageButton functionality by providing a new path= attribute.
	Unless manually overridden, specifying path="path/to/file" (note: no .png
	extension) will interpret that as these attributes:

	      up_image = "content/gui/path/to/file.png"
	    down_image = "content/gui/path/to/file_d.png"
	   hover_image = "content/gui/path/to/file_h.png"
	inactive_image = "content/gui/path/to/file_bw.png"

	If some of those files could not be found, pychan uses up_image instead.
	inactive_image only applies to ToggleImageButton (a custom UH widget)
	and widgets derived from it. Sets is_focusable to False unless overridden.
	"""
	ATTRIBUTES = FifeImageButton.ATTRIBUTES + [Attr('path')]
	IMAGE = "content/gui/{path}{{mode}}.png"

	def __init__(self, path='', is_focusable=False, **kwargs):
		super(ImageButton, self).__init__(is_focusable=is_focusable, **kwargs)
		if path:
			# initializing from python, not xml, so path is available here
			# and should be set
			self.path = path

	def _get_path(self):
		return self.__path

	def _set_path(self, path):
		self.__path = path
		image_path = self.IMAGE.format(path=path)
		self.up_image = image_path.format(mode='')
		try:
			self.hover_image = image_path.format(mode='_h')
		except RuntimeError:
			# RuntimeError: _[NotFound]_ , Something was searched, but not found
			# by default, pychan will set hover_image to be the same as up_image
			pass
		try:
			self.down_image = image_path.format(mode='_d')
		except RuntimeError:
			pass

		#TODO move ToggleImageButton into this file

	path = property(_get_path, _set_path)


class OkButton(ImageButton):
	"""The OkButton is a shortcut for an ImageButton with our OK / apply icon.
	Its default attributes are:
	name="okButton" path="images/buttons/ok"
	"""
	DEFAULT_NAME = 'okButton'
	def __init__(self, name=None, **kwargs):
		if name is None:
			name = self.__class__.DEFAULT_NAME
		size = (34, 40)
		super(OkButton, self).__init__(
			name=name, is_focusable=False,
			max_size=size, min_size=size, size=size, **kwargs)
		self.path = "images/buttons/ok"

class CancelButton(ImageButton):
	"""The CancelButton is a shortcut for an ImageButton with our cancel / close
	icon. Its default attributes are:
	name="cancelButton" path="images/buttons/close"
	"""
	DEFAULT_NAME = 'cancelButton'
	def __init__(self, name=None, **kwargs):
		if name is None:
			name = self.__class__.DEFAULT_NAME
		size = (34, 40)
		super(CancelButton, self).__init__(
			name=name, is_focusable=False,
			max_size=size, min_size=size, size=size, **kwargs)
		self.path = "images/buttons/close"

class DeleteButton(ImageButton):
	"""The DeleteButton is a shortcut for an ImageButton with our delete / tear
	icon. Its default attributes are:
	name="deleteButton" path="images/buttons/delete"
	"""
	DEFAULT_NAME = 'deleteButton'
	def __init__(self, name=None, **kwargs):
		if name is None:
			name = self.__class__.DEFAULT_NAME
		size = (34, 40)
		super(DeleteButton, self).__init__(
			name=name, is_focusable=False,
			max_size=size, min_size=size, size=size, **kwargs)
		self.path = "images/buttons/delete"


class MainmenuButton(ImageButton):
	"""For use in main menu. bw: whether to use greyscale or color."""

	ATTRIBUTES = ImageButton.ATTRIBUTES + [Attr('icon')]
	ICON = "content/gui/icons/mainmenu/{icon}{bw}.png"

	def __init__(self, icon='door', **kwargs):
		super(MainmenuButton, self).__init__(is_focusable=False, **kwargs)
		self.icon = icon

	def _get_icon(self):
		return self.__icon

	def _set_icon(self, icon):
		self.__icon = icon
		self.up_image = self.ICON.format(icon=icon, bw='_bw')
		self.hover_image = self.down_image = self.ICON.format(icon=icon, bw='')

	icon = property(_get_icon, _set_icon)
