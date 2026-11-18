import numpy as np
import pytest
from wmr.proposed import WheelConfig, WheelReader, wheel_windows
from wmr.baseline import BaselineConfig, read_meter

def templates():
    return np.random.default_rng(3).uniform(0,255,(10,60,40)).astype(np.float32)

def test_periodic_windows_recover_center_and_wrap():
    t=templates(); windows=wheel_windows(t,WheelConfig(pitch=60))
    np.testing.assert_array_equal(windows[0],t[0])
    np.testing.assert_array_equal(windows[9*60+30][:30],t[9][30:])
    np.testing.assert_array_equal(windows[9*60+30][30:],t[0][:30])

def test_phase_search_recovers_synthetic_roll(monkeypatch):
    import wmr.proposed as p
    monkeypatch.setattr(p,'preprocess',lambda x:x)
    reader=WheelReader(templates(),WheelConfig(pitch=60,max_shift=0))
    for y in (0,17,235,570,599):
        image=np.tile(reader.windows[y],(1,5))
        phase,score=reader.phase(image)
        assert phase==pytest.approx(y/60)
        assert score>0.999

def test_disabled_is_exact_baseline():
    t=templates(); im=np.random.default_rng(2).integers(0,256,(60,200),dtype=np.uint8)
    reader=WheelReader(t,WheelConfig(enabled=False))
    assert reader.read(im)==read_meter(im,t,BaselineConfig())

def test_first_four_unchanged():
    t=templates(); im=np.random.default_rng(4).integers(0,256,(60,200),dtype=np.uint8)
    reader=WheelReader(t)
    assert reader.read(im)[:4]==read_meter(im,t,BaselineConfig())[:4]

@pytest.mark.parametrize('kwargs',[{'pitch':0},{'threshold':0},{'threshold':1.1},{'max_shift':-1}])
def test_invalid_config(kwargs):
    with pytest.raises(ValueError): WheelConfig(**kwargs)

def test_discrete_phases_stay_near_digit_centers(monkeypatch):
    import wmr.proposed as p
    monkeypatch.setattr(p,'preprocess',lambda x:x)
    full=WheelReader(templates(),WheelConfig(pitch=60,max_shift=4))
    discrete=WheelReader(templates(),WheelConfig(pitch=60,max_shift=4,continuous=False))
    assert len(discrete.windows)==10*9
    image=np.tile(full.windows[150],(1,5))
    assert full.phase(image)[0]==pytest.approx(2.5)
    phase=discrete.phase(image)[0]
    assert min(abs(phase*60-k*60) for k in range(11))<=4
