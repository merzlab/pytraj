from __future__ import absolute_import
from .externals.six import string_types, PY3
from .base import *
from .TrajReadOnly import TrajReadOnly
from .FrameArray import FrameArray
from .Topology import Topology
from .utils.check_and_assert import make_sure_exist
from .load_HD5F import load_hd5f
from .load_cpptraj_file import load_cpptraj_file
from ._shared_methods import _frame_iter_master
from .dataframe import to_dataframe
from ._set_silent import set_error_silent

try:
    from .externals._load_ParmEd import load_ParmEd
except:
    load_ParmEd = None

try:
    from pytraj.externals._load_pseudo_parm import load_pseudo_parm
except:
    load_pseudo_parm = None

# load mdtraj and MDAnalysis
from .externals._load_mdtraj import load_mdtraj 
from .externals._load_MDAnalysis import load_MDAnalysis

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

__all__ = ['load', 'load_hd5f', 'write_traj', 'read_parm', 'write_parm', 'save']

def load(*args, **kwd):
    """try loading and returning appropriate values"""

    if 'filename' in kwd.keys():
        make_sure_exist(kwd['filename'])
    else:
        make_sure_exist(args[0])

    if len(args) + len(kwd) == 1:
        # loading only Topology
        return readparm(*args, **kwd)
    else:
        # load traj
        return loadtraj(*args, **kwd)

def loadtraj(filename=None, top=Topology(), indices=None):
    """load trajectory from filename
    Parameters
    ----------
    filename : str
    top : {str, Topology}
    indices : {None, list, array ...}

    Returns
    -------
    TrajReadOnly : if indices is None
    or 
    FrameArray : if there is indices
    """
    if not isinstance(top, Topology):
        top = Topology(top)
    ts = TrajReadOnly()
    ts.load(filename, top)

    if indices is not None:
        farray = FrameArray()
        farray.top = top.copy()
        for i in indices:
            farray.append(ts[i])
        return farray
    else:
        return ts

def load_remd(filename, top=Topology(), T="300.0"):
    """Load remd trajectory for single temperature.
    Example: Suppose you have replica trajectoris remd.x.00{1-4}. 
    You want to load and extract only frames at 300 K, use this "load_remd" method

    Parameters
    ----------
    filename : str
    top : {str, Topology objecd}
    T : {int, float, str}, defaul="300.0"

    Returns
    ------
    TrajReadOnly object
    """
    from pytraj import CpptrajState

    state = CpptrajState()
    # add keyword 'remdtraj' to trick cpptraj
    trajin = filename + ' remdtraj remdtrajtemp ' + str(T)
    state.toplist.add_parm(top)

    # load trajin, add "is_ensemble = False" to trick cpptraj
    # is_ensemble has 3 values: None, False and True
    state.add_trajin(trajin, is_ensemble=False)
    traj = state.get_trajinlist()[0]
    traj.top = state.toplist[0].copy()

    # use _tmpobj to hold CpptrajState(). If not, cpptraj will free memory
    traj._tmpobj = state
    return traj

def writetraj(filename="", traj=None, top=None, 
              fmt='UNKNOWN_TRAJ', indices=None,
              overwrite=False):
    """writetraj(filename="", traj=None, top=None, 
              ftm='UNKNOWN_TRAJ', indices=None):
    """
    # TODO : support list (tuple) of FrameArray, TrajReadOnly or 
    # list of filenames
    #filename = filename.encode("UTF-8")

    if fmt == 'unknown':
        fmt = fmt.upper() + "_TRAJ"
    else:
        fmt = fmt.upper()

    if isinstance(top, string_types):
        top = Topology(top)

    if traj is None or top is None:
        raise ValueError("Need non-empty traj and top files")

    with Trajout(filename=filename, top=top, fmt=fmt, overwrite=overwrite) as trajout:
        if isinstance(traj, Frame):
            if indices is not None:
                raise ValueError("indices does not work with single Frame")
            trajout.writeframe(0, traj, top)
        else:
            if isinstance(traj, string_types):
                traj2 = load(traj, top)
            else:
                traj2 = traj

            if indices is None:
                # write all traj
                if isinstance(traj2, (FrameArray, TrajReadOnly)):
                    for idx, frame in enumerate(traj2):
                        trajout.writeframe(idx, frame, top)
                elif isinstance(traj2, (list, tuple)):
                    # list, tuple
                    for traj3 in traj2:
                        for idx, frame in enumerate(traj3):
                            trajout.writeframe(idx, frame, top)
            else:
                if isinstance(traj2, (list, tuple)):
                    raise NotImplementedError("must be FrameArray or TrajReadOnly instance")
                for idx in indices:
                    trajout.writeframe(idx, traj2[idx], top)


def writeparm(filename=None, top=None, fmt='AMBERPARM'):
    # TODO : add *args
    from pytraj.parms.ParmFile import ParmFile
    #filename = filename.encode("UTF-8")
    parm = ParmFile()
    parm.writeparm(filename=filename, top=top, fmt=fmt)

def readparm(filename):
    """return topology instance from reading filename"""
    #filename = filename.encode("UTF-8")
    set_error_silent(True)
    top = Topology(filename)
    set_error_silent(False)
    return top

def loadpdb_rcsb(pdbid):
    # TODO : use tempfile
    """load pdb file from rcsb website
    Return : Topology and FrameArray instance
    """

    url = 'http://www.rcsb.org/pdb/files/%s.pdb' % pdbid
    txt = urlopen(url).read()
    print ("test saving pdb")
    print (type(txt))
    with open("/tmp/._tmp", 'w') as fh:
        if PY3:
            fh.write(txt.decode())
        else:
            fh.write(txt)
    top = readparm("/tmp/._tmp")
    frames = load("/tmp/._tmp", top)
    return frames

def load_single_frame(frame=None, top=None):
    """load single Frame"""
    return load(frame, top)[0]

def load_full_ParmEd(parmed_obj):
    """save and reload ParmEd object to pytraj object"""
    import os
    import tempfile

    name = "mytmptop"
    cwd = os.getcwd()
    directory_name = tempfile.mkdtemp()
    os.chdir(directory_name)
    parmed_obj.write_parm(name)
    top = load(name)
    os.remove(name)
    os.removedirs(directory_name)
    os.chdir(cwd)
    return top

# creat alias
write_traj = writetraj
save = writetraj
save_traj = writetraj
load_traj = loadtraj
read_parm = readparm
write_parm = writeparm
