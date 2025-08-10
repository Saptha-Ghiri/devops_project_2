# Flask App with S3 and GitHub Actions Deployment

## 1. Project Overview
This project hosts a Flask web application on an AWS EC2 instance that:
- Accepts **Name** and **Age** from the user.
- Stores the data as JSON in an **S3 bucket**.
- Is deployed and updated automatically via **GitHub Actions**.

---

## 2. Prerequisites
Before starting, ensure you have:
1. **AWS EC2 instance** running Ubuntu.
2. **IAM Role** attached to EC2 with **AmazonS3FullAccess**.
3. **AWS S3 bucket** created (replace `test-bucket-saptha-ghiri` with your bucket name).
4. **GitHub repository** with your Flask app code.
5. **SSH key pair** for EC2.

---

## 3. Setting Up EC2

### Step 1 — Update and Install Requirements
```bash
sudo apt update -y
sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv unzip -y
```

### Step 2 — Install AWS CLI
```bash
cd ~
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws --version
```

### Step 3 — Clone Your Repo
```bash
cd ~
git clone https://github.com/<your-username>/<your-repo>.git devops_project_2
cd devops_project_2
```

### Step 4 — Create Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install flask boto3
```

---

## 4. Flask App (`app.py`)
```python
from flask import Flask, request, render_template
import boto3
import json
import botocore

app = Flask(__name__)
S3_BUCKET = "test-bucket-saptha-ghiri"
S3_REGION = "ap-south-1"
s3_client = boto3.client("s3")

@app.route("/", methods=["GET", "POST"])
def home():
    message = None
    file_key = "data.json"
    try:
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=file_key)
        data_list = json.loads(response["Body"].read().decode("utf-8"))
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            data_list = []
        else:
            raise e

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        data_list.append({"name": name, "age": age})
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=file_key,
            Body=json.dumps(data_list),
            ContentType="application/json"
        )
        message = f"Data for {name} stored successfully!"

    return render_template("index.html", message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

---

## 5. HTML Form (`templates/index.html`)
```html
<!DOCTYPE html>
<html>
<head>
    <title>Flask S3 App</title>
</head>
<body>
    <h1>Enter Your Details</h1>
    <form method="POST">
        Name: <input type="text" name="name" required><br><br>
        Age: <input type="number" name="age" required><br><br>
        <input type="submit" value="Submit">
    </form>
    {% if message %}
        <p>{{ message }}</p>
    {% endif %}
</body>
</html>
```

---

## 6. Manual Test
Start Flask App:
```bash
source ~/venv/bin/activate
python3 app.py
```
Visit **`http://<EC2-Public-IP>:8080`** in your browser.

---

## 7. GitHub Actions Auto Deployment
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy Flask App to EC2

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repo
      uses: actions/checkout@v3

    - name: Set up SSH
      uses: webfactory/ssh-agent@v0.9.0
      with:
        ssh-private-key: ${{ secrets.EC2_SSH_KEY }}

    - name: Deploy to EC2
      run: |
        ssh -o StrictHostKeyChecking=no ubuntu@${{ secrets.EC2_HOST }} << 'EOF'
          cd /home/ubuntu/devops_project_2
          git pull origin main
          source /home/ubuntu/venv/bin/activate
          pkill -f app.py || true
          nohup python3 app.py > flask.log 2>&1 &
        EOF
```

---

## 8. GitHub Secrets Needed
In your repo settings → Secrets and variables → Actions:
- `EC2_SSH_KEY` → Paste **private key** from your EC2 `.pem` file.
- `EC2_HOST` → Your EC2 **Public IP**.

---

## 9. Viewing Logs
SSH into EC2:
```bash
ssh -i mykey.pem ubuntu@<EC2-Public-IP>
cd devops_project_2
cat flask.log
```

---

## 10. Flow Summary
1. User submits **Name** & **Age** in HTML form.
2. Flask app appends it to `data.json` in **S3**.
3. GitHub Actions deploys latest code to EC2 automatically.
4. Flask restarts with new code — no manual intervention.
