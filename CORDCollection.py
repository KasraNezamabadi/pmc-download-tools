"""
Fetch PDFs from PMC database for CORD19 dataset.
CORD19 dataset (final release, June 2, 2022):
https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases/cord-19_2022-06-02.tar.gz
Above package contains a metadata CSV file showing PMCID of the publications.
These IDs are cross-ref with PMCIDs on `ftp.ncbi.nih.gov` whose PDFs are available to download.
The final extracted PDFs are stored in `Data/ExtractedPDFs`
The metadata of the COVID publications whose PDFs are stored in above directory is stored at Data/cord19_with_pdfs.xlsx
"""

import io
import os
from ftplib import FTP

import pandas as pd
from tqdm import tqdm


if __name__ == "__main__":
    # Part 1: Download `oa_non_comm_use_pdf.csv` from `ftp.ncbi.nih.gov/pub/pmc`
    print('Fetching "oa_non_comm_use_pdf.csv" from ncbi FTP server ...')
    ftp = FTP('ftp.ncbi.nih.gov')
    ftp.login()
    ftp.cwd('pub/pmc')
    a = ftp.nlst()
    oa_file_list = io.BytesIO()
    ftp.retrbinary('RETR oa_non_comm_use_pdf.csv', oa_file_list.write)
    oa_file_list.seek(0)
    pmc_lookup_df = pd.read_csv(oa_file_list)
    ftp.close()

    # Part 2: Read `metadata.csv` from cord19 dataset.
    print('Loading entire CORD19 latest metadata into memory ...')
    meta = pd.read_csv('Data/metadata.csv')
    # Some data cleaning.
    meta['publish_time'] = pd.to_datetime(meta['publish_time'])
    meta.sort_values(by='publish_time', inplace=True, ascending=False)

    # Cross-ref with PMC database whose PDFs are available to download.
    pmcids_with_pdfs = set(pmc_lookup_df['Accession ID'])
    available_pmc_ids = []
    for pmc_id in meta['pmcid'].values:
        if pmc_id in pmcids_with_pdfs:
            available_pmc_ids.append(pmc_id)
    print(f'{len(available_pmc_ids)} articles have PDFs in PMC')

    available_meta = meta.loc[meta['pmcid'].isin(set(available_pmc_ids))]
    print('Storing metadata for articles whose PDFs are available in PMC database ...')
    available_meta.to_excel('Data/cord19_with_pdfs.xlsx', index=False)

    # Fetch cache from previous process. In case of failure, resume from last checkpoint.
    pmc_ids_processed = set([x.split('.')[0] for x in os.listdir('Data/ExtractedPDFs') if x.startswith('PMC')])

    for count, pmc_id in enumerate(pbar := tqdm(available_pmc_ids)):
        # After ~140 requests, the NIH server closes the FTP. Here, we manually reset connection to maintain persistent
        # FTP pipeline.
        if count % 100 == 0:
            ftp.close()
            ftp = FTP('ftp.ncbi.nih.gov')
            ftp.login()
            ftp.cwd('pub/pmc')
        if pmc_id not in pmc_ids_processed:
            pbar.set_description(f'Fetch PDF for PMCID={pmc_id}')
            article_path = pmc_lookup_df.loc[pmc_lookup_df['Accession ID'] == pmc_id]['File'].values[0]
            article = io.BytesIO()
            ftp.retrbinary(f'RETR {article_path}', article.write)
            article.seek(0)
            with open(f'Data/ExtractedPDFs/{pmc_id}.pdf', 'wb') as f:
                f.write(article.getvalue())
    ftp.close()
