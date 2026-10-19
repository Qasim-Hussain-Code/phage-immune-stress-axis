import json
import math
from pathlib import Path
import unittest
from pisa.metrics import close,clr,aitchison,bray_curtis


class CommunityMath(unittest.TestCase):
    def setUp(self):
        self.fixture=json.loads((Path(__file__).parent/'fixtures/community_software_only.json').read_text())
    def test_closure_scale_invariance(self):
        self.assertEqual(close([1,2,4]),close([10,20,40]))
        self.assertAlmostEqual(sum(clr([1,2,4])),0)
    def test_pairwise_logratio_identity(self):
        x,y=self.fixture['a'],self.fixture['b']
        independent=math.sqrt(sum((math.log(x[i]/x[j])-math.log(y[i]/y[j]))**2
                              for i in range(3) for j in range(3))/(2*3))
        self.assertAlmostEqual(aitchison(x,y),independent)
    def test_bray_curtis_scipy(self):
        from scipy.spatial.distance import braycurtis
        x,y=self.fixture['a'],self.fixture['b']
        self.assertAlmostEqual(bray_curtis(x,y),float(braycurtis(close(x),close(y))))
    def test_zero_handling_and_identity(self):
        self.assertEqual(aitchison([0,1,3],[0,2,6]),0)
        self.assertNotEqual(clr([0,1,3],.1),clr([0,1,3],.5))
    def test_invalid_abundances(self):
        for x in [[0,0],[-1,1],[float('nan'),1],[]]:
            with self.subTest(x=x),self.assertRaises(ValueError):close(x)
        with self.assertRaises(ValueError):aitchison([1],[1,2])
        with self.assertRaises(ValueError):clr([1,2],0)
