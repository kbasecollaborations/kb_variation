# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import shutil

from installed_clients.KBaseReportClient import KBaseReport
from kb_variation.Utils.file_utils import file_utils
from kb_variation.Utils.SnippyUtils import SnippyUtils
from kb_variation.Utils.htmlreportutils import htmlreportutils
from kb_variation.Utils.igvutils import igvutils
from installed_clients.VariationUtilClient import VariationUtil


#END_HEADER


class kb_variation:
    '''
    Module Name:
    kb_variation

    Module Description:
    A KBase module: kb_variation
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = ""
    GIT_COMMIT_HASH = ""

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.config = config
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.ws_url = config["workspace-url"]
        self.scratch = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_kb_variation(self, ctx, params):
        """
        Method to run variation analysis using snippy
        :param params: instance of type "InputParams" -> structure: parameter
           "variation_object_name" of String, parameter "workspace_name" of
           String, parameter "fastq_ref" of String, parameter "map_qual" of
           Long, parameter "base_qual" of Long, parameter "min_cov" of Long,
           parameter "min_qual" of Long, parameter "genome_or_assembly_ref"
           of String, parameter "sample_attribute_ref" of String
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_kb_variation

        print (params)
        
        #Download reads as fastq and assembly as fasta
        futils = file_utils(self.callback_url, self.ws_url)
        
       
        reads = futils.fetch_reads_from_reference(params['fastq_ref'])
        assembly = futils.fetch_fasta_from_genome_or_assembly (params['genome_or_assembly_ref'])

        print (reads)
        print (assembly)
        
        #Get file names of reads and assembly
        name_map = futils.get_object_names([params['fastq_ref'], 
                                           params['genome_or_assembly_ref']
                                          ])

        genome_or_assembly_name = name_map[params['genome_or_assembly_ref']]
        reads_name = name_map[params['fastq_ref']]

        print (reads)
        print (assembly)
        print (name_map)

        
        #Run Snippy analysis
        snippy = SnippyUtils(self.scratch)
        snippy_vcf_file_path = snippy.run_snippy_command_paired_end(assembly, reads, reads_name, genome_or_assembly_name)

        

        #Save variation object in workspace using VariationUtil API

        vu = VariationUtil(self.callback_url)

        VariationUtilParams = {
            'workspace_name': params['workspace_name'],
            'genome_or_assembly_ref': params['genome_or_assembly_ref'],
            'vcf_staging_file_path': snippy_vcf_file_path,
            'sample_attribute_ref': params['sample_attribute_ref'],
            'variation_object_name': params['variation_object_name']
        }

        vu.save_variation_from_vcf(VariationUtilParams)

        

        #TODO: Remove hard coded stuff from here
        template_dir = "/kb/module/lib/kb_variation/Utils/report_template"
        #data_dir = "/kb/module/lib/kb_variation/Utils/report/data"

        report_dir = "/kb/module/work/tmp/report_dir"
        report_data_dir = report_dir + "/data"

        destination_report = shutil.copytree(template_dir, report_dir)
        #destination_report_data = shutil.copytree(data_dir, report_data_dir)

        

        assembly_file_path = assembly['path']
        ig = igvutils ()
        filenames = ig.prepare_data_igv(assembly_file_path, snippy_vcf_file_path)


        #Create html report
        name_dict = dict()
        name_dict['GENOME'] = "data/" + filenames['assembly_name']
        name_dict['GENOME_NAME'] =  filenames['assembly_name']
        name_dict['SNP_FILE'] = "data/" + filenames['vcf_gz']
        name_dict['SNP_INDEX_FILE'] = "data/" + filenames['vcf_gz_index']
        name_dict['SNP_NAME'] = reads_name   #TODO: Fix this for population

        hu = htmlreportutils(self.callback_url, params['workspace_name'])

        hu.create_html_report(report_dir, name_dict)

        
        report = KBaseReport(self.callback_url)
        report_info = report.create({'report': {'objects_created':[],
                                                'text_message': "xmx"},
                                                'workspace_name': params['workspace_name']})
        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref'],
        }
        #END run_kb_variation

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_kb_variation return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
