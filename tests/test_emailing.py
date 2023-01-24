import unittest

from coles_vs_woolies.emailing.mailer_send import send
from unittest.mock import patch


class TestSearch(unittest.TestCase):

    def test_send(self):
        with patch("coles_vs_woolies.emailing.mailer_send.emails.NewEmail.send") as mock:
            mock.return_value = '202'
            send(email_html='Some HTML string',
                 to_addrs=['test@domain.com'],
                 from_addr='test@domain.com',
                 mailersend_api_key='asdf')

    def test_missing_api_key(self):
        with patch("coles_vs_woolies.emailing.mailer_send.load_dotenv") as mock:
            with self.assertRaises(ValueError) as context:
                send(email_html='Some HTML string', to_addrs=['test@domain.com'], from_addr='test@domain.com')

        self.assertTrue("MailerSend API Key not provided" in context.exception.args)


if __name__ == '__main__':
    unittest.main()
