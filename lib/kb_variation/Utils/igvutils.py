
import os
import subprocess
import uuid


from pprint import pprint,pformat

class igvutils:

    def __init__(self):
       self.output_dir = "/kb/module/work/tmp/report_dir/data/"
       pass 

    
    def run_command(self, command):

        cmdProcess = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        for line in cmdProcess.stdout:
            print(line.decode("utf-8").rstrip())
            cmdProcess.wait()
            print('return code: ' + str(cmdProcess.returncode))
            if cmdProcess.returncode != 0:
                raise ValueError('Error running ' + command + " " +
                                 str(cmdProcess.returncode) + '\n')

    
    def prepare_data_igv (self, genome_fa_path, vcf_path):



        #TODO: Fix all hard codes
        vcf_name = os.path.basename(vcf_path)
        vcf_gz_name = vcf_name + ".gz"
        cmd1 = "bgzip " +  vcf_path + " -c > "  +  self.output_dir + vcf_gz_name  
        self.run_command(cmd1)

        vcf_gz_path = self.output_dir + vcf_gz_name
        cmd2 = "tabix -p vcf " + vcf_gz_path
        self.run_command (cmd2)

        cmd3 = "cp " + genome_fa_path + " " + self.output_dir
        self.run_command(cmd3)

        genome_name = os.path.basename(genome_fa_path)
        new_genome_path = self.output_dir + genome_name

        cmd4 = "samtools faidx " + new_genome_path
        self.run_command(cmd4)

        filenames = dict()
        filenames['assembly_name'] = genome_name
        filenames['vcf_gz'] = vcf_gz_name
        filenames['vcf_gz_index'] = vcf_gz_name + "tbi"

        return filenames


