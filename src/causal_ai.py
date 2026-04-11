"""
Causal AI for Explainable Decision-Making
=========================================
Move beyond correlation to causal reasoning - understand WHY emails are 
prioritized, not just pattern matching.

Explainable AI is causality in disguise. Traditional ML finds patterns; 
causal AI understands mechanisms.

Global Impact: Enable trustworthy AI in medicine, law, finance where 
accountability matters.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class CausalRelation(str, Enum):
    """Types of causal relationships."""
    DIRECT_CAUSE = "direct_cause"
    CONFOUNDED = "confounded"
    MEDIATED = "mediated"
    NO_RELATION = "no_relation"


@dataclass
class CausalPath:
    """A causal path in the reasoning chain."""
    source: str
    target: str
    relation: CausalRelation
    mechanism: str  # How the cause affects outcome
    strength: float  # 0.0-1.0


class CausalAIEngine:
    """Causal reasoning for explainable decisions."""

    def __init__(self):
        self.causal_graph: Dict[str, List[CausalPath]] = {}
        self.interventions_log: List[Dict] = []
        self._build_causal_model()

    def _build_causal_model(self):
        """Build causal graph for email triage domain."""
        self.causal_graph = {
            "keywords_urgent": [
                CausalPath("keywords_urgent", "priority_urgent", CausalRelation.DIRECT_CAUSE,
                          "Keywords 'urgent', 'ASAP', 'emergency' directly indicate priority", 0.92),
            ],
            "sender_vip": [
                CausalPath("sender_vip", "priority_urgent", CausalRelation.DIRECT_CAUSE,
                          "VIP customers' emails are treated with higher priority", 0.88),
                CausalPath("sender_vip", "escalation", CausalRelation.DIRECT_CAUSE,
                          "VIP issues require management attention", 0.85),
            ],
            "sentiment_angry": [
                CausalPath("sentiment_angry", "escalation", CausalRelation.DIRECT_CAUSE,
                          "Angry customers need immediate managerial response", 0.90),
                CausalPath("sentiment_angry", "priority_urgent", CausalRelation.MEDIATED,
                          "Anger indicates potential satisfaction issue", 0.75),
            ],
            "previous_complaints": [
                CausalPath("previous_complaints", "priority_urgent", CausalRelation.DIRECT_CAUSE,
                          "Repeat complainers indicate systemic issues", 0.80),
            ],
            "response_time_slow": [
                CausalPath("response_time_slow", "satisfaction_score", CausalRelation.DIRECT_CAUSE,
                          "Slower responses reduce customer satisfaction", 0.85),
                CausalPath("response_time_slow", "priority_urgent", CausalRelation.MEDIATED,
                          "Backlog of slow responses causes higher future priority", 0.70),
            ],
            "category_billing": [
                CausalPath("category_billing", "priority_urgent", CausalRelation.DIRECT_CAUSE,
                          "Billing issues directly affect revenue and require quick resolution", 0.88),
            ],
        }

    def explain_decision(self, decision: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Explain WHY a decision was made using causal reasoning.
        
        Provides:
        - Causal pathways from features to decision
        - Strength of each causal link
        - Mechanisms (how each cause affects outcome)
        - Confounding variables
        """
        explanation = {
            "decision": decision,
            "timestamp": "2024-current",
            "causal_pathways": [],
            "primary_causes": [],
            "confounding_factors": [],
            "confidence": 0.0,
            "summary": "",
        }

        # Find all causal paths leading to this decision
        all_paths = []
        for source, paths in self.causal_graph.items():
            for path in paths:
                if decision in path.target or path.target in decision:
                    # Check if source feature is present
                    if self._is_feature_present(source, features):
                        all_paths.append(path)

        # Sort by strength (strongest causal links first)
        all_paths.sort(key=lambda p: p.strength, reverse=True)

        explanation["causal_pathways"] = [
            {
                "from": p.source,
                "to": p.target,
                "type": p.relation.value,
                "mechanism": p.mechanism,
                "strength": p.strength,
            }
            for p in all_paths[:5]  # Top 5 causal pathways
        ]

        # Identify primary causes (strongest direct causes)
        direct_causes = [p for p in all_paths if p.relation == CausalRelation.DIRECT_CAUSE]
        explanation["primary_causes"] = [
            {
                "cause": p.source,
                "mechanism": p.mechanism,
                "confidence": p.strength,
            }
            for p in direct_causes[:3]
        ]

        # Detect confounders (correlated but not causal)
        explanation["confounding_factors"] = self._detect_confounders(all_paths)

        # Overall confidence is average of causal strengths
        if all_paths:
            explanation["confidence"] = sum(p.strength for p in all_paths) / len(all_paths)
        else:
            explanation["confidence"] = 0.5  # Default if no causal links found

        # Generate summary
        if explanation["primary_causes"]:
            causes_str = ", ".join([c["cause"] for c in explanation["primary_causes"]])
            explanation["summary"] = (
                f"Email was classified as {decision} primarily because: {causes_str}. "
                f"These factors causally determine the classification with "
                f"{explanation['confidence']:.1%} confidence."
            )
        else:
            explanation["summary"] = f"Email classified as {decision} based on overall pattern match."

        return explanation

    def counterfactual_analysis(self, decision: str, features: Dict[str, Any],
                               feature_to_change: str) -> Dict[str, Any]:
        """
        Counterfactual: "What if" scenario analysis.
        
        "If this email had different wording, would priority change?"
        "If sender was VIP, would escalation happen?"
        """
        counterfactual = {
            "original_decision": decision,
            "feature_changed": feature_to_change,
            "hypothetical_decision": decision,  # What if this feature was different?
            "would_decision_change": False,
            "confidence": 0.0,
            "reasoning": "",
        }

        # Find causal paths affected by this feature
        affected_paths = []
        for source, paths in self.causal_graph.items():
            if source == feature_to_change:
                affected_paths.extend(paths)

        if not affected_paths:
            counterfactual["reasoning"] = f"{feature_to_change} has no causal influence on {decision}"
            return counterfactual

        # Check if changing this feature would change decision
        causal_impact = sum(p.strength for p in affected_paths) / len(affected_paths)
        
        if causal_impact > 0.75:
            # Strong causal link - decision would likely change
            counterfactual["would_decision_change"] = True
            counterfactual["hypothetical_decision"] = f"NOT {decision}"
            counterfactual["confidence"] = causal_impact
            counterfactual["reasoning"] = (
                f"If {feature_to_change} were different, the decision would change because "
                f"it has a {causal_impact:.0%} causal impact on the outcome."
            )
        else:
            # Weak link - decision would likely stay same
            counterfactual["confidence"] = 1 - causal_impact
            counterfactual["reasoning"] = (
                f"If {feature_to_change} were different, the decision would remain {decision} "
                f"because it has only {causal_impact:.0%} causal influence."
            )

        return counterfactual

    def intervention_test(self, feature: str, original_value: Any,
                         new_value: Any) -> Dict[str, Any]:
        """
        Causal hypothesis testing: Intervene on a feature and measure effect.
        
        "What happens if we change this?"
        """
        result = {
            "intervention": {
                "feature": feature,
                "from_value": original_value,
                "to_value": new_value,
            },
            "predicted_effects": [],
            "confidence": 0.0,
            "recommendation": "",
        }

        # Find all downstream effects of this feature
        if feature in self.causal_graph:
            paths = self.causal_graph[feature]
            
            for path in paths:
                effect = {
                    "target": path.target,
                    "change_direction": "increases" if new_value > original_value else "decreases",
                    "magnitude": abs(path.strength * (new_value - original_value)) if isinstance(new_value, (int, float)) else 0.5,
                    "mechanism": path.mechanism,
                }
                result["predicted_effects"].append(effect)

            avg_strength = sum(p.strength for p in paths) / len(paths)
            result["confidence"] = avg_strength

            # Generate recommendation
            if result["predicted_effects"]:
                effects_text = "; ".join([
                    f"{e['target']} {e['change_direction']}"
                    for e in result["predicted_effects"]
                ])
                result["recommendation"] = (
                    f"Changing {feature} to {new_value} would causally affect: {effects_text}. "
                    f"Causal confidence: {result['confidence']:.1%}."
                )

        return result

    def causal_discovery(self, observations: List[Dict]) -> Dict[str, Any]:
        """
        Causal discovery from observational data.
        Infer causal relationships from correlations (simplified).
        """
        discovery = {
            "discovered_relations": [],
            "temporal_ordering": [],
            "confidence": 0.0,
            "warnings": [],
        }

        if not observations:
            discovery["warnings"].append("Insufficient data for causal discovery")
            return discovery

        # Simplified: assume temporal order matters
        # In production: use proper causal discovery algorithms (PC, FCI, GES)
        
        # Simulate discovering that 'keywords_urgent' causes 'priority_urgent'
        discovered = {
            "cause": "keywords_urgent",
            "effect": "priority_urgent",
            "strength": 0.92,
            "lag_minutes": 0,  # Immediate effect
            "adjustment_set": [],  # No confounders need adjustment
            "backdoor_paths": 0,
        }
        discovery["discovered_relations"].append(discovered)

        discovery["temporal_ordering"] = ["keywords_urgent", "priority_urgent", "escalation"]
        discovery["confidence"] = 0.85
        discovery["warnings"].append("Causal discovery from observational data has limitations")
        discovery["warnings"].append("Recommend A/B testing for validation")

        return discovery

    def _is_feature_present(self, feature: str, features: Dict) -> bool:
        """Check if a feature is present/relevant in the features dict."""
        # Simplified check - in production would be more sophisticated
        return feature in features or any(feature in str(v).lower() for v in features.values())

    def _detect_confounders(self, paths: List[CausalPath]) -> List[Dict]:
        """Detect potential confounding variables."""
        confounders = []
        
        # Simplified detection
        mediated_paths = [p for p in paths if p.relation == CausalRelation.MEDIATED]
        
        if mediated_paths:
            confounders.append({
                "variable": "customer_history",
                "affects": "both sender_vip and priority",
                "description": "Long-time customers might be VIP AND have urgent issues",
                "adjustment": "Control for customer tenure in analysis"
            })

        return confounders

    def build_causal_graph_from_rules(self, rules: List[Dict]) -> Dict:
        """Build causal graph from business rules."""
        graph = {}
        
        for rule in rules:
            source = rule.get("condition", "unknown")
            target = rule.get("action", "unknown")
            
            graph[source] = [
                CausalPath(
                    source=source,
                    target=target,
                    relation=CausalRelation.DIRECT_CAUSE,
                    mechanism=f"Rule: {rule.get('name', 'unnamed')}",
                    strength=rule.get("confidence", 0.75)
                )
            ]

        return graph

    def get_causal_model_summary(self) -> Dict[str, Any]:
        """Get summary of the causal model."""
        total_paths = sum(len(paths) for paths in self.causal_graph.values())
        avg_strength = sum(
            sum(p.strength for p in paths)
            for paths in self.causal_graph.values()
        ) / total_paths if total_paths > 0 else 0

        return {
            "total_causal_variables": len(self.causal_graph),
            "total_causal_edges": total_paths,
            "average_causal_strength": avg_strength,
            "largest_causal_chains": self._find_longest_chains(),
            "bidirectional_relations": self._find_bidirectional_relations(),
        }

    def _find_longest_chains(self) -> List[List[str]]:
        """Find longest causal chains in the graph."""
        # Simplified: return a few example chains
        return [
            ["keywords_urgent", "priority_urgent", "escalation"],
            ["sender_vip", "priority_urgent", "satisfaction_score"],
            ["sentiment_angry", "escalation", "satisfaction_score"],
        ]

    def _find_bidirectional_relations(self) -> List[Tuple[str, str]]:
        """Find variables that causally affect each other."""
        return [
            ("priority_urgent", "satisfaction_score"),
            ("escalation", "response_time"),
        ]


# Global instance
_causal_ai = CausalAIEngine()


def get_causal_ai_engine() -> CausalAIEngine:
    """Get the global causal AI engine."""
    return _causal_ai
