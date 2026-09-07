from cedar import fixture, select


def test_five_applicability_cases_and_equal_metadata():
    data = fixture()
    assert [p["id"] for p in data["new"]["selected"]] == ["r2"]
    assert [p["id"] for p in data["upgraded"]["selected"]] == ["migration"]
    assert [p["id"] for p in data["historical"]["selected"]] == ["r1"]
    assert (
        data["unspecified"]["status"] == "needs-scope"
        and data["unsupported"]["status"] == "unsupported"
    )
    assert select(graph=True)["selected"] == select(graph=False)["selected"]
    assert not select(budget=0)["selected"]


def test_graph_can_reach_noninitial_applicable_evidence():
    from cedar import retrieve
    sources={'a':{'text':'lookup','release':'1'},'b':{'text':'qualification','release':'1'},'c':{'text':'wrong release','release':'2'}}
    edges=[{'source':'a','target':target,'reviewed':True,'reason':'fixture relation'} for target in ['b','c']]
    result=retrieve(sources,edges,'lookup',{'release':'1'},initial_limit=1)
    assert result['selected']==['a','b']
    assert retrieve(sources,edges,'lookup',{'release':'1'},initial_limit=1,max_hops=0)['selected']==['a']
