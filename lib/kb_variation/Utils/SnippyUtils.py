import os
import subprocess
import uuid


from pprint import pprint,pformat

class SnippyUtils:

    def __init__(self, scratch):
       self.scratch = scratch
       self.SNIPPY = '/kb/module/deps/snippy/bin/snippy'
       pass 


    def run_command(self, command):

        cmdProcess = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        for line in cmdProcess.stdout:
            print(line.decode("utf-8").rstrip())
            cmdProcess.wait()
            print('return code: ' + str(cmdProcess.returncode))
            if cmdProcess.returncode != 0:
                raise ValueError('Error running bwa index, return code: ' + command + 
                                 str(cmdProcess.returncode) + '\n')


    def run_snippy_command_paired_end (self, assembly, reads, reads_name, genome_or_assembly_name):
    	
        outpath = os.path.join (self.scratch + "/" + str(uuid.uuid4()) + "/" + reads_name )
        assembly_file_path = assembly['path']
        file_fwd = reads['file_fwd']
        file_rev = reads['file_rev']

        command = self.SNIPPY + "  --outdir " + outpath + " --ref  "+ assembly_file_path + "  --R1  " + file_fwd  + " --R2  " + file_rev 

        print(command)
        print (outpath)

        self.run_command (command)

        return(outpath + "/snps.vcf")
        


