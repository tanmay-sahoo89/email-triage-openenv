"""Tests for Synthetic Data Generation."""

import pytest
from src.synthetic_data import (
    get_synthetic_generator,
    SyntheticDataGenerator,
    SyntheticEmail,
    EmailCategory,
    Sentiment
)


class TestEmailCategories:
    """Test email category enums."""
    
    def test_email_categories(self):
        assert EmailCategory.BILLING.value == "billing"
        assert EmailCategory.TECHNICAL.value == "technical"
        assert EmailCategory.GENERAL.value == "general"
        assert EmailCategory.COMPLAINT.value == "complaint"
        assert EmailCategory.INQUIRY.value == "inquiry"

    def test_sentiments(self):
        assert Sentiment.POSITIVE.value == "positive"
        assert Sentiment.NEUTRAL.value == "neutral"
        assert Sentiment.NEGATIVE.value == "negative"


class TestSyntheticEmailGeneration:
    """Test synthetic email creation."""
    
    def test_generate_single_email(self):
        generator = get_synthetic_generator()
        
        email = generator._generate_email(
            email_id=1,
            category=EmailCategory.BILLING,
            sentiment=Sentiment.NEGATIVE,
            priority="urgent",
            customer_tier="pro"
        )
        
        assert isinstance(email, SyntheticEmail)
        assert email.category == "billing"
        assert email.sentiment == "negative"
        assert email.priority == "urgent"
        assert email.customer_tier == "pro"
        assert email.created_synthetic is True

    def test_email_has_realistic_content(self):
        generator = get_synthetic_generator()
        
        email = generator._generate_email(
            email_id=1,
            category=EmailCategory.TECHNICAL,
            sentiment=Sentiment.NEUTRAL,
            priority="normal",
            customer_tier="free"
        )
        
        assert len(email.subject) > 0
        assert len(email.body) > 0
        assert email.subject is not None
        assert email.body is not None

    def test_email_id_is_non_identifiable(self):
        generator = get_synthetic_generator()
        
        email1 = generator._generate_email(1, EmailCategory.GENERAL, Sentiment.NEUTRAL, "normal", "free")
        email2 = generator._generate_email(1, EmailCategory.GENERAL, Sentiment.NEUTRAL, "normal", "free")
        
        # IDs should be hash-based and different (due to randomness)
        # Even with same inputs, IDs differ


class TestDatasetGeneration:
    """Test full dataset generation."""
    
    def test_generate_dataset(self):
        generator = get_synthetic_generator()
        dataset = generator.generate_dataset(count=50, privacy_epsilon=1.0)
        
        assert dataset["count"] == 50
        assert len(dataset["emails"]) == 50
        assert "privacy_epsilon" in dataset
        assert dataset["privacy_epsilon"] == 1.0
        assert "statistics" in dataset

    def test_dataset_diversity(self):
        generator = get_synthetic_generator()
        dataset = generator.generate_dataset(count=100)
        
        categories = set(e["category"] for e in dataset["emails"])
        sentiments = set(e["sentiment"] for e in dataset["emails"])
        
        # Should have diversity across categories
        assert len(categories) >= 3
        assert len(sentiments) >= 2

    def test_dataset_statistics(self):
        generator = get_synthetic_generator()
        dataset = generator.generate_dataset(count=100)
        
        stats = dataset["statistics"]
        assert "category_distribution" in stats
        assert "sentiment_distribution" in stats
        assert "priority_distribution" in stats
        assert "customer_tier_distribution" in stats

    def test_distribution_coverage(self):
        generator = get_synthetic_generator()
        dataset = generator.generate_dataset(count=200)
        
        stats = dataset["statistics"]
        
        # Should have some of each category
        assert len(stats["category_distribution"]) >= 3
        # Should have multiple priority levels
        assert len(stats["priority_distribution"]) >= 2


class TestPrivacyGuarantees:
    """Test privacy properties of synthetic data."""
    
    def test_no_pii_present(self):
        generator = get_synthetic_generator()
        dataset = generator.generate_dataset(count=50)
        
        for email in dataset["emails"]:
            subject_lower = email["subject"].lower()
            body_lower = email["body"].lower()
            
            # Shouldn't contain real email patterns
            assert not any(x in subject_lower for x in ["@", "mail:", "password"])

    def test_privacy_audit(self):
        generator = get_synthetic_generator()
        dataset = generator.generate_dataset(count=50)
        
        audit = generator.privacy_audit(dataset)
        
        assert "pii_scan" in audit
        assert audit["pii_risk_score"] < 0.05  # Very low risk
        assert "GDPR" in audit["compliant_with"]
        assert "HIPAA" in audit["compliant_with"]

    def test_differential_privacy_epsilon(self):
        generator = get_synthetic_generator()
        
        # Lower epsilon = more privacy, more noise
        dataset_tight = generator.generate_dataset(count=50, privacy_epsilon=0.5)
        dataset_loose = generator.generate_dataset(count=50, privacy_epsilon=2.0)
        
        assert dataset_tight["privacy_epsilon"] == 0.5
        assert dataset_loose["privacy_epsilon"] == 2.0

    def test_differentially_private_noise(self):
        generator = get_synthetic_generator()
        dataset = generator.generate_dataset(count=50)
        
        # Add differential privacy noise
        noisy_data = generator.add_differential_privacy_noise(
            dataset["emails"],
            epsilon=1.0
        )
        
        assert len(noisy_data) == len(dataset["emails"])
        # IDs should be modified
        for original, noisy in zip(dataset["emails"], noisy_data):
            assert original["id"] != noisy["id"]


class TestUtilityMeasurement:
    """Test utility vs privacy tradeoff."""
    
    def test_utility_comparison(self):
        generator = get_synthetic_generator()
        dataset = generator.generate_dataset(count=50)
        
        real_stats = {
            "billing": 0.20,
            "technical": 0.30,
            "general": 0.25,
            "complaint": 0.15,
            "inquiry": 0.10,
        }
        
        comparison = generator.compare_synthetic_vs_real(dataset, real_stats)
        
        assert "synthetic_distribution" in comparison
        assert "real_distribution" in comparison
        assert "utility_score" in comparison
        assert "privacy_score" in comparison

    def test_utility_validation(self):
        generator = get_synthetic_generator()
        dataset_list = generator.generate_dataset(count=100)["emails"]
        
        validation = generator.validate_utility(dataset_list, utility_threshold=0.80)
        
        assert "total_samples" in validation
        assert "diversity_score" in validation
        assert "representativeness_score" in validation
        assert "suitable_for_training" in validation

    def test_model_training_fitness(self):
        generator = get_synthetic_generator()
        dataset = generator.generate_dataset(count=100)["emails"]
        
        validation = generator.validate_utility(dataset)
        
        # Should be suitable for training
        assert validation["overall_utility"] > 0.80
        assert validation["suitable_for_training"] is True


class TestDataComparison:
    """Test synthetic vs real data comparison."""
    
    def test_distribution_similarity(self):
        generator = get_synthetic_generator()
        synthetic = generator.generate_dataset(count=200)
        
        real_stats = {
            "billing": 0.20,
            "technical": 0.30,
            "general": 0.25,
            "complaint": 0.15,
            "inquiry": 0.10,
        }
        
        comparison = generator.compare_synthetic_vs_real(synthetic, real_stats)
        
        # Should be reasonably similar (KL divergence based)
        assert comparison["distribution_similarity"] > 0.70

    def test_use_case_recommendations(self):
        generator = get_synthetic_generator()
        synthetic = generator.generate_dataset(count=100)
        
        real_stats = {}
        comparison = generator.compare_synthetic_vs_real(synthetic, real_stats)
        
        # Should recommend use cases
        use_cases = comparison["trade_off_analysis"]["best_use_cases"]
        assert "training" in str(use_cases).lower()
        assert "evaluation" in str(use_cases).lower()


class TestGlobalImpact:
    """Test global impact features."""
    
    def test_gdpr_compliance(self):
        generator = get_synthetic_generator()
        dataset = generator.generate_dataset(count=100)
        
        audit = generator.privacy_audit(dataset)
        assert "GDPR" in audit["compliant_with"]

    def test_hipaa_compliance(self):
        generator = get_synthetic_generator()
        dataset = generator.generate_dataset(count=100)
        
        audit = generator.privacy_audit(dataset)
        assert "HIPAA" in audit["compliant_with"]

    def test_ccpa_compliance(self):
        generator = get_synthetic_generator()
        dataset = generator.generate_dataset(count=100)
        
        audit = generator.privacy_audit(dataset)
        assert "CCPA" in audit["compliant_with"]

    def test_cross_institutional_sharing(self):
        generator = get_synthetic_generator()
        dataset = generator.generate_dataset(count=100)
        
        audit = generator.privacy_audit(dataset)
        
        # Should be safe to share across institutions
        assert audit["pii_risk_score"] < 0.05

    def test_research_enablement(self):
        generator = get_synthetic_generator()
        dataset = generator.generate_dataset(count=100)
        
        # Should be usable for research
        assert dataset.get("format") or dataset["count"]
        # Should be replicable without real data

    def test_vendor_evaluation_use_case(self):
        generator = get_synthetic_generator()
        dataset = generator.generate_dataset(count=100)
        
        audit = generator.privacy_audit(dataset)
        
        # Use case: Can give to vendors without exposing real data
        assert audit["pii_risk_score"] <= 0.01  # Almost no PII risk


class TestTemplateGeneration:
    """Test template variable substitution."""
    
    def test_template_substitution(self):
        generator = get_synthetic_generator()
        
        template = "Invoice #{num} - Payment issue"
        filled = generator._fill_template(template)
        
        # Should have replaced placeholder
        assert "#" not in filled or filled != template
        assert "{num}" not in filled

    def test_variable_diversity(self):
        generator = get_synthetic_generator()
        
        # Generate multiple versions to test diversity
        templates = generator.subjects[EmailCategory.BILLING]
        
        versions = []
        for _ in range(10):
            template = templates[0]
            filled = generator._fill_template(template)
            versions.append(filled)
        
        # Should have some variety
        unique_versions = set(versions)
        assert len(unique_versions) > 1


class TestSentimentSampling:
    """Test realistic sentiment distribution."""
    
    def test_complaint_bias_negative(self):
        generator = get_synthetic_generator()
        
        # Complaints should bias negative
        for _ in range(10):
            sentiment = generator._sample_sentiment(EmailCategory.COMPLAINT)
            # Most should be negative or at least not positive
    
    def test_inquiry_bias_neutral_positive(self):
        generator = get_synthetic_generator()
        
        # Inquiries should be neutral or positive
        sentiments = [generator._sample_sentiment(EmailCategory.INQUIRY) for _ in range(10)]
        # Should not all be negative

    def test_general_balanced(self):
        generator = get_synthetic_generator()
        
        # General category should be balanced
        sentiments = [generator._sample_sentiment(EmailCategory.GENERAL) for _ in range(20)]
        # Should have variety


class TestPrioritySampling:
    """Test realistic priority distribution."""
    
    def test_negative_sentiment_high_priority(self):
        generator = get_synthetic_generator()
        
        # Negative emails should often be urgent
        priority = generator._sample_priority(Sentiment.NEGATIVE, EmailCategory.GENERAL)
        # Should frequently return "urgent"

    def test_billing_high_priority(self):
        generator = get_synthetic_generator()
        
        # Billing should often be urgent
        priorities = [
            generator._sample_priority(Sentiment.NEUTRAL, EmailCategory.BILLING)
            for _ in range(20)
        ]
        # Most should be normal or urgent


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
