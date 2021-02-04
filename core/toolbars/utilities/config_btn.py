"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
import json
import operator
from functools import partial

from qgis.PyQt.QtCore import QDate
from qgis.PyQt.QtWidgets import QComboBox, QCheckBox, QDateEdit, QDoubleSpinBox, QSpinBox, QGroupBox, QSpacerItem, \
    QSizePolicy, QGridLayout, QWidget, QLabel, QTextEdit, QLineEdit
from qgis.gui import QgsDateTimeEdit

from ..dialog import GwAction
from ...ui.ui_manager import GwConfigUi
from ...utils import tools_gw
from ....lib import tools_qt, tools_db, tools_qgis


class GwConfigButton(GwAction):
    """ Button 99: Config """

    def __init__(self, icon_path, action_name, text, toolbar, action_group):

        super().__init__(icon_path, action_name, text, toolbar, action_group)


    def clicked_event(self):

        self._open_config()


    # region private functions

    def _open_config(self):

        # Get user and role
        super_users = tools_gw.get_config_parser('system', 'super_users', "project", "giswater")
        cur_user = tools_db.get_current_user()

        self.list_update = []

        # Get visible layers name from TOC
        result = self._get_layers_name()

        body = tools_gw.create_body(form='"formName":"config"', extras=result)
        json_result = tools_gw.execute_procedure('gw_fct_getconfig', body)
        if not json_result or json_result['status'] == 'Failed':
            return False

        self.dlg_config = GwConfigUi()
        tools_gw.load_settings(self.dlg_config)
        self.dlg_config.btn_cancel.clicked.connect(partial(tools_gw.close_dialog, self.dlg_config))
        self.dlg_config.btn_accept.clicked.connect(partial(self._update_values))

        page1_layout1 = self.dlg_config.tab_main.findChild(QGridLayout, 'page1_layout1')
        page1_layout2 = self.dlg_config.tab_main.findChild(QGridLayout, 'page1_layout2')
        page2_layout1 = self.dlg_config.tab_main.findChild(QGridLayout, 'page2_layout1')
        page2_layout2 = self.dlg_config.tab_main.findChild(QGridLayout, 'page2_layout2')

        admin_layout1 = self.dlg_config.tab_main.findChild(QGridLayout, 'admin_layout1')
        admin_layout2 = self.dlg_config.tab_main.findChild(QGridLayout, 'admin_layout2')

        man_layout1 = self.dlg_config.tab_main.findChild(QGridLayout, 'man_layout1')
        man_layout2 = self.dlg_config.tab_main.findChild(QGridLayout, 'man_layout2')

        addfields_layout1 = self.dlg_config.tab_main.findChild(QGridLayout, 'addfields_layout1')

        group_box_1 = QGroupBox("Basic")
        group_box_2 = QGroupBox("O&&M")
        group_box_3 = QGroupBox("Inventory")
        group_box_4 = QGroupBox("Mapzones")
        group_box_5 = QGroupBox("Edit")
        group_box_6 = QGroupBox("Epa")
        group_box_7 = QGroupBox("MasterPlan")
        group_box_8 = QGroupBox("Other")

        group_box_9 = QGroupBox("Node")
        group_box_10 = QGroupBox("Arc")
        group_box_11 = QGroupBox("Utils")
        group_box_12 = QGroupBox(f"Connec")
        group_box_13 = QGroupBox(f"Gully")

        group_box_14 = QGroupBox("Topology")
        group_box_15 = QGroupBox("Builder")
        group_box_16 = QGroupBox("Review")
        group_box_17 = QGroupBox("Analysis")
        group_box_18 = QGroupBox("System")

        group_box_19 = QGroupBox("Fluid type")
        group_box_20 = QGroupBox("Location type")
        group_box_21 = QGroupBox("Category type")
        group_box_22 = QGroupBox("Function type")

        group_box_23 = QGroupBox("Addfields")


        self.basic_form = QGridLayout()
        self.om_form = QGridLayout()
        self.inventory_form = QGridLayout()
        self.mapzones_form = QGridLayout()
        self.cad_form = QGridLayout()
        self.epa_form = QGridLayout()
        self.masterplan_form = QGridLayout()
        self.other_form = QGridLayout()

        self.node_type_form = QGridLayout()
        self.cat_form = QGridLayout()
        self.utils_form = QGridLayout()
        self.connec_form = QGridLayout()
        self.gully_form = QGridLayout()

        self.topology_form = QGridLayout()
        self.builder_form = QGridLayout()
        self.review_form = QGridLayout()
        self.analysis_form = QGridLayout()
        self.system_form = QGridLayout()

        self.fluid_type_form = QGridLayout()
        self.location_type_form = QGridLayout()
        self.category_type_form = QGridLayout()
        self.function_type_form = QGridLayout()

        self.addfields_form = QGridLayout()

        # Construct form for config and admin
        self._build_dialog_options(json_result['body']['form']['formTabs'], 0)
        self._construct_form_param_system(json_result['body']['form']['formTabs'], 1)

        group_box_1.setLayout(self.basic_form)
        group_box_2.setLayout(self.om_form)
        group_box_3.setLayout(self.inventory_form)
        group_box_4.setLayout(self.mapzones_form)
        group_box_5.setLayout(self.cad_form)
        group_box_6.setLayout(self.epa_form)
        group_box_7.setLayout(self.masterplan_form)
        group_box_8.setLayout(self.other_form)

        group_box_9.setLayout(self.node_type_form)
        group_box_10.setLayout(self.cat_form)
        group_box_11.setLayout(self.utils_form)
        group_box_12.setLayout(self.connec_form)
        group_box_13.setLayout(self.gully_form)

        group_box_14.setLayout(self.topology_form)
        group_box_15.setLayout(self.builder_form)
        group_box_16.setLayout(self.review_form)
        group_box_17.setLayout(self.analysis_form)
        group_box_18.setLayout(self.system_form)

        group_box_19.setLayout(self.fluid_type_form)
        group_box_20.setLayout(self.location_type_form)
        group_box_21.setLayout(self.category_type_form)
        group_box_22.setLayout(self.function_type_form)

        group_box_23 .setLayout(self.addfields_form)

        page1_layout1.addWidget(group_box_1)
        page1_layout1.addWidget(group_box_2)
        page1_layout1.addWidget(group_box_3)
        page1_layout1.addWidget(group_box_4)
        page1_layout2.addWidget(group_box_5)
        page1_layout2.addWidget(group_box_6)
        page1_layout2.addWidget(group_box_7)
        page1_layout2.addWidget(group_box_8)

        page2_layout1.addWidget(group_box_9)
        page2_layout2.addWidget(group_box_10)
        page2_layout2.addWidget(group_box_12)
        page2_layout2.addWidget(group_box_13)
        page2_layout2.addWidget(group_box_11)

        admin_layout1.addWidget(group_box_14)
        admin_layout2.addWidget(group_box_15)
        admin_layout2.addWidget(group_box_16)
        admin_layout2.addWidget(group_box_17)
        admin_layout2.addWidget(group_box_18)

        man_layout1.addWidget(group_box_19)
        man_layout1.addWidget(group_box_20)
        man_layout2.addWidget(group_box_21)
        man_layout2.addWidget(group_box_22)

        addfields_layout1.addWidget(group_box_23)

        verticalSpacer1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        page1_layout1.addItem(verticalSpacer1)
        page1_layout2.addItem(verticalSpacer1)
        page2_layout1.addItem(verticalSpacer1)
        page2_layout2.addItem(verticalSpacer1)
        admin_layout1.addItem(verticalSpacer1)
        admin_layout2.addItem(verticalSpacer1)
        man_layout1.addItem(verticalSpacer1)
        man_layout2.addItem(verticalSpacer1)
        addfields_layout1.addItem(verticalSpacer1)

        # Event on change from combo parent
        self._get_event_combo_parent(json_result['body']['form']['formTabs'])

        # Set signals Combo parent/child
        chk_expl = self.dlg_config.tab_main.findChild(QWidget, 'chk_exploitation_vdefault')
        chk_dma = self.dlg_config.tab_main.findChild(QWidget, 'chk_dma_vdefault')
        if chk_dma and chk_expl:
            chk_dma.stateChanged.connect(partial(self._check_child_to_parent, chk_dma, chk_expl))
            chk_expl.stateChanged.connect(partial(self._check_parent_to_child, chk_expl, chk_dma))
        tools_qt.hide_void_groupbox(self.dlg_config)

        # Set shortcut keys
        self.dlg_config.key_escape.connect(partial(tools_gw.close_dialog, self.dlg_config))

        # Check user/role and remove tabs
        role_admin = tools_db.check_role_user("role_admin", cur_user)
        if not role_admin and cur_user not in super_users:
            tools_qt.remove_tab(self.dlg_config.tab_main, "tab_admin")

        # Open form
        tools_gw.open_dialog(self.dlg_config, dlg_name='config')


    def _get_layers_name(self):
        """ Returns the name of all the layers visible in the TOC, then populate the cad_combo_layers """

        layers = self.iface.mapCanvas().layers()
        if not layers:
            return
        layers_name = '"list_layers_name":"{'
        tables_name = '"list_tables_name":"{'
        for layer in layers:
            layers_name += f"{layer.name()}, "
            tables_name += f"{tools_qgis.get_layer_source_table_name(layer)}, "
        result = layers_name[:-2] + '}", ' + tables_name[:-2] + '}"'

        return result


    def _get_event_combo_parent(self, row):

        for field in row[0]["fields"]:
            if field['isparent']:
                widget = self.dlg_config.findChild(QComboBox, field['widgetname'])
                if widget:
                    widget.currentIndexChanged.connect(partial(tools_gw.fill_child, self.dlg_config, widget, 'config'))


    def _update_values(self):

        my_json = json.dumps(self.list_update)
        extras = f'"fields":{my_json}'
        body = tools_gw.create_body(form='"formName":"config"', extras=extras)
        json_result = tools_gw.execute_procedure('gw_fct_setconfig', body)
        if not json_result or json_result['status'] == 'Failed':
            return False

        message = "Values has been updated"
        tools_qgis.show_info(message)
        # Close dialog
        tools_gw.close_dialog(self.dlg_config)


    # noinspection PyUnresolvedReferences
    def _build_dialog_options(self, row, pos):

        widget = None
        for field in row[pos]['fields']:
            if field['label']:
                lbl = QLabel()
                lbl.setObjectName('lbl' + field['widgetname'])
                lbl.setText(field['label'])
                lbl.setMinimumSize(160, 0)
                lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                lbl.setToolTip(field['tooltip'])

                chk = QCheckBox()
                chk.setObjectName('chk_' + field['widgetname'])
                if field['checked'] in ('true', 'True', 'TRUE', True):
                    chk.setChecked(True)
                elif field['checked'] in ('false', 'False', 'FALSE', False):
                    chk.setChecked(False)
                chk.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

                if field['widgettype'] == 'text' or field['widgettype'] == 'linetext':
                    widget = QLineEdit()
                    widget.setText(field['value'])
                    widget.editingFinished.connect(partial(self._get_dialog_changed_values, chk, widget, field))
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                elif field['widgettype'] == 'textarea':
                    widget = QTextEdit()
                    widget.setText(field['value'])
                    widget.editingFinished.connect(partial(self._get_dialog_changed_values, chk, widget, field))
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                elif field['widgettype'] == 'combo':
                    widget = QComboBox()
                    self._fill_combo(widget, field)
                    widget.currentIndexChanged.connect(partial(self._get_dialog_changed_values, chk, widget, field))
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                elif field['widgettype'] == 'check':
                    widget = chk
                    widget.stateChanged.connect(partial(self._get_dialog_changed_values, chk, chk, field))
                    widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                elif field['widgettype'] == 'datetime':
                    widget = QgsDateTimeEdit()
                    widget.setAllowNull(True)
                    widget.setCalendarPopup(True)
                    widget.setDisplayFormat('dd/MM/yyyy')

                    if field['value']:
                        field['value'] = field['value'].replace('/', '-')
                    date = QDate.fromString(field['value'], 'yyyy-MM-dd')
                    if date:
                        widget.setDate(date)
                    else:
                        widget.clear()
                    widget.dateChanged.connect(partial(self._get_dialog_changed_values, chk, widget, field))
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                elif field['widgettype'] == 'spinbox':
                    widget = QDoubleSpinBox()
                    if 'value' in field and field['value'] is not None:
                        value = float(str(field['value']))
                        widget.setValue(value)
                    widget.valueChanged.connect(partial(self._get_dialog_changed_values, chk, widget, field))
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                else:
                    pass

                widget.setObjectName(field['widgetname'])

                # Set signals
                chk.stateChanged.connect(partial(self._get_values_checked_param_user, chk, widget, field))

                if field['layoutname'] == 'lyt_basic':
                    self._order_widgets(field, self.basic_form, lbl, chk, widget)
                elif field['layoutname'] == 'lyt_om':
                    self._order_widgets(field, self.om_form, lbl, chk, widget)
                elif field['layoutname'] == 'lyt_inventory':
                    self._order_widgets(field, self.inventory_form, lbl, chk, widget)
                elif field['layoutname'] == 'lyt_mapzones':
                    self._order_widgets(field, self.mapzones_form, lbl, chk, widget)
                elif field['layoutname'] == 'lyt_edit':
                    self._order_widgets(field, self.cad_form, lbl, chk, widget)
                elif field['layoutname'] == 'lyt_epa':
                    self._order_widgets(field, self.epa_form, lbl, chk, widget)
                elif field['layoutname'] == 'lyt_masterplan':
                    self._order_widgets(field, self.masterplan_form, lbl, chk, widget)
                elif field['layoutname'] == 'lyt_other':
                    self._order_widgets(field, self.other_form, lbl, chk, widget)
                elif field['layoutname'] == 'lyt_node_vdef':
                    self._order_widgets(field, self.node_type_form, lbl, chk, widget)
                elif field['layoutname'] == 'lyt_arc_vdef':
                    self._order_widgets(field, self.cat_form, lbl, chk, widget)
                elif field['layoutname'] == 'lyt_utils_vdef':
                    self._order_widgets(field, self.utils_form, lbl, chk, widget)
                elif field['layoutname'] == 'lyt_connec_vdef':
                    self._order_widgets(field, self.connec_form, lbl, chk, widget)
                elif field['layoutname'] == 'lyt_gully_vdef':
                    self._order_widgets(field, self.gully_form, lbl, chk, widget)
                elif field['layoutname'] == 'lyt_fluid_type':
                    self._order_widgets(field, self.fluid_type_form, lbl, chk, widget)
                elif field['layoutname'] == 'lyt_location_type':
                    self._order_widgets(field, self.location_type_form, lbl, chk, widget)
                elif field['layoutname'] == 'lyt_category_type':
                    self._order_widgets(field, self.category_type_form, lbl, chk, widget)
                elif field['layoutname'] == 'lyt_function_type':
                    self._order_widgets(field, self.function_type_form, lbl, chk, widget)
                elif field['layoutname'] == 'lyt_addfields':
                    self._order_widgets(field, self.addfields_form, lbl, chk, widget)


    # noinspection PyUnresolvedReferences
    def _construct_form_param_system(self, row, pos):

        widget = None
        for field in row[pos]['fields']:
            if field['label']:
                lbl = QLabel()
                lbl.setObjectName('lbl' + field['widgetname'])
                lbl.setText(field['label'])
                lbl.setMinimumSize(160, 0)
                lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                lbl.setToolTip(field['tooltip'])

                if field['widgettype'] == 'text' or field['widgettype'] == 'linetext':
                    widget = QLineEdit()
                    widget.setText(field['value'])
                    widget.editingFinished.connect(partial(self._get_values_changed_param_system, widget))
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                elif field['widgettype'] == 'textarea':
                    widget = QTextEdit()
                    widget.setText(field['value'])
                    widget.editingFinished.connect(partial(self._get_values_changed_param_system, widget))
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                elif field['widgettype'] == 'combo':
                    widget = QComboBox()
                    self._fill_combo(widget, field)
                    widget.currentIndexChanged.connect(partial(self._get_values_changed_param_system, widget))
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                elif field['widgettype'] == 'checkbox' or field['widgettype'] == 'check':
                    widget = QCheckBox()
                    if field['value'] in ('true', 'True', 'TRUE', True):
                        widget.setChecked(True)
                    elif field['value'] in ('false', 'False', 'FALSE', False):
                        widget.setChecked(False)
                    widget.stateChanged.connect(partial(self._get_values_changed_param_system, widget))
                    widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                elif field['widgettype'] == 'datetime':
                    widget = QDateEdit()
                    widget.setCalendarPopup(True)
                    if field['value']:
                        field['value'] = field['value'].replace('/', '-')
                    date = QDate.fromString(field['value'], 'yyyy-MM-dd')
                    widget.setDate(date)
                    widget.dateChanged.connect(partial(self._get_values_changed_param_system, widget))
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                elif field['widgettype'] == 'spinbox':
                    widget = QSpinBox()
                    if 'value' in field and field['value'] is not None:
                        value = float(str(field['value']))
                        widget.setValue(value)
                    widget.valueChanged.connect(partial(self._get_values_changed_param_system, widget))
                    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                else:
                    pass

                if widget:
                    widget.setObjectName(field['widgetname'])
                else:
                    pass

                # Order Widgets
                if 'layoutname' in field:
                    if field['layoutname'] == 'lyt_topology':
                        self._order_widgets_system(field, self.topology_form, lbl, widget)
                    elif field['layoutname'] == 'lyt_builder':
                        self._order_widgets_system(field, self.builder_form, lbl, widget)
                    elif field['layoutname'] == 'lyt_review':
                        self._order_widgets_system(field, self.review_form, lbl, widget)
                    elif field['layoutname'] == 'lyt_analysis':
                        self._order_widgets_system(field, self.analysis_form, lbl, widget)
                    elif field['layoutname'] == 'lyt_system':
                        self._order_widgets_system(field, self.system_form, lbl, widget)


    def _check_child_to_parent(self, widget_child, widget_parent):

        if widget_child.isChecked():
            widget_parent.setChecked(True)


    def _check_parent_to_child(self, widget_parent, widget_child):

        if not widget_parent.isChecked():
            widget_child.setChecked(False)


    def _fill_combo(self, widget, field):

        # Generate list of items to add into combo
        widget.blockSignals(True)
        widget.clear()
        widget.blockSignals(False)
        combolist = []
        if 'comboIds' in field:
            for i in range(0, len(field['comboIds'])):
                if field['comboIds'][i] is not None and field['comboNames'][i] is not None:
                    elem = [field['comboIds'][i], field['comboNames'][i]]
                    combolist.append(elem)

            records_sorted = sorted(combolist, key=operator.itemgetter(1))
            # Populate combo
            for record in records_sorted:
                widget.addItem(record[1], record)
        if 'value' in field:
            if str(field['value']) != 'None':
                tools_qt.set_combo_value(widget, field['value'], 0)


    def _get_dialog_changed_values(self, chk, widget, field, value=None):

        elem = {}
        if type(widget) is QLineEdit:
            value = tools_qt.get_text(self.dlg_config, widget, return_string_null=False)
        elif type(widget) is QComboBox:
            value = tools_qt.get_combo_value(self.dlg_config, widget, 0)
        elif type(widget) is QCheckBox:
            value = tools_qt.is_checked(self.dlg_config, chk)
        elif type(widget) is QDateEdit:
            value = tools_qt.get_calendar_date(self.dlg_config, widget)
        elif type(widget) is QgsDateTimeEdit:
            value = tools_qt.get_calendar_date(self.dlg_config, widget)
        if chk.isChecked():
            elem['widget'] = str(widget.objectName())
            elem['chk'] = str(chk.objectName())
            elem['isChecked'] = str(tools_qt.is_checked(self.dlg_config, chk))
            elem['value'] = value

            self.list_update.append(elem)


    def _get_values_checked_param_user(self, chk, widget, field, value=None):

        elem = {}

        elem['widget'] = str(widget.objectName())
        elem['chk'] = str(chk.objectName())

        if type(widget) is QLineEdit:
            value = tools_qt.get_text(self.dlg_config, widget, return_string_null=False)
            elem['widget_type'] = 'text'
        elif type(widget) is QComboBox:
            value = tools_qt.get_combo_value(self.dlg_config, widget, 0)
            elem['widget_type'] = 'combo'
        elif type(widget) is QCheckBox:
            value = tools_qt.is_checked(self.dlg_config, chk)
            elem['widget_type'] = 'check'
        elif type(widget) is QDateEdit:
            value = tools_qt.get_calendar_date(self.dlg_config, widget)
            elem['widget_type'] = 'datetime'
        elif type(widget) is QgsDateTimeEdit:
            value = tools_qt.get_calendar_date(self.dlg_config, widget)
            elem['widget_type'] = 'datetime'

        elem['isChecked'] = str(tools_qt.is_checked(self.dlg_config, chk))
        elem['value'] = value

        self.list_update.append(elem)


    def _get_values_changed_param_system(self, widget, value=None):

        elem = {}

        if type(widget) is QLineEdit:
            value = tools_qt.get_text(self.dlg_config, widget, return_string_null=False)
        elif type(widget) is QComboBox:
            value = tools_qt.get_combo_value(self.dlg_config, widget, 0)
        elif type(widget) is QCheckBox:
            value = tools_qt.is_checked(self.dlg_config, widget)
        elif type(widget) is QDateEdit:
            value = tools_qt.get_calendar_date(self.dlg_config, widget)

        elem['widget'] = str(widget.objectName())
        elem['chk'] = str('')
        elem['isChecked'] = str('')
        elem['value'] = value
        elem['sysRoleId'] = 'role_admin'

        self.list_update.append(elem)


    def _order_widgets(self, field, form, lbl, chk, widget):

        form.addWidget(lbl, field['layoutorder'], 0)
        if field['widgettype'] != 'check':
            form.addWidget(chk, field['layoutorder'], 1)
            form.addWidget(widget, field['layoutorder'], 2)
        else:
            form.addWidget(chk, field['layoutorder'], 1)


    def _order_widgets_system(self, field, form, lbl, widget):

        form.addWidget(lbl, field['layoutorder'], 0)
        if field['widgettype'] == 'checkbox' or field['widgettype'] == 'check':
            form.addWidget(widget, field['layoutorder'], 2)
        elif field['widgettype'] != 'checkbox' and field['widgettype'] != 'check':
            form.addWidget(widget, field['layoutorder'], 3)
        else:
            form.addWidget(widget, field['layoutorder'], 1)

    # endregion