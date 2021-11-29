"""
This file is part of Giswater 3
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import Qt, pyqtSignal

import os

from .task import GwTask
from ..utils import tools_gw
from ...lib import tools_qt, tools_log


class GwCreateSchemaTask(GwTask):

    task_finished = pyqtSignal(list)

    def __init__(self, admin, description, params):

        super().__init__(description)
        self.admin = admin
        self.params = params
        self.dict_folders_process = {}

        # Manage buttons & other dlg-related widgets
        # Disable dlg_readsql_create_project buttons
        self.admin.dlg_readsql_create_project.btn_cancel_task.show()
        self.admin.dlg_readsql_create_project.btn_accept.hide()
        self.admin.dlg_readsql_create_project.btn_close.setEnabled(False)
        try:
            self.admin.dlg_readsql_create_project.key_escape.disconnect()
        except TypeError:
            pass

        # Disable red 'X' from dlg_readsql_create_project
        self.admin.dlg_readsql_create_project.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.admin.dlg_readsql_create_project.show()
        # Disable dlg_readsql buttons
        self.admin.dlg_readsql.btn_close.setEnabled(False)


    def run(self):

        super().run()
        self.is_test = self.params['is_test']
        self.finish_execution = {'import_data': False}
        self.dict_folders_process = {}
        self.admin.total_sql_files = 0
        self.admin.current_sql_file = 0
        self.admin.progress_value = 0

        status = self.main_execution()
        if not status:
            tools_log.log_info("Function main_execution returned False")
            return False

        self.custom_execution()
        return True


    def finished(self, result):

        super().finished(result)
        # Enable dlg_readsql_create_project buttons
        self.admin.dlg_readsql_create_project.btn_cancel_task.hide()
        self.admin.dlg_readsql_create_project.btn_accept.show()
        self.admin.dlg_readsql_create_project.btn_close.setEnabled(True)
        # Enable red 'X' from dlg_readsql_create_project
        self.admin.dlg_readsql_create_project.setWindowFlag(Qt.WindowCloseButtonHint, True)
        self.admin.dlg_readsql_create_project.show()
        # Disable dlg_readsql buttons
        self.admin.dlg_readsql.btn_close.setEnabled(True)

        if self.isCanceled():
            self.setProgress(100)
            return

        # Handle exception
        if self.exception is not None:
            msg = f"<b>Key: </b>{self.exception}<br>"
            msg += f"<b>key container: </b>'body/data/ <br>"
            msg += f"<b>Python file: </b>{__name__} <br>"
            msg += f"<b>Python function:</b> {self.__class__.__name__} <br>"
            tools_qt.show_exception_message("Key on returned json from ddbb is missed.", msg)

        if self.finish_execution['import_data']:
            tools_gw.set_config_parser('btn_admin', 'create_schema_type', 'rdb_import_data', prefix=False)
            msg = ("The base schema have been correctly executed."
                   "\nNow will start the import process. It is experimental and it may crash."
                   "\nIf this happens, please notify it by send a e-mail to info@giswater.org.")
            tools_qt.show_info_box(msg, "Info")
            self.admin.execute_import_inp_data(self.params['project_name_schema'], self.params['project_type'])
        else:
            self.admin.manage_process_result(self.params['project_name_schema'], self.params['project_type'],
                                             is_test=self.is_test)
        self.setProgress(100)


    def set_progress(self, value):

        if not self.is_test:
            self.setProgress(value)


    def main_execution(self):
        """ Main common execution """

        self.set_progress(0)

        project_type = self.params['project_type']
        exec_last_process = self.params['exec_last_process']
        project_name_schema = self.params['project_name_schema']
        project_locale = self.params['project_locale']
        project_srid = self.params['project_srid']

        self.admin.total_sql_files = self.calculate_number_of_files()
        tools_log.log_info(f"Number of SQL files 'TOTAL': {self.admin.total_sql_files}")

        status = self.admin.load_base(self.dict_folders_process['load_base'])
        if not status and self.admin.dev_commit is False:
            return False

        status = self.admin.load_locale()
        if not status and self.admin.dev_commit is False:
            return False

        status = self.admin.update_30to31(True, project_type)
        if not status and self.admin.dev_commit is False:
            return False

        status = self.admin.load_views()
        if not status and self.admin.dev_commit is False:
            return False

        status = self.admin.load_trg()
        if not status and self.admin.dev_commit is False:
            return False

        status = self.admin.update_31to39(True, project_type)
        if not status and self.admin.dev_commit is False:
            return False

        status = True
        if exec_last_process:
            status = self.admin.execute_last_process(True, project_name_schema, self.admin.schema_type,
                                                     project_locale, project_srid)

        if not status and self.admin.dev_commit is False:
            return False

        return True


    def custom_execution(self):
        """ Custom execution """

        project_type = self.params['project_type']
        example_data = self.params['example_data']

        if self.admin.rdb_import_data.isChecked():
            self.finish_execution['import_data'] = True
            # TODO:
            self.set_progress(90)
            return True
        elif self.admin.rdb_sample.isChecked() and example_data:
            self.set_progress(80)
            tools_gw.set_config_parser('btn_admin', 'create_schema_type', 'rdb_sample', prefix=False)
            self.admin.load_sample_data(project_type=project_type)
        elif self.admin.rdb_sample_dev.isChecked():
            self.set_progress(80)
            tools_gw.set_config_parser('btn_admin', 'create_schema_type', 'rdb_sample_dev', prefix=False)
            self.admin.load_sample_data(project_type=project_type)
            self.set_progress(90)
            self.admin.load_dev_data(project_type=project_type)
        elif self.admin.rdb_data.isChecked():
            tools_gw.set_config_parser('btn_admin', 'create_schema_type', 'rdb_data', prefix=False)


    def calculate_number_of_files(self):
        """ Calculate total number of SQL to execute """

        total_sql_files = 0
        dict_process = {}
        list_process = ['load_base', 'load_locale', 'update_30to31', 'load_views', 'load_trg', 'update_31to39']

        for process in list_process:
            dict_folders, total = self.get_number_of_files_process(process)
            total_sql_files += total
            tools_log.log_info(f"Number of SQL files '{process}': {total}")
            dict_process[process] = total
            self.dict_folders_process[process] = dict_folders

        return total_sql_files


    def get_number_of_files_process(self, process_name: str):
        """ Calculate number of files of all folders of selected @process_name """

        dict_folders = self.get_folders_process(process_name)
        if dict_folders is None:
            return dict_folders, 0

        number_of_files = 0
        for folder in dict_folders.keys():
            file_count = sum(len(files) for _, _, files in os.walk(folder))
            number_of_files += file_count
            dict_folders[folder] = file_count

        return dict_folders, number_of_files


    def get_folders_process(self, process_name):
        """ Get list of folders related with this @process_name """

        dict_folders = {}
        if process_name == 'load_base':
            dict_folders[os.path.join(self.admin.folder_utils, self.admin.file_pattern_ddl)] = 0
            dict_folders[os.path.join(self.admin.folder_utils, self.admin.file_pattern_dml)] = 0
            dict_folders[os.path.join(self.admin.folder_utils, self.admin.file_pattern_fct)] = 0
            dict_folders[os.path.join(self.admin.folder_utils, self.admin.file_pattern_ftrg)] = 0
            dict_folders[os.path.join(self.admin.folder_software, self.admin.file_pattern_ddl)] = 0
            dict_folders[os.path.join(self.admin.folder_software, self.admin.file_pattern_ddlrule)] = 0
            dict_folders[os.path.join(self.admin.folder_software, self.admin.file_pattern_dml)] = 0
            dict_folders[os.path.join(self.admin.folder_software, self.admin.file_pattern_tablect)] = 0
            dict_folders[os.path.join(self.admin.folder_software, self.admin.file_pattern_fct)] = 0
            dict_folders[os.path.join(self.admin.folder_software, self.admin.file_pattern_ftrg)] = 0
            dict_folders[os.path.join(self.admin.folder_utils, self.admin.file_pattern_tablect)] = 0
            dict_folders[os.path.join(self.admin.folder_utils, self.admin.file_pattern_ddlrule)] = 0

        elif process_name == 'load_locale':
            dict_folders[self.admin.folder_locale] = 0

        elif process_name == 'update_30to31':
            dict_folders[os.path.join(self.admin.folder_updates, '31', '31100')] = 0

        elif process_name == 'load_views':
            dict_folders[os.path.join(self.admin.folder_software, self.admin.file_pattern_ddlview)] = 0
            dict_folders[os.path.join(self.admin.folder_utils, self.admin.file_pattern_ddlview)] = 0

        elif process_name == 'load_trg':
            dict_folders[os.path.join(self.admin.folder_utils, self.admin.file_pattern_trg)] = 0
            dict_folders[os.path.join(self.admin.folder_software, self.admin.file_pattern_trg)] = 0

        elif process_name == 'update_31to39':
            dict_folders[os.path.join(self.admin.folder_updates, '31', '31103')] = 0
            dict_folders[os.path.join(self.admin.folder_updates, '31', '31105')] = 0
            dict_folders[os.path.join(self.admin.folder_updates, '31', '31109')] = 0
            dict_folders[os.path.join(self.admin.folder_updates, '31', '31110')] = 0
            dict_folders[os.path.join(self.admin.folder_updates, '32')] = 0
            dict_folders[os.path.join(self.admin.folder_updates, '33')] = 0
            dict_folders[os.path.join(self.admin.folder_updates, '34')] = 0
            dict_folders[os.path.join(self.admin.folder_updates, '35')] = 0

        return dict_folders

