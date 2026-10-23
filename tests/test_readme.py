"""Reader-facing numbers must track the computed primary contrasts."""
from pathlib import Path
import unittest
from pisa.io import read_csv
from pisa.reporting import verify_readme_primary_table

ROOT=Path(__file__).resolve().parents[1]


class ReadmeNumbers(unittest.TestCase):
    def test_real_readme_matches_computed_estimates_and_counts(self):
        self.assertTrue(verify_readme_primary_table((ROOT/'README.md').read_text(encoding='utf-8'),
            read_csv(ROOT/'results/tables/immune_contrasts.csv')))

    def test_stale_count_effect_interval_or_q_is_rejected(self):
        text=(ROOT/'README.md').read_text(encoding='utf-8')
        rows=read_csv(ROOT/'results/tables/immune_contrasts.csv')
        for name,value in [('n_first','999'),('mean_difference','999'),('ci_low','-999'),('q_value','0.9')]:
            changed=[dict(row) for row in rows];changed[0][name]=value
            with self.subTest(field=name),self.assertRaises(ValueError):
                verify_readme_primary_table(text,changed)
