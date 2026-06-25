import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import pandas as pd
from reliabj.parsers import parse_pairwise_output
from reliabj.metrics import accuracy, expected_calibration_error


class ParserMetricTests(unittest.TestCase):
    def test_parse_pairwise_json(self):
        out = parse_pairwise_output('{"winner":"A","confidence":0.9,"rationale":"ok"}')
        self.assertEqual(out["parsed_label"], "A")
        self.assertEqual(out["confidence"], 0.9)

    def test_accuracy(self):
        df = pd.DataFrame({"parsed_label": ["A", "B"], "gold_label": ["A", "A"], "confidence": [0.8, 0.7]})
        self.assertEqual(accuracy(df), 0.5)
        self.assertGreaterEqual(expected_calibration_error(df), 0.0)


if __name__ == '__main__':
    unittest.main()
