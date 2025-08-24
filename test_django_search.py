#!/usr/bin/env python3
"""
Django Search Test Script
Tests the search functionality within Django environment
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'person_profile_tracker.settings')
django.setup()

from profiles.views import (
    github_search, 
    linkedin_search, 
    twitter_search, 
    calculate_confidence_score,
    calculate_string_similarity
)

def test_string_similarity():
    """Test the string similarity function"""
    print("🔍 Testing String Similarity...")
    
    test_cases = [
        ("John Doe", "John Doe", 1.0),
        ("John Doe", "john doe", 1.0),
        ("John Doe", "John Smith", 0.5),
        ("John Doe", "Jane Doe", 0.5),
        ("John Doe", "John", 0.8),
        ("John Doe", "Doe", 0.8),
    ]
    
    for str1, str2, expected in test_cases:
        result = calculate_string_similarity(str1, str2)
        status = "✅" if abs(result - expected) < 0.2 else "❌"
        print(f"  {status} '{str1}' vs '{str2}': {result:.2f} (expected ~{expected})")

def test_confidence_scoring():
    """Test the confidence scoring function"""
    print("\n🎯 Testing Confidence Scoring...")
    
    # Mock profile and search data
    profile = {
        'full_name': 'John Doe',
        'location': 'New York, USA',
        'company': 'Google',
        'bio': 'Software Engineer at Google',
        'followers_count': 1000,
        'image_url': 'https://example.com/image.jpg'
    }
    
    search_data = {
        'name': 'John Doe',
        'city': 'New York',
        'company': 'Google'
    }
    
    score = calculate_confidence_score(profile, search_data)
    print(f"  Confidence score: {score:.1f}/100")
    
    # Test with partial match
    profile2 = {
        'full_name': 'John Smith',
        'location': 'New York, USA',
        'company': 'Microsoft',
        'bio': 'Developer',
        'followers_count': 100,
        'image_url': ''
    }
    
    score2 = calculate_confidence_score(profile2, search_data)
    print(f"  Partial match score: {score2:.1f}/100")

def test_github_search():
    """Test GitHub search functionality"""
    print("\n🐙 Testing GitHub Search...")
    
    test_cases = [
        {"name": "John Doe", "city": "New York"},
        {"name": "Jane Smith", "company": "Google"},
    ]
    
    for test_case in test_cases:
        print(f"\n  Searching for: {test_case['name']}")
        try:
            results = github_search(
                test_case["name"],
                test_case.get("city"),
                test_case.get("country")
            )
            print(f"    Found {len(results)} GitHub profiles")
            
            for i, result in enumerate(results[:3]):  # Show first 3 results
                print(f"    {i+1}. {result.get('full_name', 'N/A')} (@{result.get('username', 'N/A')})")
                print(f"       Location: {result.get('location', 'N/A')}")
                print(f"       Company: {result.get('company', 'N/A')}")
                print(f"       Followers: {result.get('followers_count', 'N/A')}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")

def test_linkedin_search():
    """Test LinkedIn search functionality"""
    print("\n💼 Testing LinkedIn Search...")
    
    test_cases = [
        {"name": "John Doe", "city": "New York"},
        {"name": "Jane Smith", "company": "Google"},
    ]
    
    for test_case in test_cases:
        print(f"\n  Searching for: {test_case['name']}")
        try:
            results = linkedin_search(
                test_case["name"],
                location=test_case.get("city"),
                company=test_case.get("company")
            )
            print(f"    Found {len(results)} LinkedIn profiles")
            
            for i, result in enumerate(results[:3]):  # Show first 3 results
                print(f"    {i+1}. {result.get('full_name', 'N/A')}")
                print(f"       Bio: {result.get('bio', 'N/A')[:50]}...")
                print(f"       Location: {result.get('location', 'N/A')}")
                print(f"       URL: {result.get('profile_url', 'N/A')}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")

def test_twitter_search():
    """Test Twitter search functionality"""
    print("\n🐦 Testing Twitter Search...")
    
    test_cases = [
        {"name": "John Doe", "city": "New York"},
        {"name": "Jane Smith", "company": "Google"},
    ]
    
    for test_case in test_cases:
        print(f"\n  Searching for: {test_case['name']}")
        try:
            results = twitter_search(
                test_case["name"],
                location=test_case.get("city"),
                company=test_case.get("company")
            )
            print(f"    Found {len(results)} Twitter profiles")
            
            for i, result in enumerate(results[:3]):  # Show first 3 results
                print(f"    {i+1}. {result.get('full_name', 'N/A')} (@{result.get('username', 'N/A')})")
                print(f"       Bio: {result.get('bio', 'N/A')[:50]}...")
                print(f"       Followers: {result.get('followers_count', 'N/A')}")
                print(f"       URL: {result.get('profile_url', 'N/A')}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")

def test_full_search_simulation():
    """Simulate a full search with all platforms"""
    print("\n🚀 Testing Full Search Simulation...")
    
    search_data = {
        'name': 'John Doe',
        'city': 'New York',
        'company': 'Google'
    }
    
    print(f"Searching for: {search_data['name']}")
    print(f"Location: {search_data['city']}")
    print(f"Company: {search_data['company']}")
    
    all_results = []
    
    # GitHub search
    try:
        github_results = github_search(search_data['name'], search_data['city'])
        all_results.extend([(r, 'GitHub') for r in github_results])
        print(f"  GitHub: {len(github_results)} results")
    except Exception as e:
        print(f"  GitHub: Error - {e}")
    
    # LinkedIn search
    try:
        linkedin_results = linkedin_search(search_data['name'], location=search_data['city'], company=search_data['company'])
        all_results.extend([(r, 'LinkedIn') for r in linkedin_results])
        print(f"  LinkedIn: {len(linkedin_results)} results")
    except Exception as e:
        print(f"  LinkedIn: Error - {e}")
    
    # Twitter search
    try:
        twitter_results = twitter_search(search_data['name'], location=search_data['city'], company=search_data['company'])
        all_results.extend([(r, 'Twitter') for r in twitter_results])
        print(f"  Twitter: {len(twitter_results)} results")
    except Exception as e:
        print(f"  Twitter: Error - {e}")
    
    # Calculate confidence scores
    print(f"\n📊 Calculating confidence scores for {len(all_results)} total results...")
    
    scored_results = []
    for profile, platform in all_results:
        try:
            confidence = calculate_confidence_score(profile, search_data)
            profile['confidence'] = confidence
            profile['platform_display'] = platform
            scored_results.append(profile)
        except Exception as e:
            print(f"  Error calculating score for {platform} profile: {e}")
    
    # Sort by confidence score
    scored_results.sort(key=lambda x: x.get('confidence', 0), reverse=True)
    
    print(f"\n🏆 Top Results (sorted by confidence):")
    for i, result in enumerate(scored_results[:5]):
        print(f"  {i+1}. {result.get('full_name', 'N/A')} ({result['platform_display']})")
        print(f"     Confidence: {result.get('confidence', 0):.1f}/100")
        print(f"     Username: {result.get('username', 'N/A')}")
        print(f"     Location: {result.get('location', 'N/A')}")
        print(f"     Company: {result.get('company', 'N/A')}")
        print()

def main():
    """Main test function"""
    print("🚀 Starting Django Search Tests\n")
    
    # Test individual components
    test_string_similarity()
    test_confidence_scoring()
    
    # Test individual platform searches
    test_github_search()
    test_linkedin_search()
    test_twitter_search()
    
    # Test full search simulation
    test_full_search_simulation()
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
