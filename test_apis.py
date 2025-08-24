#!/usr/bin/env python3
"""
API Testing Script for Person Profile Tracker
This script tests all APIs to ensure they're working properly
"""

import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Tokens
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

def test_github_api():
    """Test GitHub API functionality"""
    print("🔍 Testing GitHub API...")
    
    if not GITHUB_TOKEN:
        print("❌ GitHub token not set")
        return False
    
    try:
        # Test basic API access
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'ProfileSearchApp'
        }
        
        response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ GitHub API working - Authenticated as: {user_data.get('login', 'Unknown')}")
            
            # Test search functionality
            search_response = requests.get(
                'https://api.github.com/search/users?q=john&per_page=1',
                headers=headers,
                timeout=10
            )
            
            if search_response.status_code == 200:
                print("✅ GitHub search API working")
                return True
            else:
                print(f"❌ GitHub search API failed: {search_response.status_code}")
                return False
        else:
            print(f"❌ GitHub API authentication failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ GitHub API error: {e}")
        return False

def test_twitter_api():
    """Test Twitter API functionality"""
    print("🐦 Testing Twitter API...")
    
    if not TWITTER_BEARER_TOKEN:
        print("❌ Twitter token not set")
        return False
    
    try:
        headers = {
            'Authorization': f'Bearer {TWITTER_BEARER_TOKEN}',
            'User-Agent': 'ProfileSearchApp'
        }
        
        # Test basic API access
        response = requests.get(
            'https://api.twitter.com/2/users/by?usernames=twitter',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Twitter API working")
            return True
        elif response.status_code == 401:
            print("❌ Twitter token invalid")
            return False
        else:
            print(f"❌ Twitter API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Twitter API error: {e}")
        return False

def test_serpapi():
    """Test SerpAPI functionality"""
    print("🔍 Testing SerpAPI...")
    
    if not SERPAPI_KEY:
        print("❌ SerpAPI key not set")
        return False
    
    try:
        from serpapi import GoogleSearch
        
        params = {
            "engine": "google",
            "q": "test search",
            "api_key": SERPAPI_KEY,
            "num": 1
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" not in results:
            print("✅ SerpAPI working")
            return True
        else:
            print(f"❌ SerpAPI error: {results['error']}")
            return False
            
    except Exception as e:
        print(f"❌ SerpAPI error: {e}")
        return False

def test_youtube_api():
    """Test YouTube API functionality"""
    print("📺 Testing YouTube API...")
    
    if not YOUTUBE_API_KEY:
        print("❌ YouTube API key not set")
        return False
    
    try:
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q=test&key={YOUTUBE_API_KEY}&maxResults=1"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "items" in data:
                print("✅ YouTube API working")
                return True
            else:
                print("❌ YouTube API returned no items")
                return False
        else:
            print(f"❌ YouTube API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ YouTube API error: {e}")
        return False

def test_search_functionality():
    """Test the actual search functionality"""
    print("\n🔍 Testing Search Functionality...")
    
    # Import the search functions
    import sys
    sys.path.append('.')
    
    try:
        from profiles.views import github_search, linkedin_search, twitter_search
        
        test_cases = [
            {"name": "John Doe", "city": "New York"},
            {"name": "Jane Smith", "company": "Google"},
        ]
        
        for test_case in test_cases:
            print(f"\nTesting search for: {test_case}")
            
            # Test GitHub search
            try:
                github_results = github_search(
                    test_case["name"],
                    test_case.get("city"),
                    test_case.get("country")
                )
                print(f"  GitHub: Found {len(github_results)} results")
            except Exception as e:
                print(f"  GitHub: Error - {e}")
            
            # Test LinkedIn search
            try:
                linkedin_results = linkedin_search(
                    test_case["name"],
                    location=test_case.get("city"),
                    company=test_case.get("company")
                )
                print(f"  LinkedIn: Found {len(linkedin_results)} results")
            except Exception as e:
                print(f"  LinkedIn: Error - {e}")
            
            # Test Twitter search
            try:
                twitter_results = twitter_search(
                    test_case["name"],
                    location=test_case.get("city"),
                    company=test_case.get("company")
                )
                print(f"  Twitter: Found {len(twitter_results)} results")
            except Exception as e:
                print(f"  Twitter: Error - {e}")
            
            time.sleep(2)  # Rate limiting
            
    except Exception as e:
        print(f"❌ Search functionality test error: {e}")

def main():
    """Main test function"""
    print("🚀 Starting API Tests for Person Profile Tracker\n")
    
    # Test individual APIs
    github_ok = test_github_api()
    twitter_ok = test_twitter_api()
    serpapi_ok = test_serpapi()
    youtube_ok = test_youtube_api()
    
    # Test search functionality
    test_search_functionality()
    
    # Summary
    print("\n" + "="*50)
    print("📊 API Test Summary")
    print("="*50)
    print(f"GitHub API: {'✅ Working' if github_ok else '❌ Failed'}")
    print(f"Twitter API: {'✅ Working' if twitter_ok else '❌ Failed'}")
    print(f"SerpAPI: {'✅ Working' if serpapi_ok else '❌ Failed'}")
    print(f"YouTube API: {'✅ Working' if youtube_ok else '❌ Failed'}")
    
    working_apis = sum([github_ok, twitter_ok, serpapi_ok, youtube_ok])
    total_apis = 4
    
    print(f"\nOverall Status: {working_apis}/{total_apis} APIs working")
    
    if working_apis == 0:
        print("\n🚨 CRITICAL: No APIs are working!")
        print("Please check your environment variables and API tokens.")
    elif working_apis < total_apis:
        print(f"\n⚠️  WARNING: {total_apis - working_apis} APIs are not working.")
        print("Some search functionality may be limited.")
    else:
        print("\n🎉 All APIs are working correctly!")
    
    print("\n💡 Recommendations:")
    if not github_ok:
        print("- Set up GitHub token for better GitHub profile search")
    if not twitter_ok:
        print("- Set up Twitter token for Twitter profile search")
    if not serpapi_ok:
        print("- Set up SerpAPI key for web-based profile search")
    if not youtube_ok:
        print("- Set up YouTube API key for YouTube channel search")

if __name__ == "__main__":
    main()
