from __future__ import absolute_import
from pytraj._get_common_objects import _get_topology, _get_data_from_dtype
from pytraj.decorators import _register_pmap, _register_openmp
from pytraj._get_common_objects import _super_dispatch
from pytraj.analyses import CpptrajAnalyses
from pytraj.datasets.DatasetList import DatasetList as CpptrajDatasetList


@_super_dispatch()
@_register_openmp
def kmeans(traj=None,
           mask='*',
           n_clusters=10,
           random_point=True,
           kseed=1,
           maxit=100,
           metric='rms',
           top=None,
           frame_indices=None,
           options=''):
    '''perform clustering and return cluster index for each frame

    Parameters
    ----------
    traj : Trajectory-like or iterable that produces Frame
    mask : str, default: * (all atoms)
    n_clusters: int, default: 10
    random_point : bool, default: True
    maxit : int, default: 100
        max iterations
    metric : str, {'rms', 'dme'}
        distance metric
    top : Topology, optional, default: None
        only need to provide this Topology if ``traj`` does not have one
    frame_indices : {None, 1D array-like}, optional
        if not None, only perform clustering for given indices. Notes that this is
        different from ``sieve`` keywords.
    options : str, optional
        extra cpptraj options controlling output, sieve, ...

    Sieve options::

        [sieve <#> [random [sieveseed <#>]]]
      
    Output options::

        [out <cnumvtime>] [gracecolor] [summary <summaryfile>] [info <infofile>]
        [summarysplit <splitfile>] [splitframe <comma-separated frame list>]
        [clustersvtime <filename> cvtwindow <window size>]
        [cpopvtime <file> [normpop | normframe]] [lifetime]
        [sil <silhouette file prefix>]

    Coordinate output options::

        [ clusterout <trajfileprefix> [clusterfmt <trajformat>] ]
        [ singlerepout <trajfilename> [singlerepfmt <trajformat>] ]
        [ repout <repprefix> [repfmt <repfmt>] [repframe] ]
        [ avgout <avgprefix> [avgfmt <avgfmt>] ]

    Notes
    -----
    - if the distance matrix is large (get memory Error), should add sieve number to
    ``options`` (check example)
    - install ``libcpptraj`` with ``-openmp`` flag to speed up this calculation.

    Returns
    -------
    1D numpy array of frame indices

    Examples
    --------
    >>> import pytraj as pt
    >>> from pytraj.cluster import kmeans
    >>> traj = pt.datafiles.load_tz2()
    >>> # use default options
    >>> kmeans(traj)
    array([8, 8, 6, ..., 0, 0, 0], dtype=int32)
    >>> # update n_clusters
    >>> data = kmeans(traj, n_clusters=5)
    >>> # update n_clusters with CA atoms
    >>> data = kmeans(traj, n_clusters=5, mask='@CA')
    >>> # specify distance metric
    >>> data = kmeans(traj, n_clusters=5, mask='@CA', kseed=100, metric='dme')
    >>> # add sieve number for less memory
    >>> data = kmeans(traj, n_clusters=5, mask='@CA', kseed=100, metric='rms', options='sieve 5')
    >>> # add sieve number for less memory, and specify random seed for sieve
    >>> data = kmeans(traj, n_clusters=5, mask='@CA', kseed=100, metric='rms', options='sieve 5 sieveseed 1')
    '''

    # don't need to _get_topology
    _clusters = 'kmeans clusters ' + str(n_clusters)
    _random_point = 'randompoint' if random_point else ''
    _kseed = 'kseed ' + str(kseed)
    _maxit = str(maxit)
    _metric = metric
    _mask = mask
    # turn of cpptraj's cluster info
    _output = options
    command = ' '.join((_clusters, _random_point, _kseed, _maxit, _metric,
                        _mask, _output))
    return _cluster(traj, command, top=top, dtype='ndarray')


def _cluster(traj=None, command="", top=None, dtype='dataset', *args, **kwd):
    """clustering

    Parameters
    ----------
    traj : Trajectory-like or any iterable that produces Frame
    command : cpptraj command
    top : Topology, optional
    *args, **kwd: optional arguments

    Notes
    -----
    Supported algorithms: kmeans, hieragglo, and dbscan.
    """
    _top = _get_topology(traj, top)
    ana = CpptrajAnalyses.Analysis_Clustering()
    # need to creat `dslist` here so that every time `do_clustering` is called,
    # we will get a fresh one (or will get segfault)
    dslist = CpptrajDatasetList()

    dname = 'DEFAULT_NAME'
    if traj is not None:
        dslist.add_set("coords", name=dname)
        dslist[0].top = _top
        for frame in traj:
            # dslist[-1].add_frame(frame)
            dslist[0].add_frame(frame)
        command += " crdset {0}".format(dname)
    else:
        pass
    # do not output cluster info to STDOUT
    command = command + ' noinfo'
    ana(command, _top, dslist, *args, **kwd)
    # remove frames in dslist to save memory
    dslist.remove_set(dslist[dname])
    return _get_data_from_dtype(dslist, dtype=dtype)
