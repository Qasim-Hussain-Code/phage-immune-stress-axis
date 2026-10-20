"""Run mathematical and input-contract checks, measuring the validation process."""
from pathlib import Path
from datetime import datetime,timezone
import importlib.metadata
import os
import sys
import tempfile
import time
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pisa.io import write_json,code_digest
from pisa.resources import peak_rss


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
    suite=unittest.defaultTestLoader.discover('tests')
    result=unittest.TextTestRunner(verbosity=2,resultclass=TimedResult).run(suite)
    versions={}
    for name in ['numpy','scipy','statsmodels','matplotlib','openpyxl','PyYAML','pypdf']:
        try:versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:versions[name]=None
    summary={'schema_version':2,'started_utc':started_utc,
             'finished_utc':datetime.now(timezone.utc).isoformat(),
             'duration_seconds':round(time.monotonic()-started,3),
             'code_sha256':code_digest(root),'python':sys.version,
             'package_versions':versions,
             'test_timings':getattr(result,'test_timings',[]),
             'tests_run':result.testsRun,'failures':len(result.failures),
             'errors':len(result.errors),'skipped':len(result.skipped),
             'success':result.wasSuccessful() and result.testsRun>0,'peak_rss_bytes':peak_rss()}
    write_json(Path('results/reports/validation_summary.json'),summary)
    raise SystemExit(0 if result.wasSuccessful() else 1)
