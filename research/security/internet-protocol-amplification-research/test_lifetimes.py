import pytest
from budgets import simulate_lifetimes


def test_deadline_boundary_releases_capacity_and_accounts_for_every_job():
    jobs=[dict(id='a',arrival=0,duration=None),dict(id='b',arrival=1,duration=1),dict(id='c',arrival=5,duration=1)]
    result=simulate_lifetimes(jobs,capacity=1,deadline=5,work_budget=2)
    assert [r['status'] for r in result['ledger']]==['expired','rejected','completed']
    assert result['peak_active']==1 and result['charged_work']==2
    assert result['remaining_after_final_deadline']==0
    with pytest.raises(ValueError):simulate_lifetimes([jobs[0],jobs[0]])
