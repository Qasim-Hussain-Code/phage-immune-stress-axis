"""Run mathematical and input-contract checks, measuring the validation process."""
from pathlib import Path
from datetime import datetime,timezone
import os
import sys
import tempfile
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pisa.io import write_json,code_digest
from pisa.resources import peak_rss
from pisa.environment import package_versions
from pisa import __version__


class TimedResult(unittest.TextTestResult):
    def startTest(self,test):
        self._test_started=time.monotonic()
        if not hasattr(self,'test_timings'):self.test_timings=[]
        super().startTest(test)

    def stopTest(self,test):
        self.test_timings.append({'test':test.id(),'seconds':round(time.monotonic()-self._test_started,6)})
        super().stopTest(test)

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    os.chdir(root)
    temporary=root/'.cache/tmp';temporary.mkdir(parents=True,exist_ok=True)
    tempfile.tempdir=str(temporary)
    for name in ['TMP','TEMP','TMPDIR']:os.environ[name]=str(temporary)
    started=time.monotonic()
    started_utc=datetime.now(timezone.utc).isoformat()
    initial_code=code_digest(root)
    suite=unittest.defaultTestLoader.discover('tests')
    result=unittest.TextTestRunner(verbosity=2,resultclass=TimedResult).run(suite)
    final_code=code_digest(root)
    summary={'schema_version':2,'started_utc':started_utc,
             'project_version':__version__,
             'finished_utc':datetime.now(timezone.utc).isoformat(),
             'duration_seconds':round(time.monotonic()-started,3),
             'code_sha256':initial_code,'code_sha256_after':final_code,
             'source_unchanged_during_validation':initial_code==final_code,'python':sys.version,
             'package_versions':package_versions(),
             'test_timings':getattr(result,'test_timings',[]),
             'tests_run':result.testsRun,'failures':len(result.failures),
             'errors':len(result.errors),'skipped':len(result.skipped),
             'success':result.wasSuccessful() and result.testsRun>0 and initial_code==final_code,'peak_rss_bytes':peak_rss()}
    if initial_code!=final_code:
        summary['execution_error']='Source or test files changed during validation; results cannot attest the final code'
        print(summary['execution_error'],file=sys.stderr)
    write_json(Path('results/reports/validation_summary.json'),summary)
    raise SystemExit(0 if summary['success'] else 1)
