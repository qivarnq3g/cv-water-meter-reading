from wmr.analysis import summarize

def test_summary_counts_wraparound_errors_and_empty_tiers():
    rows=[dict(method='p',tier='heavy',reading='00009',prediction='00000'),
          dict(method='p',tier='heavy',reading='00001',prediction='00007')]
    results={r['tier']:r for r in summarize(rows)}
    assert results['heavy']['n']==2
    assert results['heavy']['adjacent_fraction']==0.5
    assert results['heavy']['first4']==1
    assert results['heavy']['full']==0
    assert results['light']['n']==0
