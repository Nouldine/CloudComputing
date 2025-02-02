#!/usr/bin/env python

# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Example of using the Compute Engine API to create and delete instances.

Creates a new compute engine instance and uses it to apply a caption to
an image.

    https://cloud.google.com/compute/docs/tutorials/python-guide

For more information, see the README.md under /compute.
"""
import argparse
import os
import time

import googleapiclient.discovery
from six.moves import input


# [START list_instances]
def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else None
# [END list_instances]


# [START create_instance]
def create_instance(compute, project, zone, name, bucket):
    # Get the latest Debian Jessie image.
    image_response = compute.images().getFromFamily(
        project='debian-cloud', family='debian-9').execute()
    source_disk_image = image_response['selfLink']


    # Configure the machine
    machine_type = "zones/%s/machineTypes/n1-standard-1" % zone
    
    print(zone, name )

    startup_script = open(
        os.path.join(
            os.path.dirname(__file__), 'startup-script.sh'), 'r').read()
    image_url = "http://storage.googleapis.com/gce-demo-input/photo.jpg"
    image_caption = "Ready for dessert?"

    config = {

        'name': name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],

        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [{
                # Startup script is automatically executed by the
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script
            }, {
                'key': 'url',
                'value': image_url
            }, {
                'key': 'text',
                'value': image_caption
            }, {
                'key': 'bucket',
                'value': bucket
            }]
        }
    }

    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()
        
# [END create_instance]


# [START delete_instance]
def delete_instance(compute, project, zone, name):
    return compute.instances().delete(
        project=project,
        zone=zone,
        instance=name).execute()
# [END delete_instance]


# [START wait_for_operation]
def wait_for_operation(compute, project, zone, operation):
    print('Waiting for operation to finish...')
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)
# [END wait_for_operation]


# [START run]
def main(project, bucket, zone, zone2, instance_name, instance_name2, wait=True):
    
    compute = googleapiclient.discovery.build('compute', 'v1')

    print('Creating instance.')

    # Creating the first instance from the first zone
    operation1 = create_instance(compute, project, zone, instance_name,bucket)
    
    # Creating the second instance from the second zone
    operation2 = create_instance(compute, project, zone2, instance_name2, bucket)

    # waiting for the creation of the instance in the second zone
    wait_for_operation(compute, project, zone, operation1['name'])
    
    # Waiting  for the creation of the instance in the second zone
    wait_for_operation(compute, project, zone2, operation2['name'])

    # list of the instance created in the first zone
    instances = list_instances(compute, project, zone)

    # list of the instance created in the second zone
    instances2 = list_instances(compute, project, zone2)

    print('Instances in project %s and zone %s:' % (project, zone))
    for instance in instances:
        print(' - ' + instance['name'])

    print('Instances in project %s and zone %s:' % (project, zone2))
    for instance in instances2:
        print(' - ' + instance['name'])


    print("""
Instance created.
It will take a minute or two for the instance to complete work.
Check this URL: http://storage.googleapis.com/{}/output.png
Once the image is uploaded press enter to delete the instance.
""".format(bucket))

    if wait:
        input()

    print('Deleting instance.')

    # Deletion of the first instance
    operation1 = delete_instance(compute, project, zone, instance_name)
    
    # Deletion of the second instance
    operation2 = delete_instance( compute, project, zone2, instance_name2)

    # wait for the creation of the first operation 
    wait_for_operation(compute, project, zone, operation1['name'])

    # Wait for the creation of the second operation
    wait_for_operation( compute, project, zone2, operation2['name'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('project_id', help='Your Google Cloud project ID.')

    parser.add_argument(
        'bucket_name', help='Your Google Cloud Storage bucket name.')

    parser.add_argument(
        '--zone',
        default='us-central1-f',
        help='Compute Engine zone to deploy to.')

    parser.add_argument(
        '--zone2',
        default='asia-southeast1',
        help='Compute Engine zone to deploy to.')

    parser.add_argument(
        '--name', default='demo-instance', help='New instance name.')

    parser.add_argument(
        '--name2', default='demo-instance', help='New instance name.')

    args = parser.parse_args()

    main(args.project_id, args.bucket_name, args.zone, args.zone2, args.name, args.name2)

# [END run]
