"""Tester B: the local-model golden set and its scorer (no Ollama needed)."""

import json
import unittest

from abos.localeval import FIELDS, GOLDEN, MUST_PASS, score


class LocalEval(unittest.TestCase):
    def test_golden_set_well_formed(self):
        items = [json.loads(line) for line in GOLDEN.read_text().splitlines()]
        self.assertEqual(len(items), 20)
        self.assertEqual(len({i["id"] for i in items}), 20)
        for item in items:
            self.assertEqual(sorted(item["expected"]), sorted(FIELDS))
        self.assertTrue(MUST_PASS <= {i["id"] for i in items})

    def test_scorer_normalizes_case_numbers_and_nulls(self):
        exp = {"product_name": "Black Protein Brew", "brand": None, "size_value": 250, "size_unit": "mL",
               "price": 3.25, "currency": "EUR", "protein_g": 12, "caffeine_mg": None}
        got = {"product_name": "black protein  brew", "brand": None, "size_value": "250", "size_unit": "ml",
               "price": 3.250, "currency": "eur", "protein_g": 12.0}
        self.assertTrue(all(score(exp, got).values()))
        got["price"] = 0
        self.assertFalse(score(exp, got)["price"])


if __name__ == "__main__":
    unittest.main()
