# distutils: language = c++
from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as incr

# python level
from pytraj.cast_dataset import cast_dataset

# can not import cpptraj_dict here
# if doing this, we introduce circle-import since cpptraj_dict already imported
# DataSet
from pytraj.cpptraj_dict import DataTypeDict

cdef class DataSetList:
    def __cinit__(self, py_free_mem=True):
        # py_free_mem is a flag to tell pytraj should free memory or let 
        # cpptraj does
        # check ./CpptrajState.pyx
        self.thisptr = new _DataSetList()
        self.py_free_mem = py_free_mem

    def __dealloc__(self):
        if self.py_free_mem:
            del self.thisptr

    def clear(self):
        self.thisptr.Clear()

    def __iadd__(self, DataSetList other):
        self.thisptr.addequal(other.thisptr[0])
        return self

    def __iter__(self):
        cdef const_iterator it
        cdef DataSet dtset
        it = self.thisptr.begin()

        while it != self.thisptr.end():
            dtset = DataSet()
            dtset.baseptr0 = deref(it)
            yield dtset
            incr(it)

    def __len__(self):
        cdef const_iterator it
        cdef DataSet dtset
        cdef int i
        it = self.thisptr.begin()

        i = 0
        while it != self.thisptr.end():
            i += 1
            incr(it)
        return i

    def len(self):
        return self.__len__()
            
    def is_empty(self):
        return self.thisptr.empty()

    property size:
        def __get__(self):
            return self.thisptr.size()

    def ensemble_num(self):
        return self.thisptr.EnsembleNum()

    def remove_set(self, DataSet dtset):
        self.thisptr.RemoveSet(dtset.baseptr0)

    def __getitem__(self, int idx):
        """return a DataSet instance
        Memory view is applied (which mean this new insance is just alias of self[idx])
        Should we use a copy instead?
        """
        cdef DataSet dset = DataSet()
        if idx >= len(self):
            raise ValueError("index is out of range")
        # get memoryview
        dset.baseptr0 = self.thisptr.index_opr(idx)
        return cast_dataset(dset, dtype=dset.dtype)

    def set_ensemble_num(self,int i):
        self.thisptr.SetEnsembleNum(i)

    def allocate_sets(self,long int i):
        self.thisptr.AllocateSets(i)

    def set_precision_of_data_sets(self, string nameIn, int widthIn, int precisionIn):
        self.thisptr.SetPrecisionOfDataSets(nameIn, widthIn, precisionIn)

    def get_set(self, string dsname, int idx, string attr_arg):
        cdef DataSet dset = DataSet()
        dset.baseptr0 = self.thisptr.GetSet(dsname, idx, attr_arg)

    def get_dataset(self, idx=None, name=None):
        """
        return DataSet instance
        Input:
        =====
        name :: str, optional
        idx :: integer, optional
        """
        cdef DataSet dset = DataSet()

        if name is not None and idx is not None:
            raise ValueError("name and idx must not be set at the same time")
        else:
            if name is not None:
                name = name.encode()
                dset.baseptr0 = self.thisptr.GetDataSet(name)
            if idx is not None:
                dset.baseptr0 = self.thisptr.index_opr(idx)
            return dset

    def get_multiple_sets(self, string s):
        """TODO: double-check cpptraj"""
        cdef DataSetList dlist = DataSetList()
        dlist.thisptr[0] = self.thisptr.GetMultipleSets(s)
        return dlist

    def add_set(self, DataType dtype, string s, char * c):
        # TODO: check cpptraj for this method
        cdef DataSet dset = DataSet()
        dset.baseptr0 = self.thisptr.AddSet(dtype, s, c)
        return dset
        
    def add_setidx(self, DataType inType, string nameIn, int idx):
        cdef DataSet dset = DataSet()
        dset.baseptr0 = self.thisptr.AddSetIdx(inType, nameIn, idx)
        if not dset.baseptr0:
            raise MemoryError("Can not initialize pointer")
        return dset

    def add_copy_of_set(self, DataSet dset):
        self.thisptr.AddCopyOfSet(dset.baseptr0)

    def printlist(self):
        self.thisptr.List()

    def find_coords_set(self, string filename):
        cdef DataSet dtset = DataSet()
        dtset.baseptr0 = self.thisptr.FindCoordsSet(filename)
        if not dtset.baseptr0:
            raise MemoryError("Can not initialize pointer")
        return dtset
