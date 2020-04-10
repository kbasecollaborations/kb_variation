/*
A KBase module: kb_variation
*/

module kb_variation {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    typedef structure{
        string variation_object_name;
        string workspace_name; 
        string fastq_ref;
        int map_qual;
        int base_qual;
        int min_cov;
        int min_qual;     
        string genome_or_assembly_ref;  
        string sample_attribute_ref; 
    } InputParams;


    /* Method to run variation analysis using snippy */
    funcdef run_kb_variation (InputParams params) returns (ReportResults output) authentication required;


};
