import os
import boto3
import mimetypes

from email.utils import make_msgid
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


s3 = boto3.client('s3')
ses = boto3.client('ses')


def get_file_from_s3(bucket_name, file_key):
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    file_content = response['Body'].read()
    return file_content


def construct_email_message(file_key, bucket_name):
    file_name = os.path.basename(file_key)
    file_type, _ = mimetypes.guess_type(file_name)
    msg = MIMEMultipart('mixed')
    msg['Subject'] = f'New file uploaded: {file_name}'
    msg['From'] = os.environ['EMAIL_FROM']
    msg['To'] = os.environ['EMAIL_TO']
    body = get_email_body(file_key, bucket_name)
    submsg = MIMEText(body, 'html')
    msg.attach(submsg)
    if file_type and file_type.startswith('image'):
        file_content = get_file_from_s3(bucket_name, file_key)
        file_attachment = MIMEImage(file_content)
    else:
        file_content = get_file_from_s3(bucket_name, file_key)
        file_attachment = MIMEApplication(
            file_content, _subtype=os.path.splitext(file_name)[1])
    file_attachment.add_header(
        'Content-Disposition', 'attachment', filename=file_name)
    msg.attach(file_attachment)
    return msg


def get_email_body(file_key, bucket_name):
    return f"""
      <html>
        <body>
          <h3>A new file has been uploaded:</h3>
          <table style="border-collapse: collapse;">
            <tr>
              <td style="font-weight: bold;">Bucket:</td>
              <td>{bucket_name}</td>
            </tr>
            <tr>
              <td style="font-weight: bold;">File:</td>
              <td>{file_key}</td>
            </tr>
          </table>
        </body>
      </html>
    """


def send_email(file_content, file_key, bucket_name):
    msg = construct_email_message(file_key, bucket_name)
    raw_msg = make_msgid().strip(
        '<>') + '.' + make_msgid().strip('<>')
    raw_msg_bytes = msg.as_bytes()
    response = ses.send_raw_email(
        Source=msg['From'],
        Destinations=[msg['To']],
        RawMessage={'Data': raw_msg_bytes}
    )


def lambda_handler(event, context):
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    file_content = get_file_from_s3(bucket_name, file_key)
    send_email(file_content, file_key, bucket_name)
    return {
        'statusCode': 200,
        'body': 'Email sent successfully'
    }
