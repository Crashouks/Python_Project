import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tourist_routes.utils.bank_account import BankAccount  # noqa: E402


class BankAccountTests(unittest.TestCase):
    def setUp(self):
        self.account = BankAccount(100)

    def tearDown(self):
        self.account = None

    def test_initial_balance(self):
        self.assertEqual(self.account.get_balance(), 100)
        self.assertEqual(BankAccount().get_balance(), 0)

    def test_invalid_initial_balance(self):
        with self.assertRaises(ValueError):
            BankAccount(-1)
        for value in ("100", None, True):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    BankAccount(value)

    def test_deposit(self):
        self.assertEqual(self.account.deposit(50), 150)
        self.assertEqual(self.account.get_balance(), 150)

    def test_deposit_float(self):
        self.account.deposit(0.5)
        self.assertAlmostEqual(self.account.get_balance(), 100.5)

    def test_deposit_rejects_non_positive(self):
        for amount in (0, -10, float("nan"), float("inf")):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    self.account.deposit(amount)
        self.assertEqual(self.account.get_balance(), 100)

    def test_deposit_rejects_wrong_type(self):
        for amount in ("10", None, True, [5]):
            with self.subTest(amount=amount):
                with self.assertRaises(TypeError):
                    self.account.deposit(amount)

    def test_withdraw(self):
        self.assertEqual(self.account.withdraw(30), 70)
        self.assertEqual(self.account.get_balance(), 70)

    def test_withdraw_entire_balance(self):
        self.account.withdraw(100)
        self.assertEqual(self.account.get_balance(), 0)

    def test_withdraw_more_than_balance(self):
        with self.assertRaises(ValueError) as context:
            self.account.withdraw(100.01)
        self.assertIn("Недостатньо", str(context.exception))
        self.assertEqual(self.account.get_balance(), 100)

    def test_withdraw_rejects_non_positive_and_wrong_type(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(0)
        with self.assertRaises(ValueError):
            self.account.withdraw(-5)
        with self.assertRaises(TypeError):
            self.account.withdraw("5")

    def test_sequence_of_operations(self):
        self.account.deposit(50)
        self.account.withdraw(120)
        self.account.deposit(20)
        self.assertEqual(self.account.get_balance(), 50)


if __name__ == "__main__":
    unittest.main()
