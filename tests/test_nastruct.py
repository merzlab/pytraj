#!/usr/bin/env python
from __future__ import print_function
import unittest
import numpy as np
import pytraj as pt
from pytraj.testing import aa_eq

class TestNastruct(unittest.TestCase):
    def test_nupars(self):
        fn = "./data/Test_NAstruct/adh026.3.pdb"
        traj = pt.iterload(fn, fn)
        data= pt.nastruct(traj)

        # default
        text = '''
        parm "./data/Test_NAstruct/adh026.3.pdb"
        trajin "./data/Test_NAstruct/adh026.3.pdb"
        nastruct
        '''

        state = pt.load_cpptraj_state(text)
        state.run()

        for key in ['major', 'minor', 'twist']:
            cpp_data = np.array([x.values for x in state.data if x.aspect == key])
            # need to transpose to get shape=(n_frames, n_pairs)
            cpp_data = cpp_data.T
            aa_eq(data[key][1], cpp_data)

        # TODO: assert
        data._summary(np.mean, indices=None)
        data._summary(np.mean, indices=[1,])
        data._summary(np.mean, keys=['major', 'twist'], indices=[1,])
        data._summary(np.std, indices=[1,])

        # pickle
        pt.to_pickle(data, 'data/na.pk')
        na2 = pt.read_pickle('data/na.pk')

        for key in data.keys():
            aa_eq(data[key][1], na2[key][1])

if __name__ == "__main__":
    unittest.main()