#!/usr/bin/env python3
"""
Pre-submission validation script for OpenEnv hackathon.
Run this before submitting to catch common issues.
"""

import json
import sys
from pathlib import Path

import yaml


def check_file_exists(path: Path, name: str) -> bool:
    """Check if a required file exists."""
    if path.exists():
        print(f"  ✓ {name} exists")
        return True
    else:
        print(f"  ✗ {name} MISSING at {path}")
        return False


def validate_openenv_yaml(path: Path) -> bool:
    """Validate openenv.yaml structure."""
    print("\n📋 Validating openenv.yaml...")
    
    try:
        with open(path) as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"  ✗ Failed to parse YAML: {e}")
        return False

    required_fields = ["name", "version", "tasks", "endpoints"]
    missing = [f for f in required_fields if f not in config]
    
    if missing:
        print(f"  ✗ Missing required fields: {missing}")
        return False
    
    print(f"  ✓ Name: {config.get('name')}")
    print(f"  ✓ Version: {config.get('version')}")
    
    # Validate tasks
    tasks = config.get("tasks", [])
    if len(tasks) < 3:
        print(f"  ✗ Need at least 3 tasks, found {len(tasks)}")
        return False
    
    print(f"  ✓ Tasks: {len(tasks)} defined")
    for task in tasks:
        difficulty = task.get("difficulty", "unknown")
        print(f"    - {task.get('id', 'unknown')}: {task.get('name', 'unnamed')} ({difficulty})")
    
    # Validate endpoints
    endpoints = config.get("endpoints", {})
    required_endpoints = ["reset", "step", "state"]
    missing_endpoints = [e for e in required_endpoints if e not in endpoints]
    
    if missing_endpoints:
        print(f"  ✗ Missing endpoints: {missing_endpoints}")
        return False
    
    print(f"  ✓ Endpoints: {list(endpoints.keys())}")
    
    return True


def validate_dockerfile(path: Path) -> bool:
    """Validate Dockerfile has required elements."""
    print("\n🐳 Validating Dockerfile...")
    
    try:
        content = path.read_text()
    except Exception as e:
        print(f"  ✗ Failed to read: {e}")
        return False
    
    checks = [
        ("FROM python:3.11", "Base image"),
        ("EXPOSE 7860", "Port 7860 exposed"),
        ("CMD", "Has CMD instruction"),
        ("uvicorn", "Uses uvicorn server"),
    ]
    
    all_pass = True
    for pattern, description in checks:
        if pattern in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} - pattern '{pattern}' not found")
            all_pass = False
    
    return all_pass


def validate_inference_script(path: Path) -> bool:
    """Validate inference.py has required elements."""
    print("\n🔬 Validating inference.py...")
    
    try:
        content = path.read_text()
    except Exception as e:
        print(f"  ✗ Failed to read: {e}")
        return False
    
    checks = [
        ("from openai import OpenAI", "Uses OpenAI Client"),
        ("API_BASE_URL", "Reads API_BASE_URL"),
        ("MODEL_NAME", "Reads MODEL_NAME"),
        ("HF_TOKEN", "Reads HF_TOKEN"),
        ("[START]", "Emits [START] log"),
        ("[STEP]", "Emits [STEP] log"),
        ("[END]", "Emits [END] log"),
    ]
    
    all_pass = True
    for pattern, description in checks:
        if pattern in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} - pattern '{pattern}' not found")
            all_pass = False
    
    return all_pass


def validate_tests_exist(tests_dir: Path) -> bool:
    """Check that tests exist and cover key areas."""
    print("\n🧪 Validating tests...")
    
    if not tests_dir.exists():
        print(f"  ✗ Tests directory not found at {tests_dir}")
        return False
    
    test_files = list(tests_dir.glob("test_*.py"))
    
    if len(test_files) < 2:
        print(f"  ✗ Need at least 2 test files, found {len(test_files)}")
        return False
    
    print(f"  ✓ Found {len(test_files)} test files:")
    for tf in test_files:
        print(f"    - {tf.name}")
    
    return True


def validate_graders_deterministic() -> bool:
    """Run a quick check that graders produce consistent scores."""
    print("\n🎯 Validating grader determinism...")
    
    try:
        from src.graders.classify_grader import grade_classification
        from src.graders.respond_grader import grade_response
        from src.graders.thread_grader import grade_thread_step
        from src.data.emails import CLASSIFY_EMAILS, RESPOND_EMAILS, THREAD_SCENARIOS
        
        # Test classification grader
        email = CLASSIFY_EMAILS[0]
        r1 = grade_classification("Priority: urgent\nCategory: billing", email)
        r2 = grade_classification("Priority: urgent\nCategory: billing", email)
        assert r1.total == r2.total, "Classification grader not deterministic"
        print(f"  ✓ Classification grader: deterministic (score={r1.total})")
        
        # Test response grader
        email = RESPOND_EMAILS[0]
        resp = "Dear Customer, we apologize for the delay. We will resolve this."
        r1 = grade_response(resp, email)
        r2 = grade_response(resp, email)
        assert r1.total == r2.total, "Response grader not deterministic"
        print(f"  ✓ Response grader: deterministic (score={r1.total})")
        
        # Test thread grader
        thread = THREAD_SCENARIOS[0]
        r1 = grade_thread_step(0, "The CFO and sysadmin contradict each other.", thread)
        r2 = grade_thread_step(0, "The CFO and sysadmin contradict each other.", thread)
        assert r1.total == r2.total, "Thread grader not deterministic"
        print(f"  ✓ Thread grader: deterministic (score={r1.total})")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Grader validation failed: {e}")
        return False


def validate_graders_vary() -> bool:
    """Check that graders produce different scores for different inputs."""
    print("\n📊 Validating grader score variation...")
    
    try:
        from src.graders.classify_grader import grade_classification
        from src.data.emails import CLASSIFY_EMAILS
        
        email = CLASSIFY_EMAILS[0]  # urgent billing
        
        # Test different responses produce different scores
        scores = {
            "correct": grade_classification("Priority: urgent\nCategory: billing", email).total,
            "partial": grade_classification("Priority: normal\nCategory: billing", email).total,
            "wrong": grade_classification("Priority: low\nCategory: general", email).total,
            "empty": grade_classification("", email).total,
        }
        
        unique_scores = set(scores.values())
        
        if len(unique_scores) < 3:
            print(f"  ✗ Grader produces only {len(unique_scores)} unique scores: {scores}")
            return False
        
        print(f"  ✓ Classification grader produces varied scores:")
        for label, score in scores.items():
            print(f"    - {label}: {score}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Score variation check failed: {e}")
        return False


def validate_server_imports() -> bool:
    """Check that server can be imported without errors."""
    print("\n🌐 Validating server imports...")
    
    try:
        from src.server import app
        from src.environment import EmailTriageEnv
        print("  ✓ Server module imports successfully")
        print("  ✓ Environment module imports successfully")
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def validate_innovative_features() -> bool:
    """Validate the innovative features are working."""
    print("\n🚀 Validating innovative features...")
    
    try:
        from src.environment import EmailTriageEnv
        from src.models import Action
        
        # Test curriculum learning
        env = EmailTriageEnv(curriculum_mode=True, adaptive_difficulty=False)
        assert "email_classify" in env._unlocked_tasks
        assert "email_respond" not in env._unlocked_tasks  # Initially locked
        print("  ✓ Curriculum learning: tasks locked/unlocked correctly")
        
        # Test email similarity avoidance
        env = EmailTriageEnv(avoid_repetition=True, curriculum_mode=False)
        env.reset(task_id="email_classify")
        env.step(Action(message="Priority: urgent\nCategory: billing"))
        assert len(env._seen_emails["email_classify"]) > 0
        print("  ✓ Email similarity avoidance: tracks seen emails")
        
        # Test curriculum unlocking
        env = EmailTriageEnv(curriculum_mode=True, adaptive_difficulty=False)
        env._task_scores["email_classify"] = [0.85, 0.90, 0.80, 0.75, 0.72]
        env._update_curriculum()
        assert "email_respond" in env._unlocked_tasks
        print("  ✓ Curriculum learning: unlocks tasks based on scores")
        
        # Test state includes new metadata
        env = EmailTriageEnv(curriculum_mode=True, avoid_repetition=True)
        env.reset(task_id="email_classify")
        state = env.state()
        assert "curriculum_mode" in state.metadata
        assert "seen_emails" in state.metadata
        print("  ✓ State metadata includes curriculum and similarity info")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Innovative features validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def validate_streaming_endpoint() -> bool:
    """Validate the streaming endpoint exists."""
    print("\n📡 Validating streaming endpoint...")
    
    try:
        from src.server import app, stream_step
        
        # Check that the endpoint exists
        routes = [r.path for r in app.routes]
        if "/stream_step" in routes:
            print("  ✓ /stream_step endpoint exists")
            return True
        else:
            print("  ✗ /stream_step endpoint not found")
            return False
            
    except Exception as e:
        print(f"  ✗ Streaming endpoint validation failed: {e}")
        return False


def main():
    print("=" * 60)
    print("🚀 OpenEnv Pre-Submission Validation")
    print("=" * 60)
    
    base_dir = Path(__file__).parent
    
    # Add src to path for imports
    sys.path.insert(0, str(base_dir))
    
    results = []
    
    # Check required files
    print("\n📁 Checking required files...")
    results.append(check_file_exists(base_dir / "openenv.yaml", "openenv.yaml"))
    results.append(check_file_exists(base_dir / "Dockerfile", "Dockerfile"))
    results.append(check_file_exists(base_dir / "inference.py", "inference.py"))
    results.append(check_file_exists(base_dir / "README.md", "README.md"))
    results.append(check_file_exists(base_dir / "requirements.txt", "requirements.txt"))
    results.append(check_file_exists(base_dir / "src" / "environment.py", "src/environment.py"))
    results.append(check_file_exists(base_dir / "src" / "models.py", "src/models.py"))
    results.append(check_file_exists(base_dir / "src" / "server.py", "src/server.py"))
    
    # Validate individual files
    results.append(validate_openenv_yaml(base_dir / "openenv.yaml"))
    results.append(validate_dockerfile(base_dir / "Dockerfile"))
    results.append(validate_inference_script(base_dir / "inference.py"))
    results.append(validate_tests_exist(base_dir / "tests"))
    
    # Validate code quality
    results.append(validate_server_imports())
    results.append(validate_graders_deterministic())
    results.append(validate_graders_vary())
    
    # Validate innovative features
    results.append(validate_innovative_features())
    results.append(validate_streaming_endpoint())
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✅ ALL CHECKS PASSED ({passed}/{total})")
        print("\nYour environment is ready for submission!")
        print("\nInnovative features verified:")
        print("  ✓ Curriculum Learning Mode")
        print("  ✓ Email Similarity Avoidance")
        print("  ✓ Streaming Grading Feedback")
        print("\nNext steps:")
        print("  1. Run tests: pytest tests/ -v")
        print("  2. Build Docker: docker build -t email-triage-env .")
        print("  3. Test locally: docker run -p 7860:7860 email-triage-env")
        print("  4. Deploy to HF Spaces")
        return 0
    else:
        print(f"❌ SOME CHECKS FAILED ({passed}/{total})")
        print("\nPlease fix the issues above before submitting.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
