import os
import json
import boto3
from botocore.client import Config
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from backend/.env if it exists
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / 'backend' / '.env')

# Configuration variables
MINIO_URL = os.getenv("MINIO_ENDPOINT_URL", "http://localhost:9000")
ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "aria")

print(f"Connecting to MinIO at {MINIO_URL}...")
print(f"Target Bucket: {BUCKET_NAME}")

# 1. Initialize the S3 client for MinIO
s3 = boto3.client(
    "s3",
    endpoint_url=MINIO_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version="s3v4"),
)

# 2. Check if bucket exists, create it if it doesn't
try:
    s3.head_bucket(Bucket=BUCKET_NAME)
    print(f"Bucket '{BUCKET_NAME}' already exists.")
except Exception:
    print(f"Bucket '{BUCKET_NAME}' does not exist. Creating it now...")
    s3.create_bucket(Bucket=BUCKET_NAME)
    print(f"Bucket '{BUCKET_NAME}' created successfully.")

# 3. Define the public read-only policy
# The Action "s3:GetObject" allows anonymous downloads
public_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicRead",
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{BUCKET_NAME}/*"],
        }
    ],
}

# 4. Apply the policy to the bucket
try:
    s3.put_bucket_policy(
        Bucket=BUCKET_NAME, Policy=json.dumps(public_policy)
    )
    print(f"Successfully made bucket '{BUCKET_NAME}' public for downloads!")
except Exception as e:
    print(f"Error applying policy: {e}")
