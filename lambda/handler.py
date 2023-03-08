import boto3
import os
import mimetypes
import email
import email.mime.application
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import codecs

s3 = boto3.client('s3')
ses = boto3.client('ses')


def lambda_handler(event, context):
    # Extract the bucket name and file key from the S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']

    # Retrieve the file from S3
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    file_content = response['Body'].read()
    file_name = os.path.basename(file_key)
    file_type, _ = mimetypes.guess_type(file_name)

    # Construct the email message
    msg = MIMEMultipart('mixed')
    msg['Subject'] = 'New file uploaded'
    msg['From'] = os.environ['EMAIL_FROM']
    msg['To'] = os.environ['EMAIL_TO']

    # Create a multipart/alternative submessage for the HTML body
    submsg = MIMEMultipart('alternative')
    html_body = MIMEText(
        '<html><body><p>A new file has been uploaded:</p></body></html>', 'html')
    submsg.attach(html_body)
    msg.attach(submsg)

    # Create a multipart/mixed submessage for the file attachment
    if file_type:
        if 'image' in file_type:
            file_attachment = MIMEImage(
                file_content, _subtype=os.path.splitext(file_name)[1])
        else:
            file_attachment = email.mime.application.MIMEApplication(
                codecs.encode(file_content.decode()), _subtype=os.path.splitext(file_name)[1])
        file_attachment.add_header(
            'Content-Disposition', 'attachment', filename=file_name)
        msg.attach(file_attachment)

    # Convert the message to a raw string and send it via SES
    raw_msg = email.utils.make_msgid().strip(
        '<>') + '.' + email.utils.make_msgid().strip('<>')
    raw_msg_bytes = msg.as_bytes()
    response = ses.send_raw_email(
        Source=msg['From'],
        Destinations=[msg['To']],
        RawMessage={'Data': raw_msg_bytes}
    )
    return {
        'statusCode': 200,
        'body': 'Email sent successfully'
    }
