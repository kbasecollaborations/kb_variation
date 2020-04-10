"""
Some utility functions for the HISAT2 module.
These mainly deal with manipulating files from Workspace objects.
There's also some parameter checking and munging functions.
"""
from __future__ import print_function

import re
from pprint import pprint

from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.WorkspaceClient import Workspace
from installed_clients.ReadsUtilsClient import ReadsUtils
from installed_clients.AssemblyUtilClient import AssemblyUtil


class file_utils:

    def __init__(self, callback_url, ws_url):
        self.callback_url = callback_url
        self.ws_url = ws_url
       
    def valid_string(s, is_ref=False):
        is_valid = isinstance(s, basestring) and len(s.strip()) > 0
        if is_valid and is_ref:
            is_valid = check_reference(s)
        return is_valid


    def check_reference(ref):
        """
        Tests the given ref string to make sure it conforms to the expected
        object reference format. Returns True if it passes, False otherwise.
        """
        obj_ref_regex = re.compile("^(?P<wsid>\d+)\/(?P<objid>\d+)(\/(?P<ver>\d+))?$")
        ref_path = ref.strip().split(";")
        for step in ref_path:
            if not obj_ref_regex.match(step):
                return False
        return True


    def check_ref_type(self, ref, allowed_types):
        """
        Validates the object type of ref against the list of allowed types. If it passes, this
        returns True, otherwise False.
        Really, all this does is verify that at least one of the strings in allowed_types is
        a substring of the ref object type name.
        Ex1:
        ref = 11/22/33, which is a "KBaseGenomes.Genome-4.0"
        allowed_types = ["assembly", "KBaseFile.Assembly"]
        returns False
        Ex2:
        ref = 44/55/66, which is a "KBaseGenomes.Genome-4.0"
        allowed_types = ["assembly", "genome"]
        returns True
        """
        obj_type = self.get_object_type(ref).lower()
        for t in allowed_types:
            if t.lower() in obj_type:
                return True
        return False


    def get_object_type(self, ref):
        """
        Fetches and returns the typed object name of ref from the given workspace url.
        If that object doesn't exist, or there's another Workspace error, this raises a
        RuntimeError exception.
        """
        ws = Workspace(self.ws_url)
        info = ws.get_object_info3({"objects": [{"ref": ref}]})
        obj_info = info.get("infos", [[]])[0]
        if len(obj_info) == 0:
            raise RuntimeError("An error occurred while fetching type info from the Workspace. "
                               "No information returned for reference {}".format(ref))
        return obj_info[2]


    def get_object_names(self, ref_list):
        """
        From a list of workspace references, returns a mapping from ref -> name of the object.
        """
        ws = Workspace(self.ws_url)
        obj_ids = list()
        for ref in ref_list:
            obj_ids.append({"ref": ref})
        info = ws.get_object_info3({"objects": obj_ids})
        name_map = dict()
        # might be in a data palette, so we can't just use the ref.
        # we already have the refs as passed previously, so use those for mapping, as they're in
        # the same order as what's returned.
        for i in range(len(info["infos"])):
            name_map[ref_list[i]] = info["infos"][i][1]
        return name_map



    def fetch_reads_from_reference(self, ref):
        """
        Fetch a FASTQ file (or 2 for paired-end) from a reads reference.
        Returns the following structure:
        {
            "style": "paired", "single", or "interleaved",
            "file_fwd": path_to_file,
            "file_rev": path_to_file, only if paired end,
            "object_ref": reads reference for downstream convenience.
        }
        """
        try:
            print("Fetching reads from object {}".format(ref))
            reads_client = ReadsUtils(self.callback_url)
            reads_dl = reads_client.download_reads({
                "read_libraries": [ref],
                "interleaved": "false"
            })
            pprint(reads_dl)
            reads_files = reads_dl['files'][ref]['files']
            ret_reads = {
                "object_ref": ref,
                "style": reads_files["type"],
                "file_fwd": reads_files["fwd"]
            }
            if reads_files.get("rev", None) is not None:
                ret_reads["file_rev"] = reads_files["rev"]
            return ret_reads
        except:
            print("Unable to fetch a file from expected reads object {}".format(ref))
            raise

    def fetch_fasta_from_genome(self, genome_refl):

        """
        Returns an assembly or contigset as FASTA.
        """

        if not self.check_ref_type(genome_ref, ['KBaseGenomes.Genome']):
            raise ValueError("The given genome_ref {} is not a KBaseGenomes.Genome type!")
        # test if genome references an assembly type
        # do get_objects2 without data. get list of refs
        ws = Workspace(self.ws_url)
        genome_obj_info = ws.get_objects2({
            'objects': [{'ref': genome_ref}],
            'no_data': 1
        })
        # get the list of genome refs from the returned info.
        # if there are no refs (or something funky with the return), this will be an empty list.
        # this WILL fail if data is an empty list. But it shouldn't be, and we know because
        # we have a real genome reference, or get_objects2 would fail.
        genome_obj_refs = genome_obj_info.get('data', [{}])[0].get('refs', [])

        # see which of those are of an appropriate type (ContigSet or Assembly), if any.
        assembly_ref = list()
        ref_params = [{'ref': genome_ref + ";" + x} for x in genome_obj_refs]
        ref_info = ws.get_object_info3({'objects': ref_params})
        for idx, info in enumerate(ref_info.get('infos')):
            if "KBaseGenomeAnnotations.Assembly" in info[2] or "KBaseGenomes.ContigSet" in info[2]:
                assembly_ref.append(";".join(ref_info.get('paths')[idx]))

        if len(assembly_ref) == 1:
            return fetch_fasta_from_assembly(assembly_ref[0], self.ws_url, self.callback_url)
        else:
            raise ValueError("Multiple assemblies found associated with the given genome ref {}! "
                             "Unable to continue.")


    def fetch_fasta_from_assembly(self, assembly_ref):
        """
        From an assembly or contigset, this uses a data file util to build a FASTA file and return the
        path to it.
        """
        allowed_types = ['KBaseFile.Assembly',
                         'KBaseGenomeAnnotations.Assembly',
                         'KBaseGenomes.ContigSet']
        if not self.check_ref_type(assembly_ref, allowed_types):
            raise ValueError("The reference {} cannot be used to fetch a FASTA file".format(
                assembly_ref))
        au = AssemblyUtil(self.callback_url)
        return au.get_assembly_as_fasta({'ref': assembly_ref})


    def fetch_fasta_from_genome_or_assembly (self, genome_or_assembly_ref):
        """
        Fetches fasta from an assembly or genome
        """
        if  self.check_ref_type(genome_or_assembly_ref, ['KBaseGenomes.Genome']):
            return (self.fetch_fasta_from_genome(genome_or_assembly_ref))
        else:
            return (self.fetch_fasta_from_assembly(genome_or_assembly_ref))



       


