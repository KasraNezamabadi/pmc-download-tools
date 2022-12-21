# pmc-download-tools
Fetch PDFs from PMC database for CORD19 dataset final release, June 2, 2022 (https://github.com/allenai/cord19).

## How to run
Download and extract `metadata.csv` from the link below and store it at `Data/metadata.csv`:  
https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases/cord-19_2022-06-02.tar.gz.  
The metadata contains PMCID of the COVID-related publications. These IDs are cross-ref with PMCIDs on `ftp.ncbi.nih.gov/pub/pmc/oa_non_comm_use_pdf.csv` whose PDFs are available to download.
## Output
* Downloaded articles in PDF are stored in `Data/ExtractedPDFs`
* Metadata of the downloaded articles is stored at `Data/cord19_with_pdfs.xlsx`
