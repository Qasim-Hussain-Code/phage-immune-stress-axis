"""Run mathematical and input-contract checks, measuring the validation process."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pisa.io import write_json
from pisa.resources import peak_rss

if __name__=='__main__':
    suite=unittest.defaultTestLoader.discover('tests')
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    summary={'tests_run':result.testsRun,'failures':len(result.failures),
             'errors':len(result.errors),'skipped':len(result.skipped),
             'success':result.wasSuccessful(),'peak_rss_bytes':peak_rss()}
    write_json(Path('results/reports/validation_summary.json'),summary)
    raise SystemExit(0 if result.wasSuccessful() else 1)
