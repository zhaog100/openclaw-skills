#!/usr/bin/env python3
"""
Test Suite for Real-Time Bounty Activity Signal System
"""

import pytest
from datetime import datetime, timedelta
from activity_signal import (
    BountyActivityAnalyzer,
    BountySignal,
    SignalType,
    SignalStrength
)


def test_initialization():
    """Test analyzer initialization"""
    analyzer = BountyActivityAnalyzer()
    assert analyzer.activity_history == []
    assert analyzer.signals == []
    assert analyzer.config is not None


def test_custom_config():
    """Test custom configuration"""
    custom_config = {
        'high_activity_threshold': 20,
        'low_activity_threshold': 5,
    }
    
    analyzer = BountyActivityAnalyzer(config=custom_config)
    assert analyzer.config['high_activity_threshold'] == 20
    assert analyzer.config['low_activity_threshold'] == 5


def test_record_activity():
    """Test recording activities"""
    analyzer = BountyActivityAnalyzer()
    
    activity = {
        'task_id': 1,
        'contributor': 'alice',
        'category': 'security',
        'status': 'completed'
    }
    
    analyzer.record_activity(activity)
    
    assert len(analyzer.activity_history) == 1
    assert 'timestamp' in analyzer.activity_history[0]


def test_high_activity_signal():
    """Test high activity detection"""
    analyzer = BountyActivityAnalyzer()
    
    # Simulate high activity (15 tasks in 1 hour)
    for i in range(15):
        analyzer.record_activity({
            'task_id': i,
            'contributor': 'user',
            'category': 'test',
            'status': 'completed'
        })
    
    signals = analyzer.analyze_patterns(time_window_hours=1)
    
    high_activity_signals = [
        s for s in signals
        if s.signal_type == SignalType.HIGH_ACTIVITY
    ]
    
    assert len(high_activity_signals) > 0
    assert high_activity_signals[0].strength in [SignalStrength.STRONG, SignalStrength.CRITICAL]


def test_low_activity_signal():
    """Test low activity detection"""
    analyzer = BountyActivityAnalyzer()
    
    # Simulate low activity (1 task in 24 hours)
    analyzer.record_activity({
        'task_id': 1,
        'contributor': 'user',
        'category': 'test',
        'status': 'completed'
    })
    
    signals = analyzer.analyze_patterns(time_window_hours=24)
    
    low_activity_signals = [
        s for s in signals
        if s.signal_type == SignalType.LOW_ACTIVITY
    ]
    
    assert len(low_activity_signals) > 0


def test_stale_signal():
    """Test stale detection"""
    analyzer = BountyActivityAnalyzer()
    
    # Simulate old activity
    old_time = datetime.now() - timedelta(hours=30)
    analyzer.activity_history = [{
        'task_id': 1,
        'contributor': 'user',
        'category': 'test',
        'status': 'completed',
        'timestamp': old_time.isoformat()
    }]
    
    signals = analyzer.analyze_patterns(time_window_hours=24)
    
    stale_signals = [
        s for s in signals
        if s.signal_type == SignalType.STALE
    ]
    
    assert len(stale_signals) > 0
    assert stale_signals[0].strength == SignalStrength.CRITICAL


def test_urge_signal():
    """Test urge detection (high priority pending)"""
    analyzer = BountyActivityAnalyzer()
    
    # Simulate activities with high priority pending
    for i in range(10):
        analyzer.record_activity({
            'task_id': i,
            'contributor': 'user',
            'category': 'test',
            'status': 'pending',
            'priority': 'high'
        })
    
    signals = analyzer.analyze_patterns(time_window_hours=1)
    
    urge_signals = [
        s for s in signals
        if s.signal_type == SignalType.URGE
    ]
    
    assert len(urge_signals) > 0


def test_completion_signal():
    """Test completion spike detection"""
    analyzer = BountyActivityAnalyzer()
    
    # Simulate completion spike
    for i in range(10):
        analyzer.record_activity({
            'task_id': i,
            'contributor': 'user',
            'category': 'test',
            'status': 'completed'
        })
    
    signals = analyzer.analyze_patterns(time_window_hours=1)
    
    completion_signals = [
        s for s in signals
        if s.signal_type == SignalType.COMPLETION
    ]
    
    assert len(completion_signals) > 0


def test_signal_recommendations():
    """Test that signals have recommendations"""
    analyzer = BountyActivityAnalyzer()
    
    analyzer.record_activity({
        'task_id': 1,
        'contributor': 'user',
        'category': 'test',
        'status': 'completed'
    })
    
    signals = analyzer.analyze_patterns(time_window_hours=24)
    
    assert len(signals) > 0
    for signal in signals:
        assert len(signal.recommendations) > 0
        assert isinstance(signal.recommendations, list)


def test_get_signals():
    """Test retrieving signals"""
    analyzer = BountyActivityAnalyzer()
    
    analyzer.record_activity({
        'task_id': 1,
        'contributor': 'user',
        'category': 'test',
        'status': 'completed'
    })
    
    analyzer.analyze_patterns(time_window_hours=24)
    
    signals = analyzer.get_signals(limit=10)
    
    assert isinstance(signals, list)
    assert len(signals) <= 10


def test_export_signals():
    """Test exporting signals to file"""
    import tempfile
    import os
    
    analyzer = BountyActivityAnalyzer()
    
    analyzer.record_activity({
        'task_id': 1,
        'contributor': 'user',
        'category': 'test',
        'status': 'completed'
    })
    
    analyzer.analyze_patterns(time_window_hours=24)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name
    
    try:
        analyzer.export_signals(temp_path)
        
        assert os.path.exists(temp_path)
        
        with open(temp_path, 'r') as f:
            import json
            data = json.load(f)
            assert isinstance(data, list)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_top_contributors():
    """Test top contributors tracking"""
    analyzer = BountyActivityAnalyzer()
    
    # Record activities with different contributors
    for i in range(5):
        analyzer.record_activity({
            'task_id': i,
            'contributor': 'alice',
            'category': 'test',
            'status': 'completed'
        })
    
    for i in range(3):
        analyzer.record_activity({
            'task_id': i + 5,
            'contributor': 'bob',
            'category': 'test',
            'status': 'completed'
        })
    
    signals = analyzer.analyze_patterns(time_window_hours=1)
    
    high_activity_signals = [
        s for s in signals
        if s.signal_type == SignalType.HIGH_ACTIVITY
    ]
    
    if high_activity_signals:
        top_contributors = high_activity_signals[0].details.get('top_contributors', [])
        assert len(top_contributors) > 0
        assert top_contributors[0]['contributor'] == 'alice'


def test_activity_categorization():
    """Test activity categorization"""
    analyzer = BountyActivityAnalyzer()
    
    categories = ['security', 'feature', 'docs', 'security', 'feature']
    
    for i, cat in enumerate(categories):
        analyzer.record_activity({
            'task_id': i,
            'contributor': 'user',
            'category': cat,
            'status': 'completed'
        })
    
    signals = analyzer.analyze_patterns(time_window_hours=1)
    
    high_activity_signals = [
        s for s in signals
        if s.signal_type == SignalType.HIGH_ACTIVITY
    ]
    
    if high_activity_signals:
        activity_types = high_activity_signals[0].details.get('activity_types', {})
        assert 'security' in activity_types
        assert activity_types['security'] == 2


def test_concurrent_activities():
    """Test handling of concurrent activities"""
    analyzer = BountyActivityAnalyzer()
    
    # Record many activities quickly
    import threading
    
    def record_activity(i):
        analyzer.record_activity({
            'task_id': i,
            'contributor': f'user_{i}',
            'category': 'test',
            'status': 'completed'
        })
    
    threads = []
    for i in range(50):
        t = threading.Thread(target=record_activity, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    assert len(analyzer.activity_history) == 50


def test_activity_history_limit():
    """Test that activity history is limited to 1000 items"""
    analyzer = BountyActivityAnalyzer()
    
    # Record more than 1000 activities
    for i in range(1500):
        analyzer.record_activity({
            'task_id': i,
            'contributor': 'user',
            'category': 'test',
            'status': 'completed'
        })
    
    assert len(analyzer.activity_history) == 1000


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
