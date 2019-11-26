

import argparse
import datetime
import pprint

# [START storage_upload_file]
from google.cloud import storage
from google.cloud.storage import Blob


def download_blob(project, bucket_name, source_blob_name, destination_file_name):
    
    """Downloads a blob from the bucket."""
    storage_client = storage.Client(project)
    
    bucket = storage_client.get_bucket(bucket_name)
    
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print('Blob {} downloaded to {}.'.format(
        source_blob_name,
        
        destination_file_name))


download_blob('pythonclient-220207', 'projectbuckete', 'Testfile1.zip', 'Testfile1.zip')

download_blob('pythonclient-220207', 'projectbuckete', 'TestFile2.zip', 'TestFile2.zip')
