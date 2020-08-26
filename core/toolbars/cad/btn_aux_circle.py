"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU 
General Public License as published by the Free Software Foundation, either version 3 of the License, 
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
from qgis.core import QgsFeature, QgsGeometry, QgsMapToPixel
from qgis.gui import QgsVertexMarker
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QDoubleValidator

from functools import partial

from ....lib import qt_tools
from ..parent_maptool import GwParentMapTool
from ....ui_manager import AuxCircle
from ...utils.giswater_tools import load_settings, open_dialog, close_dialog
from ....lib.qgis_tools import get_event_point, snap_to_current_layer, snap_to_background_layers, add_marker, \
    get_snapping_options, get_snapped_point


class GwAuxCircleButton(GwParentMapTool):
    """ Button 71: Add circle """

    def __init__(self, icon_path, text, toolbar, action_group):
        """ Class constructor """

        super().__init__(icon_path, text, toolbar, action_group)
        self.vertex_marker.setIconType(QgsVertexMarker.ICON_CROSS)
        self.cancel_circle = False
        self.layer_circle = None
        self.snap_to_selected_layer = False


    def init_create_circle_form(self, point):

        # Create the dialog and signals
        self.dlg_create_circle = AuxCircle()
        load_settings(self.dlg_create_circle)
        self.cancel_circle = False
        validator = QDoubleValidator(0.00, 999.00, 3)
        validator.setNotation(QDoubleValidator().StandardNotation)
        self.dlg_create_circle.radius.setValidator(validator)

        self.dlg_create_circle.btn_accept.clicked.connect(partial(self.get_radius, point))
        self.dlg_create_circle.btn_cancel.clicked.connect(self.cancel)
        self.dlg_create_circle.radius.setFocus()

        open_dialog(self.dlg_create_circle, self.controller, dlg_name='auxcircle')


    def get_radius(self, point):

        self.radius = self.dlg_create_circle.radius.text()
        if not self.radius:
            self.radius = 0.1
        self.delete_prev = qt_tools.isChecked(self.dlg_create_circle, self.dlg_create_circle.chk_delete_prev)

        if self.layer_circle:
            self.layer_circle.startEditing()
            close_dialog(self.dlg_create_circle)
            if self.delete_prev:
                selection = self.layer_circle.getFeatures()
                self.layer_circle.selectByIds([f.id() for f in selection])
                if self.layer_circle.selectedFeatureCount() > 0:
                    features = self.layer_circle.selectedFeatures()
                    for feature in features:
                        self.layer_circle.deleteFeature(feature.id())

            if not self.cancel_circle:
                feature = QgsFeature()
                feature.setGeometry(QgsGeometry.fromPointXY(point).buffer(float(self.radius), 100))
                provider = self.layer_circle.dataProvider()
                # Next line generate: WARNING    Attribute index 0 out of bounds [0;0]
                # but all work ok
                provider.addFeatures([feature])

            self.layer_circle.commitChanges()
            self.layer_circle.dataProvider().forceReload()
            self.layer_circle.triggerRepaint()

        else:
            self.iface.actionPan().trigger()
            self.cancel_circle = False
            return


    def cancel(self):

        close_dialog(self.dlg_create_circle)
        self.cancel_map_tool()
        if self.layer_circle:
            if self.layer_circle.isEditable():
                self.layer_circle.commitChanges()
        self.cancel_circle = True
        self.iface.setActiveLayer(self.current_layer)


    """ QgsMapTools inherited event functions """

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Escape:
            self.cancel_map_tool()
            self.iface.setActiveLayer(self.current_layer)
            return


    def canvasMoveEvent(self, event):

        # Hide marker and get coordinates
        self.vertex_marker.hide()
        event_point = get_event_point(event)

        # Snapping
        if self.snap_to_selected_layer:
            result = snap_to_current_layer(event_point)
        else:
            result = snap_to_background_layers(event_point)

        # Add marker
        add_marker(result, self.vertex_marker)


    def canvasReleaseEvent(self, event):

        if event.button() == Qt.LeftButton:

            # Get coordinates
            x = event.pos().x()
            y = event.pos().y()
            event_point = get_event_point(event)

            # Create point with snap reference
            result = snap_to_background_layers(event_point)
            point = get_snapped_point(result)

            # Create point with mouse cursor reference
            if point is None:
                point = QgsMapToPixel.toMapCoordinates(self.canvas.getCoordinateTransform(), x, y)

            self.init_create_circle_form(point)

        elif event.button() == Qt.RightButton:
            self.iface.actionPan().trigger()
            self.cancel_circle = True
            self.cancel_map_tool()
            self.iface.setActiveLayer(self.current_layer)
            return

        if self.layer_circle:
            self.layer_circle.commitChanges()


    def activate(self):

        self.snap_to_selected_layer = False
        # Check button
        self.action.setChecked(True)

        # Change cursor
        self.canvas.setCursor(self.cursor)

        # Show help message when action is activated
        if self.show_help:
            message = "Select an element and click it to set radius"
            self.controller.show_info(message)

        # Store user snapping configuration
        self.previous_snapping = get_snapping_options()

        # Get current layer
        self.current_layer = self.iface.activeLayer()

        self.layer_circle = self.controller.get_layer_by_tablename('v_edit_cad_auxcircle')
        if self.layer_circle is None:
            self.controller.show_warning("Layer not found", parameter='v_edit_cad_auxcircle')
            self.iface.actionPan().trigger()
            self.cancel_circle = True
            self.cancel_map_tool()
            self.iface.setActiveLayer(self.current_layer)
            return

        # Check for default base layer
        self.vdefault_layer = None

        row = self.controller.get_config('edit_cadtools_baselayer_vdefault')
        if row:
            self.snap_to_selected_layer = True
            self.vdefault_layer = self.controller.get_layer_by_tablename(row[0], True)
            if self.vdefault_layer:
                self.iface.setActiveLayer(self.vdefault_layer)

        if self.vdefault_layer is None:
            self.vdefault_layer = self.iface.activeLayer()


    def deactivate(self):

        # Call parent method
        super().deactivate()
        self.iface.setActiveLayer(self.current_layer)

