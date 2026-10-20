"""Check recorded PDF review hashes; optionally render current PDFs for inspection."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pisa.figure_qa import review_status,render_for_review


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render',action='store_true')
    parser.add_argument('--output',default='.cache/pdf_qa/current')
    parser.add_argument('--renderer-path',default=None)
    parser.add_argument('--scale',type=float,default=1.5)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    if args.render:
        from pisa.pipeline import load_config
        from pisa.resources import Guard
        renderer=args.renderer_path
        if renderer is None and (root/'.cache/pdf_renderer').is_dir():
            renderer=root/'.cache/pdf_renderer'
        result=render_for_review(root,root/args.output,renderer,args.scale,
                                 Guard(root,load_config(root/'config/analysis.yaml')))
    else:
        result=review_status(root)
    print(json.dumps(result,indent=2))
    return 0 if args.render or result['status']=='previous_review_matches_current_files' else 1


if __name__=='__main__':
    raise SystemExit(main())
