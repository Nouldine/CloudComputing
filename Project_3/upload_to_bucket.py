
import argparse
import datetime
import pprint

# [START storage_upload_file]
from google.cloud import storage
from google.cloud.storage import Blob

#[ upload  function ]
def upload_blob( project, bucket_name, source_file_name, destination_blob_name ):

    """Uploads a file to the bucket."""
    
    storage_client = storage.Client(project)
    
    bucket = storage_client.get_bucket(bucket_name)
    
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name ))

upload_blob('pythonclient-220207', 'projectbuckete', 'Testfile1.zip', 'Testfile1.zip')

upload_blob('pythonclient-220207', 'projectbuckete', 'TestFile2.zip', 'TestFile2.zip')

