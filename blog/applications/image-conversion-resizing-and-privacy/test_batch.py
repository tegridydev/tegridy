import pytest
from PIL import Image
from batch import batch


def test_batch_preserves_sources_and_records_failures(tmp_path):
    good=tmp_path/'good.png';Image.new('RGB',(8,8)).save(good)
    original=good.read_bytes();bad=tmp_path/'bad.png';bad.write_bytes(b'not an image')
    result=batch([good,bad],tmp_path/'out',format='PNG')
    assert result['converted']==1 and result['failed']==1
    assert good.read_bytes()==original
    assert (tmp_path/'out/receipts.json').is_file()
    with pytest.raises(FileExistsError):batch([good],tmp_path/'out')
