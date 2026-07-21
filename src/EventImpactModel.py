"""
Task 3: Event Impact Modeling
==============================

This module models how events (policies, product launches, infrastructure) 
affect financial inclusion indicators in Ethiopia.

Key Concepts:
- Impact links encode causal relationships between events and indicators
- Event effects have a lifecycle: lag → ramp up → peak → decay
- Multiple event effects combine additively
- Estimates are validated against historical data and refined

Usage:
    
    from src.event_impact_model import EventImpactModel
    model = EventImpactModel(df, df_impact)

    # Get effect of a specific event at a specific date
    effect = model.event_effect(event_date, lag_months, impact_estimate, eval_date)

    # Get combined effect of all events on an indicator
    combined = model.combined_effect('USG_P2P_COUNT', pd.Timestamp('2025-07-01'))

    # Validate against historical data
    validation = model.validate('ACC_MM_ACCOUNT')
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')


class EventImpactModel:
    """
    Models event impacts on financial inclusion indicators.

    The model uses a functional form to represent how event effects
    unfold over time: lag → ramp up → peak → decay.
    """

    def __init__(self, df_data: pd.DataFrame, df_impact: pd.DataFrame, 
                 ramp_up_months: int = 3, decay_halflife: int = 12):
        """
        Initialize the event impact model.

        Args:
            df_data: Main dataset with observations, events, targets
            df_impact: Impact links dataset
            ramp_up_months: Months to reach full effect (default: 3)
            decay_halflife: Months for effect to halve (default: 12)
        """
        self.df = df_data.copy()
        self.df_impact = df_impact.copy()
        self.ramp_up = ramp_up_months
        self.decay_halflife = decay_halflife

        # Convert dates
        self.df['observation_date'] = pd.to_datetime(self.df['observation_date'], errors='coerce')

        # Separate record types
        self.observations = self.df[self.df['record_type'] == 'observation'].copy()
        self.events = self.df[self.df['record_type'] == 'event'].copy()
        self.targets = self.df[self.df['record_type'] == 'target'].copy()

        # Build event-indicator mapping
        self._build_event_indicator_map()

    def _build_event_indicator_map(self):
        """Build mapping of which events affect which indicators."""
        self.event_indicator_map = {}

        for _, link in self.df_impact.iterrows():
            parent_id = link['parent_id']
            indicator = link['related_indicator']

            if parent_id not in self.event_indicator_map:
                self.event_indicator_map[parent_id] = []

            self.event_indicator_map[parent_id].append({
                'indicator': indicator,
                'impact_direction': link['impact_direction'],
                'impact_magnitude': link['impact_magnitude'],
                'impact_estimate': link['impact_estimate'],
                'lag_months': link['lag_months'],
                'confidence': link['confidence'],
                'evidence_basis': link['evidence_basis']
            })

    def event_effect(self, event_date: datetime, lag_months: int, 
                     impact_estimate: float, current_date: datetime) -> float:
        """
        Calculate the active effect of an event at a given date.

        The effect follows a lifecycle:
        1. Lag phase: no effect (0 to lag_months)
        2. Ramp up: effect builds linearly (lag to lag + ramp_up)
        3. Peak & decay: effect at maximum then decays exponentially

        Args:
            event_date: When the event occurred
            lag_months: Months until effect starts
            impact_estimate: Maximum effect size
            current_date: Date to evaluate effect at

        Returns:
            Active effect at current_date
        """
        if pd.isna(event_date) or pd.isna(current_date):
            return 0.0

        months_since_event = (current_date - event_date).days / 30.44

        # Phase 1: Before lag - no effect
        if months_since_event < lag_months:
            return 0.0

        months_since_effect_start = months_since_event - lag_months

        # Phase 2: Ramp up
        if months_since_effect_start < self.ramp_up:
            ramp_progress = months_since_effect_start / self.ramp_up
            return impact_estimate * ramp_progress

        # Phase 3: Peak and decay
        months_at_peak = months_since_effect_start - self.ramp_up
        decay_factor = 0.5 ** (months_at_peak / self.decay_halflife)
        return impact_estimate * decay_factor

    def get_events_for_indicator(self, indicator_code: str) -> pd.DataFrame:
        """Get all events that affect a specific indicator."""
        links = self.df_impact[self.df_impact['related_indicator'] == indicator_code]

        event_effects = []
        for _, link in links.iterrows():
            parent_id = link['parent_id']
            event = self.events[self.events['record_id'] == parent_id]
            if len(event) > 0:
                event_effects.append({
                    'event_id': parent_id,
                    'event_name': event.iloc[0]['indicator'],
                    'event_category': event.iloc[0]['category'],
                    'event_date': event.iloc[0]['observation_date'],
                    'impact_direction': link['impact_direction'],
                    'impact_magnitude': link['impact_magnitude'],
                    'impact_estimate': link['impact_estimate'],
                    'lag_months': link['lag_months'],
                    'confidence': link['confidence'],
                    'evidence_basis': link['evidence_basis'],
                    'comparable_country': link['comparable_country']
                })

        return pd.DataFrame(event_effects)

    def combined_effect(self, indicator_code: str, eval_date: datetime) -> Dict:
        """
        Calculate the combined effect of all events on an indicator at a date.

        Uses additive combination: total = effect_A + effect_B + ...

        Args:
            indicator_code: Indicator to evaluate
            eval_date: Date to evaluate at

        Returns:
            Dictionary with total effect and breakdown by event
        """
        events = self.get_events_for_indicator(indicator_code)

        if len(events) == 0:
            return {'total_effect': 0.0, 'events': []}

        total = 0.0
        breakdown = []

        for _, evt in events.iterrows():
            event_date = evt['event_date']
            lag = evt['lag_months']

            # Apply direction to estimate
            estimate = evt['impact_estimate'] if pd.notna(evt['impact_estimate']) else 0
            if evt['impact_direction'] == 'decrease':
                estimate = -abs(estimate)
            elif evt['impact_direction'] == 'increase':
                estimate = abs(estimate)

            effect = self.event_effect(event_date, lag, estimate, eval_date)
            total += effect

            breakdown.append({
                'event': evt['event_name'],
                'effect': effect,
                'active': effect > 0.1
            })

        return {'total_effect': total, 'events': breakdown}

    def validate(self, indicator_code: str, gender: str = 'all', 
                 location: str = 'national') -> Dict:
        """
        Validate impact model against historical observations.

        Compares model predictions to actual observations and
        calculates prediction errors.

        Args:
            indicator_code: Indicator to validate
            gender: Gender filter
            location: Location filter

        Returns:
            Validation results dictionary
        """
        # Get observations
        mask = (self.observations['indicator_code'] == indicator_code)
        if gender:
            mask &= (self.observations['gender'] == gender)
        if location:
            mask &= (self.observations['location'] == location)

        obs = self.observations[mask].sort_values('observation_date')

        if len(obs) < 2:
            return {
                'indicator': indicator_code,
                'status': 'INSUFFICIENT_DATA',
                'message': f'Only {len(obs)} observation(s) available'
            }

        # Use first observation as baseline
        baseline = obs.iloc[0]
        baseline_date = baseline['observation_date']
        baseline_value = baseline['value_numeric']

        validations = []

        for i in range(1, len(obs)):
            current = obs.iloc[i]
            current_date = current['observation_date']
            actual_value = current['value_numeric']

            # Calculate combined event effect since baseline
            combined = self.combined_effect(indicator_code, current_date)
            predicted = baseline_value + combined['total_effect']

            error = actual_value - predicted
            error_pct = (error / actual_value * 100) if actual_value != 0 else np.inf

            validations.append({
                'date': current_date,
                'actual': actual_value,
                'predicted': predicted,
                'error': error,
                'error_pct': error_pct,
                'events_active': [e['event'] for e in combined['events'] if e['active']]
            })

        return {
            'indicator': indicator_code,
            'baseline_date': baseline_date,
            'baseline_value': baseline_value,
            'validations': validations,
            'status': 'VALIDATED'
        }

    def build_association_matrix(self) -> pd.DataFrame:
        """
        Build the event-indicator association matrix.

        Rows = Events, Columns = Indicators, Values = Estimated impact
        """
        all_events = self.events['indicator'].tolist()
        all_indicators = self.observations['indicator_code'].dropna().unique().tolist()

        # Add indicators from impact links
        impact_indicators = self.df_impact['related_indicator'].dropna().unique().tolist()
        all_indicators = list(set(all_indicators + impact_indicators))
        all_indicators.sort()

        matrix = pd.DataFrame(index=all_events, columns=all_indicators)
        matrix[:] = 0.0

        for _, link in self.df_impact.iterrows():
            event_id = link['parent_id']
            event_row = self.events[self.events['record_id'] == event_id]
            if len(event_row) > 0:
                event_name = event_row.iloc[0]['indicator']
                indicator = link['related_indicator']

                estimate = link['impact_estimate'] if pd.notna(link['impact_estimate']) else 0
                if link['impact_direction'] == 'decrease':
                    estimate = -abs(estimate)
                elif link['impact_direction'] == 'increase':
                    estimate = abs(estimate)

                matrix.loc[event_name, indicator] = estimate

        return matrix

    def refine_estimate(self, impact_link_id: str, new_estimate: float, 
                        reason: str, confidence: str = 'high') -> Dict:
        """
        Propose a refined impact estimate based on validation.

        Args:
            impact_link_id: ID of the impact link to refine
            new_estimate: Revised estimate
            reason: Documentation for the change
            confidence: New confidence level

        Returns:
            Refinement record
        """
        link = self.df_impact[self.df_impact['record_id'] == impact_link_id]
        if len(link) == 0:
            return {'status': 'ERROR', 'message': f'Impact link {impact_link_id} not found'}

        old_estimate = link.iloc[0]['impact_estimate']

        return {
            'impact_link_id': impact_link_id,
            'old_estimate': old_estimate,
            'new_estimate': new_estimate,
            'reason': reason,
            'confidence': confidence,
            'status': 'PROPOSED'
        }


if __name__ == "__main__":
    # Example usage
    print("Event Impact Model - Example Usage")
    print("=" * 60)

    # This would normally load from files:
    # df = pd.read_excel("data/raw/ethiopia_fi_unified_data.xlsx")
    # df_impact = pd.read_excel("data/raw/ethiopia_fi_unified_data.xlsx", sheet_name=1)
    # model = EventImpactModel(df, df_impact)

    # Example: Get combined effect on P2P Count in July 2025
    # combined = model.combined_effect('USG_P2P_COUNT', pd.Timestamp('2025-07-01'))
    # print(f"Combined effect: {combined['total_effect']:.2f}%")

    # Example: Validate ACC_MM_ACCOUNT
    # validation = model.validate('ACC_MM_ACCOUNT')
    # print(validation)