#!/usr/bin/env python3
"""
Real-Time Bounty Activity Signal System
Bounty Issue #224

A real-time monitoring system that detects and signals bounty activity patterns.
"""

import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class SignalType(Enum):
    """Types of bounty activity signals"""
    HIGH_ACTIVITY = "high_activity"
    LOW_ACTIVITY = "low_activity"
    TRENDING = "trending"
    STALE = "stale"
    URGE = "urge"
    COMPLETION = "completion"

class SignalStrength(Enum):
    """Signal strength levels"""
    WEAK = 1
    MODERATE = 2
    STRONG = 3
    CRITICAL = 4

@dataclass
class BountySignal:
    """Represents a bounty activity signal"""
    signal_type: SignalType
    strength: SignalStrength
    timestamp: datetime
    score: float
    details: Dict
    recommendations: List[str]

class BountyActivityAnalyzer:
    """Analyzes bounty activity and generates real-time signals"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {
            'high_activity_threshold': 10,  # tasks/hour
            'low_activity_threshold': 2,     # tasks/hour
            'trending_threshold': 5,         # % increase
            'stale_threshold_hours': 24,      # hours without activity
            'urge_threshold': 0.7,           # completion rate
        }
        self.activity_history: List[Dict] = []
        self.signals: List[BountySignal] = []

    def record_activity(self, activity: Dict) -> None:
        """Record a bounty activity event"""
        activity['timestamp'] = datetime.now().isoformat()
        self.activity_history.append(activity)
        
        # Keep only last 1000 activities
        if len(self.activity_history) > 1000:
            self.activity_history = self.activity_history[-1000:]

    def analyze_patterns(self, time_window_hours: int = 24) -> List[BountySignal]:
        """Analyze activity patterns and generate signals"""
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
        
        recent_activities = [
            a for a in self.activity_history
            if datetime.fromisoformat(a['timestamp']) >= cutoff_time
        ]

        signals = []

        # High Activity Signal
        activity_rate = len(recent_activities) / time_window_hours
        if activity_rate >= self.config['high_activity_threshold']:
            signals.append(self._generate_high_activity_signal(
                activity_rate, recent_activities
            ))

        # Low Activity Signal
        elif activity_rate <= self.config['low_activity_threshold']:
            signals.append(self._generate_low_activity_signal(
                activity_rate, recent_activities
            ))

        # Trending Signal
        if self._is_trending(recent_activities):
            signals.append(self._generate_trending_signal(recent_activities))

        # Stale Signal
        if self._is_stale(recent_activities):
            signals.append(self._generate_stale_signal())

        # Urge Signal (high priority tasks pending)
        urge_signal = self._check_urge_signal(recent_activities)
        if urge_signal:
            signals.append(urge_signal)

        # Completion Signal
        if self._check_completion_spike(recent_activities):
            signals.append(self._generate_completion_signal(recent_activities))

        self.signals.extend(signals)
        return signals

    def _generate_high_activity_signal(self, rate: float, activities: List[Dict]) -> BountySignal:
        """Generate high activity signal"""
        strength = SignalStrength.CRITICAL if rate > 20 else SignalStrength.STRONG
        
        return BountySignal(
            signal_type=SignalType.HIGH_ACTIVITY,
            strength=strength,
            timestamp=datetime.now(),
            score=rate / 10.0,  # Normalize to 0-10
            details={
                'activity_rate': rate,
                'total_activities': len(activities),
                'top_contributors': self._get_top_contributors(activities),
                'activity_types': self._categorize_activities(activities),
            },
            recommendations=[
                f"Activity rate: {rate:.1f} tasks/hour - Consider scaling resources",
                "Review task queue for bottlenecks",
                "Monitor system performance",
            ]
        )

    def _generate_low_activity_signal(self, rate: float, activities: List[Dict]) -> BountySignal:
        """Generate low activity signal"""
        return BountySignal(
            signal_type=SignalType.LOW_ACTIVITY,
            strength=SignalStrength.MODERATE,
            timestamp=datetime.now(),
            score=rate,
            details={
                'activity_rate': rate,
                'last_activity': activities[-1] if activities else None,
                'idle_hours': self._calculate_idle_hours(activities),
            },
            recommendations=[
                f"Low activity detected: {rate:.1f} tasks/hour",
                "Check for blockers or system issues",
                "Review task assignment strategy",
                "Consider outreach to contributors",
            ]
        )

    def _generate_trending_signal(self, activities: List[Dict]) -> BountySignal:
        """Generate trending signal"""
        growth_rate = self._calculate_growth_rate(activities)
        
        return BountySignal(
            signal_type=SignalType.TRENDING,
            strength=SignalStrength.STRONG,
            timestamp=datetime.now(),
            score=growth_rate,
            details={
                'growth_rate': growth_rate,
                'trending_categories': self._get_trending_categories(activities),
                'hot_tasks': self._get_hot_tasks(activities),
            },
            recommendations=[
                f"Trending upward: +{growth_rate:.1f}% growth",
                "Focus on high-demand categories",
                "Allocate more resources to trending tasks",
                "Share success metrics with community",
            ]
        )

    def _generate_stale_signal(self) -> BountySignal:
        """Generate stale signal"""
        return BountySignal(
            signal_type=SignalType.STALE,
            strength=SignalStrength.CRITICAL,
            timestamp=datetime.now(),
            score=0.0,
            details={
                'stale_duration_hours': self.config['stale_threshold_hours'],
                'last_activity': None,
            },
            recommendations=[
                "CRITICAL: No activity detected in 24+ hours",
                "Immediate investigation required",
                "Check system health and connectivity",
                "Review blocker issues",
                "Consider manual intervention",
            ]
        )

    def _check_urge_signal(self, activities: List[Dict]) -> Optional[BountySignal]:
        """Check for urge signal (high priority pending)"""
        pending_high_priority = [
            a for a in activities
            if a.get('priority') == 'high' and a.get('status') == 'pending'
        ]
        
        if not pending_high_priority:
            return None
        
        pending_rate = len(pending_high_priority) / max(len(activities), 1)
        
        if pending_rate >= self.config['urge_threshold']:
            return BountySignal(
                signal_type=SignalType.URGE,
                strength=SignalStrength.STRONG,
                timestamp=datetime.now(),
                score=pending_rate,
                details={
                    'pending_high_priority': len(pending_high_priority),
                    'pending_rate': pending_rate,
                    'oldest_pending': self._get_oldest_pending(pending_high_priority),
                },
                recommendations=[
                    f"URGE: {len(pending_high_priority)} high-priority tasks pending",
                    "Prioritize high-value tasks immediately",
                    "Assign additional resources if needed",
                    "Set aggressive deadlines",
                ]
            )
        
        return None

    def _generate_completion_signal(self, activities: List[Dict]) -> BountySignal:
        """Generate completion signal"""
        completed = [a for a in activities if a.get('status') == 'completed']
        
        return BountySignal(
            signal_type=SignalType.COMPLETION,
            strength=SignalStrength.MODERATE,
            timestamp=datetime.now(),
            score=len(completed),
            details={
                'completed_count': len(completed),
                'completion_rate': len(completed) / max(len(activities), 1),
                'top_completers': self._get_top_completers(completed),
                'avg_completion_time': self._calculate_avg_completion_time(completed),
            },
            recommendations=[
                f"Completion spike detected: {len(completed)} tasks completed",
                "Celebrate and recognize contributors",
                "Document successful patterns",
                "Review and merge pending PRs",
            ]
        )

    def _is_trending(self, activities: List[Dict]) -> bool:
        """Check if activity is trending upward"""
        if len(activities) < 10:
            return False
        
        growth_rate = self._calculate_growth_rate(activities)
        return growth_rate >= self.config['trending_threshold']

    def _is_stale(self, activities: List[Dict]) -> bool:
        """Check if activity is stale"""
        if not activities:
            return True
        
        last_activity_time = datetime.fromisoformat(activities[-1]['timestamp'])
        hours_since_last = (datetime.now() - last_activity_time).total_seconds() / 3600
        
        return hours_since_last >= self.config['stale_threshold_hours']

    def _check_completion_spike(self, activities: List[Dict]) -> bool:
        """Check for completion spike"""
        completed = [a for a in activities if a.get('status') == 'completed']
        return len(completed) >= 5  # Threshold for "spike"

    def _calculate_growth_rate(self, activities: List[Dict]) -> float:
        """Calculate growth rate of activities"""
        if len(activities) < 20:
            return 0.0
        
        midpoint = len(activities) // 2
        first_half = activities[:midpoint]
        second_half = activities[midpoint:]
        
        if not first_half:
            return 0.0
        
        growth = (len(second_half) - len(first_half)) / len(first_half) * 100
        return growth

    def _calculate_idle_hours(self, activities: List[Dict]) -> float:
        """Calculate idle hours since last activity"""
        if not activities:
            return 24.0
        
        last_time = datetime.fromisoformat(activities[-1]['timestamp'])
        return (datetime.now() - last_time).total_seconds() / 3600

    def _get_top_contributors(self, activities: List[Dict]) -> List[Dict]:
        """Get top contributors"""
        contributor_counts = {}
        for a in activities:
            contributor = a.get('contributor', 'unknown')
            contributor_counts[contributor] = contributor_counts.get(contributor, 0) + 1
        
        sorted_contributors = sorted(
            contributor_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return [{'contributor': c, 'count': count} for c, count in sorted_contributors]

    def _categorize_activities(self, activities: List[Dict]) -> Dict[str, int]:
        """Categorize activities by type"""
        categories = {}
        for a in activities:
            category = a.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
        return categories

    def _get_trending_categories(self, activities: List[Dict]) -> List[str]:
        """Get trending categories"""
        categories = self._categorize_activities(activities)
        sorted_categories = sorted(
            categories.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        return [cat for cat, count in sorted_categories]

    def _get_hot_tasks(self, activities: List[Dict]) -> List[Dict]:
        """Get hot tasks (most active)"""
        task_activity = {}
        for a in activities:
            task_id = a.get('task_id')
            if task_id:
                task_activity[task_id] = task_activity.get(task_id, 0) + 1
        
        hot_tasks = sorted(
            task_activity.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return [{'task_id': tid, 'activity_count': count} for tid, count in hot_tasks]

    def _get_oldest_pending(self, activities: List[Dict]) -> Optional[Dict]:
        """Get oldest pending high-priority task"""
        pending = [a for a in activities if a.get('status') == 'pending']
        if not pending:
            return None
        
        oldest = min(pending, key=lambda a: a.get('created_at', ''))
        return oldest

    def _get_top_completers(self, completed_activities: List[Dict]) -> List[Dict]:
        """Get top completers"""
        completer_counts = {}
        for a in completed_activities:
            completer = a.get('completer', 'unknown')
            completer_counts[completer] = completer_counts.get(completer, 0) + 1
        
        sorted_completers = sorted(
            completer_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return [{'completer': c, 'count': count} for c, count in sorted_completers]

    def _calculate_avg_completion_time(self, completed_activities: List[Dict]) -> float:
        """Calculate average completion time in hours"""
        if not completed_activities:
            return 0.0
        
        total_hours = 0.0
        count = 0
        
        for a in completed_activities:
            created = a.get('created_at')
            completed = a.get('completed_at')
            
            if created and completed:
                created_time = datetime.fromisoformat(created)
                completed_time = datetime.fromisoformat(completed)
                hours = (completed_time - created_time).total_seconds() / 3600
                total_hours += hours
                count += 1
        
        return total_hours / max(count, 1)

    def get_signals(self, limit: int = 10) -> List[Dict]:
        """Get recent signals as dictionaries"""
        recent_signals = self.signals[-limit:]
        return [asdict(s) for s in recent_signals]

    def export_signals(self, file_path: str) -> None:
        """Export signals to JSON file"""
        signals_data = self.get_signals(limit=100)
        
        with open(file_path, 'w') as f:
            json.dump(signals_data, f, indent=2, default=str)


def main():
    """Demo usage"""
    analyzer = BountyActivityAnalyzer()
    
    # Simulate some activities
    activities = [
        {'task_id': 1, 'contributor': 'alice', 'category': 'security', 'status': 'completed'},
        {'task_id': 2, 'contributor': 'bob', 'category': 'feature', 'status': 'pending', 'priority': 'high'},
        {'task_id': 3, 'contributor': 'alice', 'category': 'security', 'status': 'in_progress'},
        {'task_id': 4, 'contributor': 'charlie', 'category': 'docs', 'status': 'completed'},
        {'task_id': 5, 'contributor': 'bob', 'category': 'feature', 'status': 'pending', 'priority': 'high'},
    ]
    
    for activity in activities:
        analyzer.record_activity(activity)
    
    # Analyze patterns
    signals = analyzer.analyze_patterns(time_window_hours=1)
    
    print("=== Real-Time Bounty Activity Signals ===\n")
    for signal in signals:
        print(f"Signal: {signal.signal_type.value}")
        print(f"Strength: {signal.strength.name}")
        print(f"Score: {signal.score:.2f}")
        print(f"Recommendations:")
        for rec in signal.recommendations:
            print(f"  • {rec}")
        print()


if __name__ == '__main__':
    main()
