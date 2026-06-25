import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from reliabj.perturbations import generate_variants


class PerturbationTests(unittest.TestCase):
    def test_generate_variants_order_swap(self):
        item = {"item_id":"x", "task_type":"pairwise", "responses":{"A":"good", "B":"bad"}, "gold_label":"A"}
        variants = generate_variants(item, ["identity", "order_swap"])
        self.assertEqual(len(variants), 2)
        self.assertEqual(variants[1]["responses"]["A"], "bad")
        self.assertEqual(variants[1]["gold_label"], "B")


if __name__ == '__main__':
    unittest.main()
