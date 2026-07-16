import base64
import boto3
import botocore
import mimetypes
import os
import unittest

from email.message import Message
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid
from handler import get_file_from_s3, construct_email_message, send_email
from unittest.mock import MagicMock, patch
from unittest import TestCase, mock


class TestLambdaFunction(unittest.TestCase):

    def setUp(self):
        self.bucket_name = 'test-bucket'
        self.file_key = 'test-file.txt'
        self.email_from = 'sender@example.com'
        self.email_to = 'recipient@example.com'
        self.s3 = boto3.client('s3')
        self.ses = boto3.client('ses')
        self.file_content = b'Test file content'
        # Set EMAIL_FROM environment variable
        os.environ['EMAIL_FROM'] = 'sender@example.com'
        os.environ['EMAIL_TO'] = 'recipient@example.com'

    @patch('boto3.resource')
    def test_get_file_from_s3(self, mock_s3_resource):
        bucket_name = 'test-bucket'
        file_key = 'test-file.txt'
        expected_content = b'test file content'
        mock_object = mock.Mock()
        mock_object.get()['Body'].read.return_value = expected_content
        mock_s3_resource().Bucket().Object.return_value = mock_object

        content = get_file_from_s3(bucket_name, file_key)
        self.assertEqual(content, expected_content)

    def test_construct_email_message_with_image_attachment(self):
        # Mock get_file_from_s3
        expected_content = self.file_content
        get_file_from_s3_mock = MagicMock(return_value=expected_content)
        # Call function
        msg = construct_email_message('test-image.png', self.bucket_name)
        # Check result
        self.assertIsInstance(msg, Message)
        self.assertEqual(msg['Subject'], 'New file uploaded: test-image.png')
        self.assertEqual(msg['From'], os.environ['EMAIL_FROM'])
        self.assertEqual(msg['To'], os.environ['EMAIL_TO'])
        self.assertIn('<h3>A new file has been uploaded:</h3>', str(msg))
        self.assertIn('<td>test-image.png</td>', str(msg))
        self.assertIn(
            'Content-Disposition: attachment; filename="test-image.png"', str(msg))
        self.assertEqual(len(msg.get_payload()), 2)
        self.assertIsInstance(msg.get_payload()[1], MIMEImage)
        self.assertEqual(msg.get_payload()[1].get_payload(), expected_content)
        get_file_from_s3_mock.assert_called_once_with(
            self.bucket_name, 'test-image.png')

    @patch('handler.s3')
    def test_send_email(self, mock_s3):
        mock_s3.get_object.return_value = {'Body': MagicMock(
            read=MagicMock(return_value=self.file_content))}
        send_email(self.file_content, self.file_key, self.bucket_name)
        self.assertTrue(mock_s3.get_object.called)
        self.assertTrue(mock_ses.send_raw_email.called)

    @patch('handler.get_file_from_s3')
    def test_construct_email_message_with_non_image_attachment(self, mock_get_file_from_s3):
        mock_get_file_from_s3.return_value = self.file_content
        msg = construct_email_message('test-file.txt', self.bucket_name)
        self.assertIsInstance(msg, Message)
        self.assertEqual(msg['Subject'], 'New file uploaded: test-file.txt')
        self.assertEqual(msg['From'], os.environ['EMAIL_FROM'])
        self.assertEqual(msg['To'], os.environ['EMAIL_TO'])
        self.assertIn('<html>', msg.as_string())
        self.assertIn('Bucket:', msg.as_string())
        self.assertIn('test-bucket', msg.as_string())
        self.assertIn('File:', msg.as_string())
        self.assertIn('test-file.txt', msg.as_string())
        self.assertEqual(len(msg.get_payload()), 2)
        self.assertIsInstance(msg.get_payload()[0], Message)
        self.assertIsInstance(msg.get_payload()[1], Message)
        self.assertIn('Content-Disposition: inline',
                      msg.get_payload()[0].as_string())
        self.assertIn('Content-Disposition: attachment',
                      msg.get_payload()[1].as_string())

    @patch('email.utils.make_msgid', side_effect=['<message-id-1>', '<message-id-2>'])
    def test_send_email(self, make_msgid_mock):
        # Mock SES client
        self.ses.send_raw_email = MagicMock()
        # Call function
        send_email(self.file_content, self.file_key, self.bucket_name)
        # Check result
        self.ses.send_raw_email.assert_called_once_with(
            Source=self.email_from,
            Destinations=[self.email_to],
            RawMessage={'Data': msg.as_bytes()}
        )
        make_msgid_mock.assert_called()
        self.assertEqual(make_msgid_mock.call_count, 2)


@patch('email.utils.make_msgid', side_effect=['<message-id-1>', '<message-id-2>'])
@patch.object(boto3, 'client')
def test_lambda_handler(self, boto3_mock, make_msgid_mock):
    # Mock event data
    event = {
        'Records': [
            {
                's3': {
                    'bucket': {'name': self.bucket_name},
                    'object': {'key': self.file_key}
                }
            }
        ]
    }
    # Mock S3 and SES clients
    expected_content = self.file_content
    self.s3.get_object = MagicMock(
        return_value={'Body': MagicMock(read=lambda: expected_content)})
    self.ses.send_raw_email = MagicMock()
    boto3_mock.side_effect = [self.s3, self.ses]
    # Call function
    result = lambda_handler(event, None)
    # Check result
    self.assertEqual(result, {'statusCode': 200,
                     'body': 'Email sent successfully'})
    self.s3.get_object.assert_called_once_with(
        Bucket=self.bucket_name, Key=self.file_key)
    self.ses.send_raw_email.assert_called_once_with(
        Source=self.email_from,
        Destinations=[self.email_to],
        RawMessage={'Data': make_msgid_mock.return_value +
                    '.' + make_msgid_mock.return_value + '\r\n'}
    )
    make_msgid_mock.assert_called()
    self.assertEqual(make_msgid_mock.call_count, 2)


if __name__ == 'main':
    unittest.main()
