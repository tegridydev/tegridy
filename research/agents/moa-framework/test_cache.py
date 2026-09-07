from orchestrator import Cache


def test_cache_scope_expiry_and_restart(tmp_path):
    path=tmp_path/'cache.sqlite';cache=Cache(path)
    request={'model':'a','prompt':'x','policy':1};cache.put(request,{'text':'saved'},100,10);cache.close()
    cache=Cache(path)
    assert cache.get(request,109)=={'text':'saved'}
    assert cache.get(dict(request,model='b'),109) is None
    assert cache.get(request,110) is None
    cache.close()
