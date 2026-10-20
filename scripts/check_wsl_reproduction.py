"""Bounded native-disk reproduction in an existing Ubuntu WSL distribution.

Uses previously verified offline wheels; never installs a distribution or system
package. Windows monitors physical disk/RAM while Linux counts native files/RSS.
"""
import argparse
import ctypes
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from pisa.pipeline import configure_environment,load_config,source_contract,require_unchanged_source
from pisa.environment import runtime_identity
from pisa.io import digest,code_digest,write_json
from pisa.resources import Guard
from pisa.reproduction import RecordingGuard,committed_identity,scientific_paths,safe_extract,remove_disposable
from pisa.portability import compare_scientific_trees,comparison_plan

RESERVATION=1_500_000_000


def cancel_native(distribution,native):
    """Signal only this marked native run; PID reuse is checked with pidfds."""
    program=r'''
import pathlib,sys,os,json,signal,select,time
p=pathlib.Path(sys.argv[1]);b=pathlib.Path('/var/tmp/phage-immune-stress-axis_validation')
assert p.parent==b and p.name.startswith('run_native_')
if b.exists():assert not b.is_symlink() and b.stat().st_uid==os.getuid()
b.mkdir(mode=0o700,exist_ok=True)
p.mkdir(mode=0o700,exist_ok=True)
assert not p.is_symlink() and p.stat().st_uid==os.getuid() and p.resolve().parent==b.resolve()
(p/'.cancelled_by_host').write_text('host resource/timeout cancellation\n')
marker=p/'.pisa_native_validation_owned'
if not marker.exists():print('prevented_or_cancelled_before_marker');sys.exit(0)
m=json.loads(marker.read_text());assert m['uid']==os.getuid()
pid=m['pid'];stat=pathlib.Path('/proc')/str(pid)/'stat'
if not stat.exists():print('already_exited');sys.exit(0)
assert int(stat.read_text().rsplit(')',1)[1].split()[19])==m['start_ticks']
argv=(stat.parent/'cmdline').read_bytes().split(b'\0');argv=[a for a in argv if a]
assert argv[-1].decode()==str(p) and (stat.parent/'status').read_text().split('Uid:')[1].split()[0]==str(os.getuid())
fd=os.pidfd_open(pid,0)
tracker=None
try:
 assert int(stat.read_text().rsplit(')',1)[1].split()[19])==m['start_ticks']
 code=p/'checkout/src'
 if (code/'pisa/processes.py').is_file():
  sys.path.insert(0,str(code));from pisa.processes import _LinuxDescendants
  tracker=_LinuxDescendants(pid);tracker.observe();tracker.send_signal(signal.SIGTERM)
 else:signal.pidfd_send_signal(fd,signal.SIGTERM)
 poll=select.poll();poll.register(fd,select.POLLIN)
 if not poll.poll(10000):
  if tracker:tracker.observe();tracker.send_signal(signal.SIGKILL)
  else:signal.pidfd_send_signal(fd,signal.SIGKILL)
  assert poll.poll(5000),'Owned controller termination unconfirmed'
 if tracker:tracker.wait(timeout=5)
 print('owned_controller_and_observed_descendants_stopped')
finally:
 if tracker:tracker.close()
 os.close(fd)
'''
    result=subprocess.run(['wsl.exe','--distribution',distribution,'--cd','/','--exec',
        '/usr/bin/python3','-I','-B','-c',program,native],capture_output=True,text=True,timeout=25)
    if result.returncode:raise RuntimeError(result.stderr[-2000:] or 'Native cancellation acknowledgement failed')
    return result.stdout.strip()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--distribution',default='Ubuntu')
    args=parser.parse_args()
    if os.name!='nt':raise SystemExit('Run scripts/run_all.py directly on Linux; this helper requires a Windows WSL host.')
    root=ROOT;configure_environment(root)
    config=load_config(root/'config/analysis.yaml')
    guard=RecordingGuard(Guard(root,config));contract=source_contract(root,root/'config/analysis.yaml')
    now=datetime.now(timezone.utc);identifier='run_native_'+now.strftime('%Y%m%dT%H%M%S%fZ')
    disposable=root/'.cache/reproduction'/identifier
    native='/var/tmp/phage-immune-stress-axis_validation/'+identifier
    report={'schema_version':1,'started_utc':now.isoformat(),'status':'running',
        'scope':'same physical host, independently installed Ubuntu WSL environment, fresh committed-source offline execution',
        'distribution':args.distribution,'native_directory':native,'native_storage_reservation_bytes':RESERVATION,
        'scientific_network_requested':False,'workers':1,'native_total_alarm_seconds':900,
        'full_child_timeout_seconds':600,'outer_timeout_seconds':950,
        'windows_runtime':runtime_identity(),'comparison_plan_sha256':comparison_plan()['sha256']}
    output=root/'results/reports/linux_reproduction_check.json'
    started=time.monotonic();process=None;guest_complete=False
    ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
    try:
        report['windows_before']=guard.snapshot();guard.check(RESERVATION)
        identity=committed_identity(root,'HEAD');report['git']=identity
        if identity['estimated_tar_bound_bytes']>50_000_000:raise ValueError('Committed export exceeds cap')
        expected={p:digest(root/p) for p in scientific_paths(root)}
        if set(expected)!=set(comparison_plan()['expected_paths']):raise ValueError('Reference inventory differs from fixed plan')
        report['reference_sha256']=expected
        verified=json.loads((root/'.cache/linux/verified_wheels.json').read_text())
        if verified['status']!='ready_for_offline_venv_install':raise ValueError('Verified wheel inventory is incomplete')
        canon=lambda s:re.sub(r'[-_.]+','-',s).lower()
        pins={canon(k.strip()):v.strip() for line in (root/'requirements.txt').read_text().splitlines()
              if line.strip() and not line.startswith('#') for k,v in [line.split('==')]}
        if len(pins)!=21 or pins!={canon(r['name']):r['version'] for r in verified['wheels']}:
            raise ValueError('Verified wheels differ from current 21-version specification')
        disposable.mkdir(parents=True,exist_ok=False)
        source=disposable/'source.tar'
        subprocess.run(['git','-c','safe.directory='+root.as_posix(),'-C',str(root),'archive',
            '--format=tar','--output='+str(source),identity['commit']],check=True,timeout=60)
        if source.stat().st_size>50_000_000:raise ValueError('Actual source export exceeds cap')
        metadata={'run_id':identifier,'source':{'path':'source.tar','bytes':source.stat().st_size,
            'sha256':digest(source),'commit':identity['commit'],'tree':identity['tree'],
            'code_sha256':code_digest(root),'config_sha256':digest(root/'config/analysis.yaml'),
            'requirements_sha256':digest(root/'requirements.txt'),
            'input_manifest_sha256':digest(root/'data/manifests/inputs.json')},'config':config,'wheels':[]}
        staged=[(source,'source.tar')]
        for row in verified['wheels']:
            path=(root/row['path']).resolve()
            if (not path.is_relative_to((root/'.cache/linux').resolve())
                or path.stat().st_size!=row['wheel_bytes'] or digest(path)!=row['wheel_sha256']):
                raise ValueError('Verified wheel path/bytes changed')
            destination='wheels/'+path.name
            metadata['wheels'].append({'name':row['name'],'version':row['version'],'path':destination,
                'bytes':row['wheel_bytes'],'sha256':row['wheel_sha256']})
            staged.append((path,destination))
        pip=verified['pip_bootstrap'];pip_path=(root/pip['copied_path']).resolve()
        if not pip_path.is_relative_to((root/'.cache/linux').resolve()) or digest(pip_path)!=pip['sha256']:
            raise ValueError('Bundled pip bootstrap changed')
        metadata['pip']={'path':'bootstrap/'+pip_path.name,'bytes':pip['bytes'],'sha256':pip['sha256'],'version':pip['version']}
        staged.append((pip_path,metadata['pip']['path']))
        metadata_path=disposable/'metadata.json';write_json(metadata_path,metadata);staged.append((metadata_path,'metadata.json'))
        estimate=sum(p.stat().st_size for p,_ in staged)+4096*len(staged)+1_048_576
        if estimate>125_000_000:raise ValueError('Bootstrap estimate exceeds cap')
        guard.check(estimate+RESERVATION)
        bootstrap=disposable/'bootstrap.tar'
        with tarfile.open(bootstrap,'w') as archive:
            for path,name in staged:archive.add(path,arcname=name,recursive=False);guard.check(RESERVATION)
        if bootstrap.stat().st_size>125_000_000:raise ValueError('Bootstrap exceeds cap')
        report['bootstrap']={'bytes':bootstrap.stat().st_size,'sha256':digest(bootstrap)}
        helper=root/'scripts/_native_wsl_guest.py'
        report['helper_sha256']={p:digest(root/p) for p in ['scripts/check_wsl_reproduction.py','scripts/_native_wsl_guest.py']}
        command=['wsl.exe','--distribution',args.distribution,'--cd','/','--exec','/usr/bin/python3','-I','-B','-c',helper.read_text(),native]
        if len(subprocess.list2cmdline(command).encode('utf-16-le'))//2>30_000:raise ValueError('Guest command line exceeds cap')
        artifact=disposable/'guest_outputs.tar';console=root/'results/reports/linux_wsl_console.log'
        first=guard.check(RESERVATION)
        report['windows_min_available_memory_bytes']=first['available_memory_bytes'];report['windows_min_disk_free_bytes']=first['disk_free_bytes']
        with bootstrap.open('rb') as incoming,artifact.open('wb') as outgoing,console.open('w',encoding='utf-8') as log:
            process=subprocess.Popen(command,cwd=root,stdin=incoming,stdout=outgoing,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
            child_started=time.monotonic()
            while process.poll() is None:
                snapshot=guard.check(RESERVATION);guard.observe_processes()
                for name,key in [('windows_min_available_memory_bytes','available_memory_bytes'),('windows_min_disk_free_bytes','disk_free_bytes')]:
                    report[name]=min(report[name],snapshot[key])
                if artifact.stat().st_size>50_000_000:raise ValueError('Guest output stream exceeds cap')
                if time.monotonic()-child_started>950:raise TimeoutError('Native WSL supervisor timeout')
                time.sleep(0.25)
        report['wsl_exit_code']=process.returncode
        if artifact.stat().st_size>50_000_000:raise ValueError('Guest artifact exceeds cap')
        report['result_archive']={'bytes':artifact.stat().st_size,'sha256':digest(artifact)}
        received=disposable/'received'
        if artifact.stat().st_size:
            report['result_extraction']=safe_extract(artifact,received,50_000_000,guard)
            for name in ['guest_evidence.json','setup_evidence.json']:
                candidate=received/'results/reports'/name
                if candidate.is_file():report[name.removesuffix('.json')]=json.loads(candidate.read_text())
        if process.returncode:raise RuntimeError('Native WSL execution failed; inspect console and guest evidence')
        guest=report['guest_evidence']
        if guest['status']!='completed_independent_linux_validation':raise ValueError('Guest execution success contract failed')
        guest_complete=True
        require_unchanged_source(root,root/'config/analysis.yaml',contract)
        if any(digest(root/p)!=h for p,h in expected.items()):raise ValueError('Reference outputs changed during replay')
        if guest['source_before']['code_sha256']!=metadata['source']['code_sha256']:raise ValueError('Guest code identity differs')
        if guest['full_pipeline_status']['runtime']['packages']!=report['windows_runtime']['packages']:
            raise ValueError('Guest dependencies differ from Windows reference')
        report['comparison']=compare_scientific_trees(root,received)
        for row in report['comparison']['comparisons']:
            if row['status']=='needs_visual_review':
                target=root/'.cache/linux_figure_review'/Path(row['path']).name
                target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(received/row['path'],target)
        for name in ['validation.log','validation_summary.json','run_status.json','resource_usage.json']:
            candidate=received/'results/reports'/name
            if candidate.is_file():shutil.copyfile(candidate,root/'results/reports'/('linux_'+name))
        report['status']=report['comparison']['status']
        if report['status']=='failed':raise ValueError('Scientific portability comparison failed')
    except BaseException as error:
        report.update(status='interrupted' if isinstance(error,KeyboardInterrupt) else 'failed',error_type=type(error).__name__,error=str(error))
        if process is not None and process.poll() is None:
            try:
                report['guest_termination']=cancel_native(args.distribution,native)
                process.wait(timeout=10)
            except Exception as cancellation_error:
                report['cancellation_error']=str(cancellation_error)
                process.terminate()
                try:process.wait(timeout=10)
                except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
                report['guest_termination']='unconfirmed_native_alarm_and_evidence_retained'
        raise
    finally:
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
        if guest_complete and report.get('status') in ('passed','needs_visual_review'):
            cleanup="import pathlib,json,shutil,sys,os; p=pathlib.Path(sys.argv[1]); b=pathlib.Path('/var/tmp/phage-immune-stress-axis_validation'); assert p.parent==b and p.name.startswith('run_native_') and p.resolve().parent==b.resolve() and p.stat().st_uid==os.getuid(); m=json.loads((p/'.pisa_native_validation_owned').read_text()); assert m['uid']==os.getuid(); shutil.rmtree(p); print('removed')"
            try:
                result=subprocess.run(['wsl.exe','--distribution',args.distribution,'--cd','/','--exec','/usr/bin/python3','-I','-B','-c',cleanup,native],capture_output=True,text=True,timeout=30)
                if result.returncode or result.stdout.strip()!='removed':raise RuntimeError(result.stderr[-2000:] or 'Missing cleanup acknowledgement')
                report['native_cleanup']='removed_verified_owned_directory'
            except Exception as error:report.update(status='failed',native_cleanup_error=str(error))
        else:report['native_cleanup']='retained_after_failure_termination_not_assumed'
        try:report['windows_before_cleanup']=guard.snapshot()
        except Exception as error:report.update(status='failed',resource_error=str(error))
        if disposable.exists() and report.get('status') in ('passed','needs_visual_review'):
            try:remove_disposable(root,disposable);report['disposable_cleanup']='removed'
            except Exception as error:report.update(status='failed',cleanup_error=str(error))
        elif disposable.exists():report['disposable_cleanup']='retained_after_failure';report['disposable_path']=disposable.relative_to(root).as_posix()
        try:report['windows_after_cleanup']=guard.snapshot()
        except Exception as error:report.update(status='failed',final_resource_error=str(error))
        report.update(elapsed_seconds=round(time.monotonic()-started,3),finished_utc=datetime.now(timezone.utc).isoformat())
        write_json(output,report)
    print(json.dumps({'status':report['status'],'byte_identical_outputs':report.get('comparison',{}).get('byte_identical_outputs')}),flush=True)
    return 0 if report['status']=='passed' else 2 if report['status']=='needs_visual_review' else 1


if __name__=='__main__':raise SystemExit(main())
