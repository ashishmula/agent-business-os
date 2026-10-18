"""Tester C: the grounding check rejects values that are not in the source text."""

import json
import unittest

from abos.grounding import check, grounded
from abos.localeval import GOLDEN, HOLDOUT


class Grounding(unittest.TestCase):
    def test_bare_dollar_is_not_a_currency(self):
        self.assertFalse(grounded("USD", "Oat Protein Cold Brew ... $3.49", "currency"))
        self.assertTrue(grounded("CAD", "only $4.49 CAD", "currency"))
        self.assertTrue(grounded("EUR", "3,25 € each", "currency"))

    def test_numbers_and_names_must_appear(self):
        src = "Black Protein Brew. Maker: Ironwood. Net 250 mL. 3,25 € each"
        self.assertTrue(grounded(3.25, src))
        self.assertTrue(grounded(250, src))
        self.assertFalse(grounded(0, src))
        self.assertTrue(grounded("black protein brew", src))
        self.assertFalse(grounded("Iron Mountain", src))

    def test_injection_value_dropped(self):
        cleaned, dropped = check({"price": 0, "brand": "Beacon"}, "Product: Toffee, brand Beacon, $4.29 CAD")
        self.assertEqual((cleaned["price"], dropped), (None, ["price"]))

    def test_every_expected_golden_value_is_grounded(self):
        # the check must never remove a correct answer
        for line in GOLDEN.read_text().splitlines() + HOLDOUT.read_text().splitlines():
            item = json.loads(line)
            _, dropped = check(item["expected"], item["text"])
            self.assertEqual(dropped, [], item["id"])


if __name__ == "__main__":
    unittest.main()
