from __future__ import print_function
import unittest
from pytraj.base import *
from pytraj import adict
from pytraj import io as mdio
from pytraj.utils import eq, aa_eq, Timer
from pytraj.decorators import no_test, test_if_having, test_if_path_exists
from pytraj.testing import cpptraj_test_dir 
import pytraj.common_actions as pyca

class Test(unittest.TestCase):
    def test_0(self):
        import numpy as np
        traj = mdio.iterload("./data/md1_prod.Tc5b.x", "./data/Tc5b.top")
        fa = traj[:]
        print (fa.xyz[0, :10])
        xyz = fa.xyz / 10.
        fa.update_xyz(xyz)
        aa_eq(xyz, fa.xyz)
        print (fa.xyz[0, :10], xyz[0, :10])

        # try to build Trajectory from scratch
        fa2 = Trajectory()
        fa2.top = fa.top
        fa2._allocate(traj.n_frames, traj.n_atoms)
        fa2.update_xyz (traj.xyz)
        aa_eq(fa2.xyz, traj.xyz)

        # timing
        xyz0 = np.empty((traj.n_frames, traj.n_atoms, 3))
        @Timer()
        def update_np():
            xyz0[:] = xyz[:]

        @Timer()
        def update_pytraj():
            fa2.update_xyz(xyz)

        print ("numpy")
        update_np()
        print ("pytraj")
        update_pytraj()

if __name__ == "__main__":
    unittest.main()