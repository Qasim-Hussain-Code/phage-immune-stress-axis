from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pisa.pipeline import main
if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        from pisa.io import write_json
        import json
        path=Path(__file__).resolve().parents[1]/'results/reports/run_status.json'
        status=json.loads(path.read_text()) if path.exists() else {}
        status.update({'status':'failed','error':f'{type(exc).__name__}: {exc}'})
        write_json(path,status)
        raise
