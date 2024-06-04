import unittest
from smtplib import SMTP


class TestExample(unittest.TestCase):
    """Example test case"""

    def setUp(self) -> None:
        self.name = "Jon Doe"
        return super().setUp()

    def test_name(self):
        self.assertEqual(self.name, "Jon Doe")
