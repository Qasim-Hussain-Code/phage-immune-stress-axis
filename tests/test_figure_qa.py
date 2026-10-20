import json
from pathlib import Path
import tempfile
import unittest
from pisa.figure_qa import review_status
from pisa.io import digest


class RecordedFigureReview(unittest.TestCase):
    def test_review_is_invalidated_by_changed_or_added_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'figures').mkdir();(root/'data/manifests').mkdir(parents=True)
            path=root/'figures/software_fixture.pdf';path.write_bytes(b'software-only fixture, not an actual PDF')
            manifest={'figures':[{'path':'figures/software_fixture.pdf','sha256':digest(path),'visual_status':'passed'}]}
            (root/'data/manifests/figure_qa.json').write_text(json.dumps(manifest))
            self.assertEqual(review_status(root)['status'],'previous_review_matches_current_files')
            path.write_bytes(b'changed fixture')
            self.assertEqual(review_status(root)['status'],'unverified_current_files')
            manifest['figures'][0]['sha256']=digest(path)
            (root/'data/manifests/figure_qa.json').write_text(json.dumps(manifest))
            (root/'figures/unreviewed.pdf').write_bytes(b'new fixture')
            self.assertEqual(review_status(root)['unreviewed_current_pdfs'],['figures/unreviewed.pdf'])

    def test_missing_review_never_means_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(review_status(Path(tmp))['status'],'unverified')
