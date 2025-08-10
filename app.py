from flask import Flask, request, render_template
import boto3
import json
import botocore

app = Flask(__name__)

# S3 Config
S3_BUCKET = "test-bucket-saptha-ghiri"
S3_REGION = "ap-south-1"
S3_FILE_KEY = "user_data.json"  # One file for all data

# Create S3 client
s3_client = boto3.client("s3")

@app.route("/", methods=["GET", "POST"])
def home():
    message = None
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]

        # Step 1: Try to fetch existing file from S3
        try:
            obj = s3_client.get_object(Bucket=S3_BUCKET, Key=S3_FILE_KEY)
            file_content = obj["Body"].read().decode("utf-8")
            data_list = json.loads(file_content)
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                data_list = []  # File doesn't exist yet
            else:
                raise e

        # Step 2: Append new record
        data_list.append({"name": name, "age": age})

        # Step 3: Upload updated file back to S3
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=S3_FILE_KEY,
            Body=json.dumps(data_list, indent=2),
            ContentType="application/json"
        )

        message = f"Added {name}'s data to {S3_FILE_KEY} in S3."

    return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
