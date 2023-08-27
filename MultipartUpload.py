import argparse
import os
import math
import hashlib
import botocore.utils
import boto3
import datetime 

def split_file(input_file, part_size):
    part_size_bytes = part_size * 1024 * 1024  # Convert MiB to bytes
    with open(input_file, 'rb') as f:
        while True:
            data = f.read(part_size_bytes)
            if not data:
                break
            yield data

def upload_to_glacier(vault_name, upload_id, part_data, start_byte, end_byte):
    glacier = boto3.client('glacier')
    response = glacier.upload_multipart_part(
        vaultName=vault_name,
        uploadId=upload_id,
        range=f'bytes {start_byte}-{end_byte - 1}/*',
        body=part_data
    )
    return response['checksum']
    
def save_to_csv(vault_name, archive_id, tree_hash, location, original_filename, upload_datetime):
    csv_filename = f"{vault_name}.csv"
    header = "Archive ID,Checksum,Location,Original Filename,Upload Date & Time\n"

    if not os.path.exists(csv_filename):
        with open(csv_filename, 'w') as csv_file:
            csv_file.write(header)

    with open(csv_filename, 'a') as csv_file:
        csv_file.write(f"{original_filename},{archive_id},{tree_hash},{location},{upload_datetime}\n")
 

def main():
    parser = argparse.ArgumentParser(description="Split a file into specified-size parts, calculate tree hash, and upload to AWS Glacier.")
    parser.add_argument("input_file", help="Input file to be split")
    parser.add_argument("part_size", type=int, help="Part size in MiB")
    parser.add_argument("vault_name", help="AWS Glacier vault name")
    args = parser.parse_args()

    input_file = args.input_file
    part_size = args.part_size
    vault_name = args.vault_name

    if not os.path.isfile(input_file):
        print("Error: Input file not found.")
        return

    if part_size <= 0:
        print("Error: Part size should be a positive value.")
        return

    total_parts = math.ceil(os.path.getsize(input_file) / (part_size * 1024 * 1024))
    print(f"Splitting {input_file} into {total_parts} parts.")

    part_size_bytes = part_size * 1024 * 1024  # Convert MiB to bytes
    glacier = boto3.client('glacier')
    upload_response = glacier.initiate_multipart_upload(
        vaultName=vault_name,
        archiveDescription=os.path.basename(input_file),  # Use filename as archiveDescription
        partSize=str(part_size_bytes)
    )
    upload_id = upload_response['uploadId']

    with open(input_file, 'rb') as f:
        tree_hash = botocore.utils.calculate_tree_hash(f)
    print(f"File Tree Hash: {tree_hash}")

    upload_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for idx, part_data in enumerate(split_file(input_file, part_size), start=1):
        start_byte = (idx - 1) * part_size_bytes
        end_byte = min(idx * part_size_bytes, os.path.getsize(input_file))

        part_checksum = upload_to_glacier(vault_name, upload_id, part_data, start_byte, end_byte)
        print(f"Uploaded Part {idx}/{total_parts} - Checksum: {part_checksum}")

    complete_response = glacier.complete_multipart_upload(
        vaultName=vault_name,
        uploadId=upload_id,
        archiveSize=str(os.path.getsize(input_file)),
        checksum=tree_hash
    )
    archive_id = complete_response['archiveId']
    location = complete_response['location']
    print(f"Multipart upload completed.")
    print(f"Archive ID: {archive_id}")
    print(f"Checksum: {tree_hash}")
    print(f"Location in S3 Glacier: {location}")

    save_to_csv(vault_name, archive_id, tree_hash, location, os.path.basename(input_file), upload_datetime)


if __name__ == "__main__":
    main()