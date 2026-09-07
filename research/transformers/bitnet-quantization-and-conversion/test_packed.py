import pytest
from packed import save,load,matvec


def test_complete_packed_matrix_and_corruption(tmp_path):
    path=tmp_path/'matrix.tern';save(path,[1,0,-1,-1,1,0],(2,3),.5)
    header,payload=load(path)
    assert matvec(header,payload,[2.,3.,4.])==[-1.,.5]
    with pytest.raises(FileExistsError):save(path,[1],(1,1),1.)
    with pytest.raises(ValueError):matvec(header,payload,[1.])
    path.write_bytes(b'corrupt')
    with pytest.raises(ValueError):load(path)
