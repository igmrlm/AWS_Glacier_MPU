# AWS Glacier Automatic Multipart Uploader

This Python program simplifies the process of splitting large files, calculating their tree hash, and uploading them to AWS Glacier storage. It automates multipart uploads and tracks the uploaded data in a CSV log.

## Prerequisites

- Python 3.x
- AWS CLI configured with appropriate credentials and default region

python MultipartUpload.py input_file part_size vault_name

Example:

python MultipartUpload.py 'large_file.zip' 16 MyGlacierVault

5. The program will split the file, calculate the tree hash, upload the parts, and generate a CSV log (`MyGlacierVault.csv`) containing archive IDs, checksums, locations, original filenames, and upload timestamps.

## Notes

- Make sure your AWS CLI is configured correctly to allow access to Glacier.
- The program will generate a CSV log in the current directory.
- The tree hash calculation uses AWS's `botocore.utils`.
- The CSV log is useful for tracking uploads and managing your Glacier data.

For more information about AWS Glacier, refer to the official [AWS Glacier Documentation](https://docs.aws.amazon.com/amazonglacier/latest/dev/introduction.html).

