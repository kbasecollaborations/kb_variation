import uuid
import os
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.WorkspaceClient import Workspace
import shutil 

class htmlreportutils:
    def __init__(self, callback_url, workspace_name):
        self.callback_url = callback_url
        self.workspace_name = workspace_name
        pass


    def generate_html_from_template(self, name_dict):

        with open("/kb/module/work/tmp/report_dir/index.html", 'w') as result_file:

            with open(os.path.join('/kb/module/lib/kb_variation/Utils', 'report_template',
                                   'report_template.html'),
                      'r') as report_template_file:
                report_template = report_template_file.read()
                report_template = report_template.replace('##GENOME##',
                                                         "'" + name_dict['GENOME'] + "'")
                report_template = report_template.replace('##GENOME_NAME##',
                                                       "'" +  name_dict['GENOME_NAME']+ "'")
                report_template = report_template.replace('##SNP_FILE##',
                                                      "'" +  name_dict['SNP_FILE']+ "'")
                report_template = report_template.replace('##SNP_INDEX_FILE##',
                                                     "'" +  name_dict['SNP_INDEX_FILE']+ "'")
                report_template = report_template.replace('##SNP_NAME##',
                                                     "'" +  name_dict['SNP_NAME']+ "'")
                result_file.write(report_template)
        result_file.close()


    def create_html_report(self, report_dir, name_dict):
        '''
         function for creating html report
        '''

        result_file = report_dir + "/index.html"
        self.generate_html_from_template(name_dict)


        dfu = DataFileUtil(self.callback_url)
        report_name = 'kb_variation_report_' + str(uuid.uuid4())
        report = KBaseReport(self.callback_url)
        

        report_shock_id = dfu.file_to_shock({'file_path': report_dir,
                                            'pack': 'zip'})['shock_id']

        html_file = {
            'shock_id': report_shock_id,
            'name': 'index.html',
            'label': 'index.html',
            'description': 'IGV Variation viewer'
            }
        
        report_info = report.create_extended_report({
                        'direct_html_link_index': 0,
                        'html_links': [html_file],
                        'report_object_name': report_name,
                        'workspace_name': self.workspace_name
                    })
        return {
            'report_name': report_info['name'],
            'report_ref': report_info['ref']
        }

