#!/usr/bin/env python3
"""
Test script for iShare Dashboard Agent API.

This script tests all API endpoints to ensure they work correctly.

Usage:
    python my_agent2/api/test_api.py

Prerequisites:
    1. iShare backend running on localhost:3000
    2. Dashboard Agent API running on localhost:8001
       Start with: uvicorn my_agent2.api.endpoints:app --reload --port 8001
"""

import requests
import json
import sys
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Configuration
API_BASE_URL = "http://localhost:8001"

# Test data - update these with valid IDs from your database
TEST_LISTING_ID = "6e4a0dad-57ac-4d4b-8a9b-4dc23b21bf6b"
TEST_OWNER_ID = 1
TEST_TOKEN_ID = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImQ4Mjg5MmZhMzJlY2QxM2E0ZTBhZWZlNjI4ZGQ5YWFlM2FiYThlMWUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vaXNoYXJlLTc0YTZkIiwiYXVkIjoiaXNoYXJlLTc0YTZkIiwiYXV0aF90aW1lIjoxNzY3OTgwMTk5LCJ1c2VyX2lkIjoiUW1rWksxSDNiSWMwMWdtclpxa1ZUSnRTbEtHMyIsInN1YiI6IlFta1pLMUgzYkljMDFnbXJacWtWVEp0U2xLRzMiLCJpYXQiOjE3Njc5ODAxOTksImV4cCI6MTc2Nzk4Mzc5OSwiZW1haWwiOiJqb2huQGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJlbWFpbCI6WyJqb2huQGdtYWlsLmNvbSJdfSwic2lnbl9pbl9wcm92aWRlciI6InBhc3N3b3JkIn19.iZQFRi5_jagHDNFrWXtSl_WAaTcIuZjA191v02nr5y-q2JAaK-DjPD9aU76rGnk6D9uAEH5i8KnInX7dWaXUhjehZmd30PUyaQexCDOF_bKwLS3AWrkk6XXmig3MJbyVB17OdtuYsOjV2dfL8QK5XlB_7YaGRtY1V38wx0ed8V4Vsh8mTbkkXwmZK951kHtJ9arJDH1FrPlEIZYQ1RLhBviObuM5bpeml7hJuTIBOIYNVESr4CZ1zv-Vll_EPFY8bDkhRA26EEY48Lb7HsGfptB2LDsaEyrCCOYppKrSkCBuWLu8X13PL4ljwXNxMZa_LVtOPl4Rnpiya04QMsuPTA"


@dataclass
class TestResult:
    """Result of a single test."""
    name: str
    passed: bool
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def print_result(result: TestResult):
    """Print a test result."""
    status = "✅ PASSED" if result.passed else "❌ FAILED"
    print(f"\n{status}: {result.name}")
    
    if result.error:
        print(f"   Error: {result.error}")
    
    if result.response:
        print(f"   Response preview:")
        # Print a shortened version of the response
        response_str = json.dumps(result.response, indent=2)
        lines = response_str.split('\n')
        if len(lines) > 20:
            print('\n'.join(lines[:20]))
            print(f"   ... ({len(lines) - 20} more lines)")
        else:
            print(response_str)


def test_health_check() -> TestResult:
    """Test the health check endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        data = response.json()
        
        passed = (
            response.status_code == 200 and
            data.get("status") == "ok" and
            data.get("service") == "iShare Dashboard Agent API"
        )
        
        return TestResult(
            name="Health Check (GET /)",
            passed=passed,
            response=data
        )
    except Exception as e:
        return TestResult(
            name="Health Check (GET /)",
            passed=False,
            error=str(e)
        )


def test_get_action_codes() -> TestResult:
    """Test getting all action codes."""
    try:
        response = requests.get(f"{API_BASE_URL}/action-codes")
        data = response.json()
        
        expected_codes = ["PRICING_ANALYZE", "PRICING_APPLY", "MARKET_ANALYZE", "REVIEW_ANALYZE"]
        passed = (
            response.status_code == 200 and
            all(code in data for code in expected_codes)
        )
        
        return TestResult(
            name="Get Action Codes (GET /action-codes)",
            passed=passed,
            response=data
        )
    except Exception as e:
        return TestResult(
            name="Get Action Codes (GET /action-codes)",
            passed=False,
            error=str(e)
        )


def test_pricing_analyze() -> TestResult:
    """Test pricing analysis endpoint."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/pricing/analyze",
            json={"listing_id": TEST_LISTING_ID, "token_id": TEST_TOKEN_ID},
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        
        passed = (
            response.status_code == 200 and
            data.get("success") == True and
            data.get("action_code") == "PRICING_ANALYZE" and
            data.get("agent") == "PricingAgent" and
            "current_price" in data.get("data", {}) and
            "suggested_price" in data.get("data", {}) and
            "can_take_action" in data.get("data", {})
        )
        
        return TestResult(
            name="Pricing Analyze (POST /pricing/analyze)",
            passed=passed,
            response=data
        )
    except Exception as e:
        return TestResult(
            name="Pricing Analyze (POST /pricing/analyze)",
            passed=False,
            error=str(e)
        )


def test_pricing_analyze_missing_param() -> TestResult:
    """Test pricing analysis with missing listing_id."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/pricing/analyze",
            json={"token_id": TEST_TOKEN_ID},
            headers={"Content-Type": "application/json"}
        )
        
        # Should return 422 (validation error) or error in response
        passed = response.status_code == 422 or (
            response.status_code == 200 and 
            response.json().get("success") == False
        )
        
        return TestResult(
            name="Pricing Analyze - Missing Param (POST /pricing/analyze)",
            passed=passed,
            response=response.json() if response.status_code == 200 else {"status_code": response.status_code}
        )
    except Exception as e:
        return TestResult(
            name="Pricing Analyze - Missing Param (POST /pricing/analyze)",
            passed=False,
            error=str(e)
        )


def test_pricing_apply() -> TestResult:
    """Test applying a price change."""
    try:
        # First get the current suggested price
        analyze_response = requests.post(
            f"{API_BASE_URL}/pricing/analyze",
            json={"listing_id": TEST_LISTING_ID},
            headers={"Content-Type": "application/json"}
        )
        suggested_price = analyze_response.json().get("data", {}).get("suggested_price", 100.0)
        
        # Apply the price change
        response = requests.post(
            f"{API_BASE_URL}/pricing/apply",
            json={
                "listing_id": TEST_LISTING_ID,
                "new_price": suggested_price,
                "token_id": TEST_TOKEN_ID
            },
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        
        passed = (
            response.status_code == 200 and
            data.get("success") == True and
            data.get("action_code") == "PRICING_APPLY" and
            data.get("agent") == "PricingAgent" and
            "old_price" in data.get("data", {}) and
            "new_price" in data.get("data", {}) and
            "message" in data.get("data", {})
        )
        
        return TestResult(
            name="Pricing Apply (POST /pricing/apply)",
            passed=passed,
            response=data
        )
    except Exception as e:
        return TestResult(
            name="Pricing Apply (POST /pricing/apply)",
            passed=False,
            error=str(e)
        )


def test_market_analyze() -> TestResult:
    """Test market trend analysis endpoint."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/market/analyze",
            json={"owner_id": TEST_OWNER_ID, "token_id": TEST_TOKEN_ID},
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        
        passed = (
            response.status_code == 200 and
            data.get("success") == True and
            data.get("action_code") == "MARKET_ANALYZE" and
            data.get("agent") == "DemandTrendAgent" and
            "portfolio" in data.get("data", {}) and
            "trending_types" in data.get("data", {}) and
            "recommendations" in data.get("data", {}) and
            data.get("show_action_button") == False  # Market analyze has no action
        )
        
        return TestResult(
            name="Market Analyze (POST /market/analyze)",
            passed=passed,
            response=data
        )
    except Exception as e:
        return TestResult(
            name="Market Analyze (POST /market/analyze)",
            passed=False,
            error=str(e)
        )


def test_review_analyze() -> TestResult:
    """Test review analysis endpoint."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/review/analyze",
            json={"listing_id": TEST_LISTING_ID},
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        
        passed = (
            response.status_code == 200 and
            data.get("success") == True and
            data.get("action_code") == "REVIEW_ANALYZE" and
            data.get("agent") == "ReviewAnalysisAgent" and
            "overall_satisfaction" in data.get("data", {}) and
            "rating_distribution" in data.get("data", {}) and
            "sentiment_analysis" in data.get("data", {}) and
            data.get("show_action_button") == False  # Review analyze has no action
        )
        
        return TestResult(
            name="Review Analyze (POST /review/analyze)",
            passed=passed,
            response=data
        )
    except Exception as e:
        return TestResult(
            name="Review Analyze (POST /review/analyze)",
            passed=False,
            error=str(e)
        )


def test_invalid_listing_id() -> TestResult:
    """Test with an invalid listing ID."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/pricing/analyze",
            json={"listing_id": "invalid-id-12345", "token_id": TEST_TOKEN_ID},
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        
        # Should either fail or return empty/error data
        passed = (
            response.status_code == 200 and
            (data.get("success") == False or 
             data.get("data", {}).get("error") is not None or
             "not found" in str(data).lower() or
             data.get("data", {}).get("current_price") is None)
        )
        
        return TestResult(
            name="Invalid Listing ID (POST /pricing/analyze)",
            passed=passed,
            response=data
        )
    except Exception as e:
        return TestResult(
            name="Invalid Listing ID (POST /pricing/analyze)",
            passed=False,
            error=str(e)
        )


def run_all_tests() -> bool:
    """Run all tests and return overall success status."""
    print_header("iShare Dashboard Agent API Tests")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Test Listing ID: {TEST_LISTING_ID}")
    print(f"Test Owner ID: {TEST_OWNER_ID}")
    
    # Check if server is running
    try:
        requests.get(f"{API_BASE_URL}/", timeout=5)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server!")
        print(f"   Make sure the server is running on {API_BASE_URL}")
        print("   Start with: uvicorn my_agent2.api.endpoints:app --reload --port 8001")
        return False
    
    # Run all tests
    tests = [
        test_health_check,
        test_get_action_codes,
        test_pricing_analyze,
        test_pricing_analyze_missing_param,
        test_pricing_apply,
        test_market_analyze,
        test_review_analyze,
        test_invalid_listing_id,
    ]
    
    results = []
    for test_func in tests:
        print(f"\nRunning: {test_func.__name__}...")
        result = test_func()
        results.append(result)
        print_result(result)
    
    # Print summary
    print_header("Test Summary")
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check the output above for details.")
        return False


def run_quick_test():
    """Run a quick smoke test of all endpoints."""
    print_header("Quick Smoke Test")
    
    endpoints = [
        ("GET", "/", None),
        ("GET", "/action-codes", None),
        ("POST", "/pricing/analyze", {"listing_id": TEST_LISTING_ID, "token_id": TEST_TOKEN_ID}),
        ("POST", "/pricing/apply", {"listing_id": TEST_LISTING_ID, "new_price": 100.0, "token_id": TEST_TOKEN_ID}),
        ("POST", "/market/analyze", {"owner_id": TEST_OWNER_ID, "token_id": TEST_TOKEN_ID}),
        ("POST", "/review/analyze", {"listing_id": TEST_LISTING_ID}),
    ]
    
    all_passed = True
    for method, endpoint, payload in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=30)
            else:
                response = requests.post(
                    f"{API_BASE_URL}{endpoint}",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {method} {endpoint} -> {response.status_code}")
            
            if response.status_code != 200:
                all_passed = False
                
        except Exception as e:
            print(f"❌ {method} {endpoint} -> ERROR: {e}")
            all_passed = False
    
    return all_passed


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test iShare Dashboard Agent API")
    parser.add_argument("--quick", action="store_true", help="Run quick smoke test only")
    parser.add_argument("--url", default=API_BASE_URL, help="API base URL")
    parser.add_argument("--listing", default=TEST_LISTING_ID, help="Test listing ID")
    parser.add_argument("--owner", type=int, default=TEST_OWNER_ID, help="Test owner ID")
    
    args = parser.parse_args()
    
    # Update configuration
    API_BASE_URL = args.url
    TEST_LISTING_ID = args.listing
    TEST_OWNER_ID = args.owner
    
    if args.quick:
        success = run_quick_test()
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
