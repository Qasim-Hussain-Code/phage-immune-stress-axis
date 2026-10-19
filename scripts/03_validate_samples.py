from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pisa.pipeline import stage_entry
if __name__=='__main__':
    stage_entry('03_validate_samples')
