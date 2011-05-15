# ###################################################
# Copyright (C) 2011 The Unknown Horizons Team
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

from horizons.i18n import load_xml_translated
from horizons.util import Callback
from fife.extensions.pychan import widgets
from horizons.gui.widgets.tooltip import TooltipButton

import horizons.main

class RouteConfig(object):
	"""
	Widget that allows configurating a ship's trading route 
	"""
	dummy_icon_path = "content/gui/icons/buildmenu/outdated/dummy_btn.png"
	buy_button_path = "content/gui/images/tabwidget/buysell_buy.png"
	sell_button_path = "content/gui/images/tabwidget/buysell_sell.png"
	MAX_ENTRIES = 6
	MIN_ENTRIES = 2
	def __init__(self, instance):
		self.instance = instance

		offices = instance.session.world.get_branch_offices()
		self.branch_offices = dict([ (bo.settlement.name, bo) for bo in offices ])
		if not hasattr(instance, 'route'):
			instance.create_route()

		self._init_gui()

	def show(self):
		self._gui.show()

	def hide(self):
		self._gui.hide()

	def start_route(self):
		if len(self.widgets) < self.MIN_ENTRIES:
			return
		self.instance.route.enable()
		self._gui.findChild(name='start_route').set_inactive()

	def stop_route(self):
		self.instance.route.disable()
		self._gui.findChild(name='start_route').set_active()

	def toggle_route(self):
		if not self.instance.route.enabled:
			self.start_route()
		else:
			self.stop_route()

	def is_visible(self):
		return self._gui.isVisible()

	def toggle_visibility(self):
		if self.is_visible():
			self.hide()
		else:
			self.show()

	def remove_entry(self, entry):
		if self.resource_menu_shown:
			self.hide_resource_menu()
		enabled = self.instance.route.enabled
		self.instance.route.disable()
		vbox = self._gui.findChild(name="left_vbox")
		self.slots.pop(entry)
		position = self.widgets.index(entry)
		self.widgets.pop(position)
		self.instance.route.waypoints.pop(position)
		vbox.removeChild(entry)
		if enabled:
			self.instance.route.enable()
		if len(self.widgets) < self.MIN_ENTRIES:
			self.stop_route()
		self.hide()
		self.show()

	def show_load_icon(self, slot):
		button = slot.findChild(name="buysell")
		button.up_image = self.buy_button_path
		button.hover_image = self.buy_button_path
		slot.action = "load"

	def show_unload_icon(self, slot):
		button = slot.findChild(name="buysell")
		button.up_image = self.sell_button_path
		button.hover_image = self.sell_button_path
		slot.action = "unload"

	def toggle_load_unload(self, slot, position):
		#same hack to get the resource
		button = slot.findChild(name="buysell")
		res_button = slot.findChild(name="button")
		for res in self.instance.route.waypoints[position]['resource_list']:
			if horizons.main.db.get_res_icon(res)[0] == res_button.up_image.source:
				self.instance.route.waypoints[position]['resource_list'][res] *= -1

		if slot.action is "unload":
			self.show_load_icon(slot)
		else:
			self.show_unload_icon(slot)

	def slider_adjust(self, slot, res_id, position):
		slider = slot.findChild(name="slider")
		amount = slot.findChild(name="amount")
		value = int(slider.getValue())
		amount.text = unicode(value) + "t"
		if slot.action is "unload":
			value = -value
		self.instance.route.add_to_resource_list(position, res_id, value)
		slot.adaptLayout()

	def add_resource(self, slot, res_id, icon, position, value=0):
		button = slot.findChild(name="button")

		#remove old resource from waypoints
		#hack to see if the old image is one of the resources in the list
		for res in self.instance.route.waypoints[position]['resource_list']:
			if horizons.main.db.get_res_icon(res)[0] == button.up_image.source:
				self.instance.route.remove_from_resource_list(position, res)
				break

		button.up_image, button.down_image, button.hover_image = icon, icon, icon

		#hide the resource menu
		self.hide_resource_menu()
		
		slider = slot.findChild(name="slider")
		if value < 0:
			self.show_unload_icon(slot)
			slider.setValue(float(-value))
			amount = -value
		else:
			self.show_load_icon(slot)
			slider.setValue(float(value))
			amount = value

		if res_id != 0:
			slot.findChild(name="amount").text = unicode(amount) + "t"
			slot.adaptLayout()
			self.instance.route.add_to_resource_list(position, res_id, value)
			slider.capture(Callback(self.slider_adjust, slot, res_id, position))
		else:
			slot.findChild(name="amount").text = unicode("")

	def show_resource_menu(self, slot, position):
		if self.resource_menu_shown:
			return
		self.resource_menu_shown = True
		vbox = self._gui.findChild(name="resources")
		label = self._gui.findChild(name="select_res_label")
		label.text = unicode("Select Resources")

		resources = horizons.main.db.get_res_id_and_icon(True)
		#hardcoded for 5 works better than vbox.width / button_width
		amount_per_line = 5

		current_hbox = widgets.HBox()
		index = 1

		for (res_id, icon) in [(0, self.dummy_icon_path)] + list(resources):
			if res_id in self.instance.route.waypoints[position]['resource_list']:
				continue
			button = TooltipButton(size=(50,50))
			button.up_image, button.down_image, button.hover_image = icon, icon, icon
			button.capture(Callback(self.add_resource, slot, res_id, icon, position))
			if res_id != 0:
				button.tooltip = horizons.main.db.get_res_name(res_id)
			current_hbox.addChild(button)
			if index > amount_per_line:
				index -= amount_per_line
				vbox.addChild(current_hbox)
				current_hbox = widgets.HBox()
			index += 1
		vbox.addChild(current_hbox)

		self.hide()
		self.show()

	def hide_resource_menu(self):
		self.resource_menu_shown = False
		self._gui.findChild(name="resources").removeAllChildren()
		self._gui.findChild(name="select_res_label").text = unicode("")

	def add_trade_slots(self, entry, num):
		x_position = 90
		#initialize slots with empty dict
		self.slots[entry] = {}
		for num in range(0,num):
			slot = load_xml_translated('trade_single_slot.xml')
			slot.position = x_position, 0

			slot.action = "load"

			slider = slot.findChild(name="slider")
			slider.setScaleStart(0.0)
			slider.setScaleEnd(float(self.instance.inventory.limit))

			position = self.widgets.index(entry)

			slot.findChild(name="buysell").capture(Callback(self.toggle_load_unload, slot, position))

			button = slot.findChild(name="button")
			button.capture(Callback(self.show_resource_menu, slot, position))
			button.up_image = self.dummy_icon_path
			button.down_image = self.dummy_icon_path
			button.hover_image = self.dummy_icon_path

			icon = slot.findChild(name="icon")
			fillbar = slot.findChild(name="fillbar")
			fillbar.position = (icon.width - fillbar.width -1, icon.height)
			x_position += 60

			entry.addChild(slot)
			self.slots[entry][num] = slot

	def add_gui_entry(self, branch_office, resource_list = {}):
		vbox = self._gui.findChild(name="left_vbox")
		entry = load_xml_translated("route_entry.xml")
		self.widgets.append(entry)

		label = entry.findChild(name="bo_name")
		label.text = unicode(branch_office.settlement.name)

		self.add_trade_slots(entry, self.slots_per_entry)

		index = 1
		for res_id in resource_list:
			if index > self.slots_per_entry:
				break
			icon = horizons.main.db.get_res_icon(res_id)[0]
			self.add_resource(self.slots[entry][index - 1],\
			                  res_id, icon, \
			                  self.widgets.index(entry), \
			                  resource_list[res_id])
			index += 1

		entry.mapEvents({
		  'delete_bo/mouseClicked' : Callback(self.remove_entry, entry)
		  })
		vbox.addChild(entry)

	def append_bo(self):
		if len(self.widgets) >= self.MAX_ENTRIES:
			return

		selected = self.listbox._getSelectedItem()

		if selected == None:
			return

		try:
			#if a new branch office is added to the list hide the resource menu
			self.instance.route.append(self.branch_offices[selected])
			self.add_gui_entry(self.branch_offices[selected])
			if self.resource_menu_shown:
				self.hide_resource_menu()
		except IndexError:
			pass

		self.hide()
		self.show()

	def _init_gui(self):
		"""
		Initial init of gui.
		widgets : list of route entry widgets
		slots : dict with slots for each entry
		"""
		self._gui = load_xml_translated("configure_route.xml")
		self.listbox = self._gui.findChild(name="branch_office_list")
		self.listbox._setItems(list(self.branch_offices))

		self.widgets=[]
		self.slots={}
		self.slots_per_entry = 3

		#don't do any actions if the resource menu is shown
		self.resource_menu_shown = False
		for entry in self.instance.route.waypoints:
			self.add_gui_entry(entry['branch_office'], entry['resource_list'])
		# we want escape key to close the widget, what needs to be fixed here?
		#self._gui.on_escape = self.hide
		if self.instance.route.enabled:
			self._gui.findChild(name='start_route').set_inactive()

		self._gui.mapEvents({
		  'cancelButton' : self.hide,
		  'add_bo/mouseClicked' : self.append_bo,
		  'start_route/mouseClicked' : self.toggle_route
		  })
		self._gui.position_technique = "automatic" # "center:center"
