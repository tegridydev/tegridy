from inventory import inventory


def test_byte_duplicates_name_conflicts_and_symlink_exclusion(tmp_path):
    (tmp_path/'a').mkdir();(tmp_path/'b').mkdir()
    (tmp_path/'a/note.md').write_text('first')
    (tmp_path/'b/note.md').write_text('revision')
    (tmp_path/'copy.md').write_text('first')
    (tmp_path/'outside').symlink_to('/etc/passwd')
    result=inventory(tmp_path)
    assert len(result['files'])==3
    assert result['exact_duplicates'][0]['paths']==['a/note.md','copy.md']
    assert result['name_conflicts'][0]['name']=='note.md'
    assert len(result['excluded'])==1
    assert (tmp_path/'a/note.md').read_text()=='first'
