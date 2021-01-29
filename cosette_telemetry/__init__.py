import os
from otter.plugins import AbstractOtterPlugin
import gspread
import copy
import re
import json
import pandas as pd

class CosetteTelemetryPlugin(AbstractOtterPlugin):

    IMPORTABLE_NAME = "cosette_telemetry.CosetteTelemetryPlugin"

    def _load_df(self):
        """
        Uses the Google Sheets API credentials stored in ``self.plugin_config`` to read in the
        sheet using ``pandas``.
        Returns:
            ``pandas.core.frame.DataFrame``: the sheet as a dataframe
        """
        oauth_json = self.plugin_config["service_account_credentials"]
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".json") as ntf:
            json.dump(oauth_json, ntf)
            ntf.seek(0)

            gc = gspread.service_account(filename=ntf.name)
        
        sheet_url = self.plugin_config["sheet_url"]
        sheet = gc.open_by_url(sheet_url)
        self.worksheet = sheet.get_worksheet(0)
        data = worksheet.get_all_values()
        colnames = data.pop(0)

        self._df = pd.DataFrame(data, columns=colnames)

    def after_execution(self, global_env):
        variable_names = self.plugin_config["query_var_names"] # list of variable names provided by instructor to grab from global_env
        self.data = {test: global_env[name] for test, name in variable_names.items()} # maps test name to query string via variable name (provided by yaml)
    
    def after_grading(self, results):
        results = copy.deepcopy(results)
        for key in results.results:
            for test in self.data:
                if not re.search(rf"""\b{test}\b""", key):
                    results.results.pop(key)
        results = results.to_gradescope_dict({})
        output = {'queries': self.data, 'results': results}
        output = json.dumps(output)


        self._load_df()

        self._df.append({'data': output}, ignore_index = True)

        self.worksheet.update([self._df.columns.values.tolist()] + self._df.values.tolist())

    def during_generate(self, otter_config, assignment):
        """
        Takes a path to Google Service Account credentials stored in this plugin's config as key
        ``credentials_json_path`` and extracts the data from that file into the plugin's config as key
        ``service_account_credentials``.
        Args:
            otter_config (``dict``): the parsed Otter configuration JSON file
            assignment (``otter.assign.assignment.Assignment``): the assignment configurations if 
                Otter Assign is used
        """
        if assignment is not None:
            curr_dir = os.getcwd()
            os.chdir(assignment.master.parent)
        
        cfg_idx = [self.IMPORTABLE_NAME in c.keys() for c in otter_config["plugins"] if isinstance(c, dict)].index(True)
        creds_path = otter_config["plugins"][cfg_idx][self.IMPORTABLE_NAME]["credentials_json_path"]
        with open(creds_path) as f:
            creds = json.load(f)
        otter_config["plugins"][cfg_idx][self.IMPORTABLE_NAME]["service_account_credentials"] = creds
        
        if assignment is not None:
            os.chdir(curr_dir)
