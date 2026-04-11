"""
Comprehensive tests for Accessibility module.
Tests WCAG 2.2 AAA compliance, accessibility modes, and disability support.
"""

import pytest
from src.accessibility import (
    AccessibilityEngine,
    AccessibilityMode,
    get_accessibility_engine
)


@pytest.fixture
def engine():
    """Create fresh engine for each test."""
    return AccessibilityEngine()


class TestScreenReaderOptimization:
    """Test screen reader compatibility (NVDA, JAWS)."""

    def test_basic_screen_reader_optimization(self, engine):
        """Test basic screen reader output."""
        content = "Welcome to email support"
        output = engine.optimize_for_screen_reader(content)
        assert isinstance(output, str)
        assert len(output) > 0
        assert "Welcome" in output

    def test_screen_reader_with_heading(self, engine):
        """Test screen reader optimization with heading structure."""
        content = "Important Message"
        structure = {"type": "heading", "level": "1"}
        output = engine.optimize_for_screen_reader(content, structure)
        assert "HEADING:" in output
        assert "Important Message" in output

    def test_screen_reader_with_list(self, engine):
        """Test screen reader optimization with list structure."""
        content = "Item 1\nItem 2\nItem 3"
        structure = {"type": "list"}
        output = engine.optimize_for_screen_reader(content, structure)
        assert "LIST START:" in output
        assert "LIST END:" in output


class TestDyslexiaFriendlyFormatting:
    """Test dyslexia-friendly formatting."""

    def test_dyslexia_formatting_complete(self, engine):
        """Test complete dyslexia formatting."""
        text = "This is important information"
        result = engine.apply_dyslexia_friendly_formatting(text)
        assert result["font"] == "OpenDyslexic"
        assert result["line_height"] == "1.5"
        assert result["letter_spacing"] == "0.12em"
        assert result["background_color"] == "#FFFACD"  # Light yellow

    def test_dyslexia_formatting_recommendations(self, engine):
        """Test dyslexia formatting includes recommendations."""
        text = "Sample text"
        result = engine.apply_dyslexia_friendly_formatting(text)
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0
        assert any("sans-serif" in rec.lower() for rec in result["recommendations"])

    def test_dyslexia_font_list(self, engine):
        """Test dyslexia-friendly font list."""
        fonts = engine.dyslexia_friendly_fonts
        assert "OpenDyslexic" in fonts
        assert "Verdana" in fonts
        assert len(fonts) >= 3


class TestHighContrastFormatting:
    """Test WCAG AAA high contrast formatting."""

    def test_high_contrast_7_to_1_ratio(self, engine):
        """Test high contrast meets WCAG AAA 7:1 ratio."""
        content = "Important notice"
        result = engine.apply_high_contrast_formatting(content)
        assert result["wcag_compliance"] == "AAA"
        assert result["contrast_ratio"] == "7:1"

    def test_high_contrast_color_scheme(self, engine):
        """Test high contrast color scheme."""
        result = engine.apply_high_contrast_formatting("text")
        scheme = result["color_scheme"]
        assert "text" in scheme
        assert "background" in scheme
        assert "accent" in scheme
        assert "alert" in scheme

    def test_high_contrast_css(self, engine):
        """Test high contrast CSS output."""
        result = engine.apply_high_contrast_formatting("Sample")
        assert "css" in result
        assert "color:" in result["css"]
        assert "background-color:" in result["css"]


class TestCognitiveSimplification:
    """Test cognitive load reduction."""

    def test_simplify_complex_vocabulary(self, engine):
        """Test vocabulary simplification."""
        text = "We will facilitate the implementation of comprehensive solutions"
        simplified = engine.simplify_for_cognitive_load(text)
        assert "help" in simplified
        assert "facility" not in simplified.lower()
        assert len(simplified.split()) <= len(text.split()) + 5  # Allow some variation

    def test_simplify_long_sentences(self, engine):
        """Test long sentence splitting."""
        long_sentence = "The quick brown fox jumps over the lazy dog and continues running " \
                       "through the field while the sun shines brightly in the sky above them all day long."
        simplified = engine.simplify_for_cognitive_load(long_sentence)
        sentences = simplified.split(".")
        # Most sentences should be shorter
        avg_length = sum(len(s.split()) for s in sentences if s.strip()) / len([s for s in sentences if s.strip()])
        assert avg_length < 20  # Average words per sentence should be reasonable

    def test_simplified_vocabulary_dict(self, engine):
        """Test simplified vocabulary mapping."""
        vocab = engine.simplified_vocabulary
        assert "facilitate" in vocab
        assert vocab["facilitate"] == "help"
        assert "comprehensive" in vocab
        assert vocab["comprehensive"] == "complete"


class TestVoiceInterface:
    """Test voice command and text-to-speech."""

    def test_voice_commands_structure(self, engine):
        """Test voice command categories."""
        commands = engine.generate_voice_command_interface()
        assert "navigation" in commands
        assert "actions" in commands
        assert "reading" in commands
        assert "help" in commands

    def test_navigation_commands(self, engine):
        """Test navigation voice commands."""
        commands = engine.generate_voice_command_interface()
        nav_commands = commands["navigation"]
        assert len(nav_commands) > 0
        assert any("next" in cmd.lower() for cmd in nav_commands)

    def test_action_commands(self, engine):
        """Test action voice commands."""
        commands = engine.generate_voice_command_interface()
        action_commands = commands["actions"]
        assert len(action_commands) > 0
        assert any("classify" in cmd.lower() for cmd in action_commands)

    def test_voice_output_generation(self, engine):
        """Test voice output parameters."""
        text = "Please read this email"
        output = engine.convert_to_voice_output(text)
        assert output["text"] == text
        assert "speech_rate" in output
        assert "pitch" in output
        assert "volume" in output
        assert "language" in output

    def test_voice_output_emphasis(self, engine):
        """Test emphasis markers in voice output."""
        text = "Hello. This is important, and we need help."
        output = engine.convert_to_voice_output(text)
        emphasized = output["emphasis_markers"]
        assert "break" in emphasized
        assert len(emphasized) > len(text)


class TestAccessibilityReporting:
    """Test WCAG 2.2 AAA compliance reporting."""

    def test_accessibility_report_structure(self, engine):
        """Test accessibility report has required sections."""
        report = engine.generate_accessibility_report("Sample content")
        assert report["wcag_version"] == "2.2"
        assert report["compliance_level"] == "AAA"
        assert "checks" in report
        assert "perceivable" in report["checks"]
        assert "operable" in report["checks"]
        assert "understandable" in report["checks"]
        assert "robust" in report["checks"]

    def test_accessibility_report_compliance(self, engine):
        """Test accessibility report includes compliance percentage."""
        report = engine.generate_accessibility_report("Content")
        assert "compliance_percentage" in report
        assert 0 <= report["compliance_percentage"] <= 100

    def test_accessibility_report_recommendations(self, engine):
        """Test accessibility report includes recommendations."""
        report = engine.generate_accessibility_report("Content")
        assert "recommendations" in report
        assert isinstance(report["recommendations"], list)

    def test_wcag_perceivable_checks(self, engine):
        """Test WCAG perceivable principle checks."""
        report = engine.generate_accessibility_report("Sample")
        perceivable = report["checks"]["perceivable"]
        assert "color_contrast" in perceivable
        assert "text_alternatives" in perceivable
        assert "readable_fonts" in perceivable

    def test_wcag_operable_checks(self, engine):
        """Test WCAG operable principle checks."""
        report = engine.generate_accessibility_report("Sample")
        operable = report["checks"]["operable"]
        assert "keyboard_navigation" in operable
        assert "sufficient_time" in operable
        assert "seizure_prevention" in operable

    def test_wcag_understandable_checks(self, engine):
        """Test WCAG understandable principle checks."""
        report = engine.generate_accessibility_report("Sample")
        understandable = report["checks"]["understandable"]
        assert "readability" in understandable
        assert "predictable" in understandable


class TestAccessibleResponseCreation:
    """Test creating accessible responses in different modes."""

    def test_accessible_response_standard_mode(self, engine):
        """Test standard accessibility mode."""
        text = "Your email has been received"
        response = engine.create_accessible_response(text, AccessibilityMode.STANDARD)
        assert response["accessibility_mode"] == "standard"
        assert "formats" in response

    def test_accessible_response_screen_reader_mode(self, engine):
        """Test screen reader accessibility mode."""
        text = "Urgent message"
        response = engine.create_accessible_response(text, AccessibilityMode.SCREEN_READER)
        assert response["accessibility_mode"] == "screen_reader"
        assert "screen_reader" in response["formats"]

    def test_accessible_response_dyslexia_mode(self, engine):
        """Test dyslexia-friendly mode."""
        text = "Important notification"
        response = engine.create_accessible_response(text, AccessibilityMode.DYSLEXIA_FRIENDLY)
        assert response["accessibility_mode"] == "dyslexia_friendly"
        assert "dyslexia" in response["formats"]

    def test_accessible_response_high_contrast_mode(self, engine):
        """Test high contrast mode."""
        text = "Alert message"
        response = engine.create_accessible_response(text, AccessibilityMode.HIGH_CONTRAST)
        assert response["accessibility_mode"] == "high_contrast"
        assert "high_contrast" in response["formats"]

    def test_accessible_response_cognitive_mode(self, engine):
        """Test cognitive simplification mode."""
        text = "We will facilitate comprehensive email management"
        response = engine.create_accessible_response(text, AccessibilityMode.COGNITIVE_SIMPLIFIED)
        assert response["accessibility_mode"] == "cognitive_simplified"
        assert "simplified" in response["formats"]

    def test_accessible_response_voice_mode(self, engine):
        """Test voice controlled mode."""
        text = "You have an email"
        response = engine.create_accessible_response(text, AccessibilityMode.VOICE_CONTROLLED)
        assert response["accessibility_mode"] == "voice_controlled"
        assert "voice_output" in response["formats"]


class TestAccessibilityModes:
    """Test all accessibility modes."""

    def test_accessibility_mode_enum(self):
        """Test AccessibilityMode enum values."""
        modes = [mode.value for mode in AccessibilityMode]
        assert "standard" in modes
        assert "screen_reader" in modes
        assert "dyslexia_friendly" in modes
        assert "high_contrast" in modes
        assert "voice_controlled" in modes
        assert "cognitive_simplified" in modes


class TestGlobalInstance:
    """Test global accessibility engine instance."""

    def test_get_accessibility_engine(self):
        """Test getting global engine instance."""
        engine1 = get_accessibility_engine()
        engine2 = get_accessibility_engine()
        assert engine1 is engine2  # Should be same instance


class TestDisabilityInclusion:
    """Test support for different disability types."""

    def test_vision_impairment_support(self, engine):
        """Test screen reader for vision impairment."""
        content = "Important message"
        sr_output = engine.optimize_for_screen_reader(content)
        assert isinstance(sr_output, str)
        assert len(sr_output) > 0

    def test_dyslexia_support(self, engine):
        """Test dyslexia-friendly formatting."""
        result = engine.apply_dyslexia_friendly_formatting("Text")
        assert result["font"] == "OpenDyslexic"
        assert "recommendations" in result

    def test_low_vision_support(self, engine):
        """Test high contrast for low vision."""
        result = engine.apply_high_contrast_formatting("Text")
        assert result["wcag_compliance"] == "AAA"
        assert result["contrast_ratio"] == "7:1"

    def test_motor_disability_support(self, engine):
        """Test voice control for motor disabilities."""
        commands = engine.generate_voice_command_interface()
        assert len(commands["actions"]) > 0
        assert len(commands["navigation"]) > 0

    def test_cognitive_disability_support(self, engine):
        """Test cognitive simplification."""
        complex_text = "We will facilitate the implementation of comprehensive solutions"
        simplified = engine.simplify_for_cognitive_load(complex_text)
        assert len(simplified.split()) <= len(complex_text.split()) + 10


class TestWCAG22Compliance:
    """Test WCAG 2.2 AAA compliance."""

    def test_wcag_22_levels(self, engine):
        """Test WCAG 2.2 compliance levels."""
        report = engine.generate_accessibility_report("Content")
        assert report["wcag_version"] == "2.2"
        assert report["compliance_level"] == "AAA"

    def test_wcag_aaa_contrast_ratio(self, engine):
        """Test WCAG AAA requires 7:1 contrast."""
        result = engine.apply_high_contrast_formatting("Text")
        assert result["contrast_ratio"] == "7:1"

    def test_wcag_perceivable_principle(self, engine):
        """Test WCAG perceivable principle."""
        report = engine.generate_accessibility_report("Test")
        assert "perceivable" in report["checks"]
        checks = report["checks"]["perceivable"]
        assert "color_contrast" in checks
        assert "text_alternatives" in checks

    def test_wcag_operable_principle(self, engine):
        """Test WCAG operable principle."""
        report = engine.generate_accessibility_report("Test")
        assert "operable" in report["checks"]
        checks = report["checks"]["operable"]
        assert "keyboard_navigation" in checks

    def test_wcag_understandable_principle(self, engine):
        """Test WCAG understandable principle."""
        report = engine.generate_accessibility_report("Test")
        assert "understandable" in report["checks"]
        checks = report["checks"]["understandable"]
        assert "readability" in checks

    def test_wcag_robust_principle(self, engine):
        """Test WCAG robust principle."""
        report = engine.generate_accessibility_report("Test")
        assert "robust" in report["checks"]
