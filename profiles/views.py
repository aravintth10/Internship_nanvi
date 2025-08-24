import requests
import tempfile
import os
from bs4 import BeautifulSoup
from django.shortcuts import render
from .forms import CandidateSearchForm
from .models import Candidate
from django.conf import settings
from PIL import Image
import numpy as np
from .face_recognition_improved import (
    initialize_face_recognition, 
    register_face_from_url, 
    match_face_from_url, 
    get_best_match_score,
    clear_registered_faces,
    is_initialized,
    register_face_from_path,
    match_face_from_path
)
import random
import time
from serpapi import GoogleSearch
import re
import json
from urllib.parse import urlparse, parse_qs

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
]

print("[DEBUG] SERPAPI_KEY loaded:", "***" if SERPAPI_KEY else "NOT SET")
print("[DEBUG] GITHUB_TOKEN loaded:", "***" if GITHUB_TOKEN else "NOT SET")
print("[DEBUG] TWITTER_BEARER_TOKEN loaded:", "***" if TWITTER_BEARER_TOKEN else "NOT SET")

def calculate_string_similarity(str1, str2):
    """Improved string similarity using multiple algorithms"""
    if not str1 or not str2:
        return 0
    
    # Normalize strings
    str1 = re.sub(r'[^\w\s]', '', str1.lower().strip())
    str2 = re.sub(r'[^\w\s]', '', str2.lower().strip())
    
    if str1 == str2:
        return 1.0
    
    # Use difflib for sequence matching
    import difflib
    similarity = difflib.SequenceMatcher(None, str1, str2).ratio()
    
    # Check for partial matches
    words1 = set(str1.split())
    words2 = set(str2.split())
    
    if words1 and words2:
        word_overlap = len(words1.intersection(words2)) / max(len(words1), len(words2))
        similarity = max(similarity, word_overlap * 0.8)
    
    return similarity

def calculate_confidence_score(profile, search_data, uploaded_image_path=None):
    """Improved confidence score calculation with better weighting"""
    score = 0
    breakdown = {}
    
    # Name matching (30% weight)
    name_score = 0
    if profile.get('full_name') and search_data.get('name'):
        similarity = calculate_string_similarity(profile['full_name'], search_data['name'])
        name_score = similarity * 30
        breakdown['name'] = f"{similarity:.2f} ({name_score:.1f})"
    
    # Image matching (35% weight) - only if image is available
    image_score = 0
    image_similarity = 0
    
    if uploaded_image_path and profile.get('image_url'):
        try:
            # Download profile image to temp file if it's a URL
            if profile['image_url'].startswith('http'):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_img:
                    response = requests.get(profile['image_url'], timeout=10)
                    if response.status_code == 200:
                        temp_img.write(response.content)
                        temp_img.flush()
                        profile_image_path = temp_img.name
                    else:
                        profile_image_path = None
            else:
                profile_image_path = profile['image_url']
            
            if profile_image_path and os.path.exists(profile_image_path):
                # Register the profile image
                clear_registered_faces()
                register_face_from_path(profile_image_path, profile.get('username', 'unknown'))
                # Match against the uploaded image
                matches = match_face_from_path(uploaded_image_path, top_k=1)
                if matches:
                    image_similarity = matches[0]['score']
                    image_score = image_similarity * 35
                    breakdown['image'] = f"{image_similarity:.2f} ({image_score:.1f})"
                else:
                    breakdown['image'] = "No match (0.0)"
                
                # Clean up temp file
                if profile['image_url'].startswith('http') and os.path.exists(profile_image_path):
                    os.unlink(profile_image_path)
        except Exception as e:
            print(f"[DEBUG] Image matching error: {e}")
            breakdown['image'] = f"Error: {str(e)[:50]}"
    
    # Metadata matching (25% weight)
    meta_score = 0
    meta_matches = 0
    total_meta = 0
    
    # Location matching
    if search_data.get('city') or search_data.get('country'):
        total_meta += 1
        profile_location = (profile.get('location') or '').lower()
        search_location = (search_data.get('city') or search_data.get('country') or '').lower()
        
        if search_location and profile_location:
            if search_location in profile_location or profile_location in search_location:
                meta_matches += 1
                breakdown['location'] = "Match"
            else:
                breakdown['location'] = "No match"
    
    # Company matching
    if search_data.get('company'):
        total_meta += 1
        profile_company = (profile.get('company') or profile.get('bio') or '').lower()
        search_company = search_data.get('company').lower()
        
        if search_company in profile_company:
            meta_matches += 1
            breakdown['company'] = "Match"
        else:
            breakdown['company'] = "No match"
    
    # Profession matching
    if search_data.get('profession'):
        total_meta += 1
        profile_bio = (profile.get('bio') or '').lower()
        search_profession = search_data.get('profession').lower()
        
        if search_profession in profile_bio:
            meta_matches += 1
            breakdown['profession'] = "Match"
        else:
            breakdown['profession'] = "No match"
    
    if total_meta > 0:
        meta_score = (meta_matches / total_meta) * 25
        breakdown['metadata'] = f"{meta_matches}/{total_meta} ({meta_score:.1f})"
    
    # Activity score (10% weight)
    activity_score = 0
    if profile.get('followers_count'):
        followers = profile['followers_count']
        if followers > 10000:
            activity_score = 10
        elif followers > 1000:
            activity_score = 7
        elif followers > 100:
            activity_score = 4
        else:
            activity_score = 1
        breakdown['activity'] = f"{followers} followers ({activity_score:.1f})"
    
    total_score = name_score + image_score + meta_score + activity_score
    
    # Boost for strong matches
    boost = 0
    if image_similarity > 0.9:
        boost = 15
    elif image_similarity > 0.7:
        boost = 10
    elif image_similarity > 0.5:
        boost = 5
    
    if name_score > 25:
        boost += 5
    
    total_score += boost
    total_score = min(round(total_score, 2), 100)
    
    breakdown['total'] = f"{total_score:.1f}"
    breakdown['boost'] = f"+{boost}"
    
    print(f"[DEBUG] Score breakdown for {profile.get('username')}: {breakdown}")
    return total_score

# --- IMPROVED GITHUB SEARCH ---
def github_search(full_name, city=None, country=None, github_url=None):
    """Enhanced GitHub search with better error handling and fallbacks"""
    profiles = []
    
    # Direct URL search
    if github_url and 'github.com/' in github_url:
        try:
            username = github_url.rstrip('/').split('/')[-1]
            if username:
                profile = fetch_github_user_details(username)
                if profile:
                    profiles.append(profile)
                    return profiles
        except Exception as e:
            print(f"[DEBUG] GitHub direct URL error: {e}")
    
    # API search (if token available)
    if GITHUB_TOKEN:
        try:
            api_profiles = github_api_search(full_name, city, country)
            profiles.extend(api_profiles)
        except Exception as e:
            print(f"[DEBUG] GitHub API search error: {e}")
    
    # Fallback: Web scraping search
    if not profiles:
        try:
            scraped_profiles = github_web_search(full_name, city, country)
            profiles.extend(scraped_profiles)
        except Exception as e:
            print(f"[DEBUG] GitHub web search error: {e}")
    
    return profiles[:5]  # Limit results

def fetch_github_user_details(username):
    """Fetch detailed GitHub user information"""
    if not GITHUB_TOKEN:
        return None
    
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'ProfileSearchApp'
    }
    
    try:
        response = requests.get(f'https://api.github.com/users/{username}', headers=headers, timeout=10)
        if response.status_code == 200:
            user_data = response.json()
            return {
                'platform': 'GitHub',
                'username': user_data.get('login'),
                'full_name': user_data.get('name') or user_data.get('login'),
                'bio': user_data.get('bio', ''),
                'location': user_data.get('location', ''),
                'company': user_data.get('company', ''),
                'profile_url': user_data.get('html_url'),
                'image_url': user_data.get('avatar_url'),
                'followers_count': user_data.get('followers'),
                'public_repos': user_data.get('public_repos'),
                'email': user_data.get('email'),
                'website': user_data.get('blog'),
                'source': 'api'
            }
    except Exception as e:
        print(f"[DEBUG] Error fetching GitHub user {username}: {e}")
    
    return None

def github_api_search(full_name, city=None, country=None):
    """Search GitHub using API"""
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'ProfileSearchApp'
    }
    
    profiles = []
    queries = []
    
    # Build search queries
    queries.append(f'"{full_name}"')
    
    name_parts = full_name.split()
    if len(name_parts) > 1:
        queries.append(f'"{name_parts[0]}" "{name_parts[-1]}"')
        queries.append(f'"{name_parts[0]}"')
        queries.append(f'"{name_parts[-1]}"')
    
    if city:
        queries.append(f'"{full_name}" location:"{city}"')
    elif country:
        queries.append(f'"{full_name}" location:"{country}"')
    
    for query in queries:
        try:
            url = f'https://api.github.com/search/users?q={requests.utils.quote(query)}&per_page=5&sort=followers'
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                for user in data.get('items', []):
                    profile = fetch_github_user_details(user['login'])
                    if profile:
                        profiles.append(profile)
                
                if profiles:
                    break  # Found results, stop searching
            elif response.status_code == 403:
                print("[DEBUG] GitHub API rate limit exceeded")
                break
                
        except Exception as e:
            print(f"[DEBUG] GitHub API query error for '{query}': {e}")
            continue
    
    return profiles

def github_web_search(full_name, city=None, country=None):
    """Fallback GitHub search using web scraping"""
    profiles = []
    
    try:
        # Use SerpAPI for web search
        if SERPAPI_KEY:
            search_query = f'site:github.com "{full_name}"'
            if city:
                search_query += f' "{city}"'
            elif country:
                search_query += f' "{country}"'
            
            params = {
                "engine": "google",
                "q": search_query,
                "api_key": SERPAPI_KEY,
                "num": 5
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            for result in results.get("organic_results", []):
                link = result.get("link")
                if link and "github.com" in link:
                    username = link.split("github.com/")[-1].split("/")[0]
                    if username and username != "search":
                        profile = fetch_github_user_details(username)
                        if profile:
                            profiles.append(profile)
    except Exception as e:
        print(f"[DEBUG] GitHub web search error: {e}")
    
    return profiles

# --- IMPROVED LINKEDIN SEARCH ---
def linkedin_search(name, linkedin_url=None, location=None, company=None):
    """Enhanced LinkedIn search with better scraping"""
    profiles = []
    
    # Direct URL
    if linkedin_url and 'linkedin.com/in/' in linkedin_url:
        try:
            profile = scrape_linkedin_profile(linkedin_url)
            if profile:
                profile['source'] = 'user-provided'
                profiles.append(profile)
        except Exception as e:
            print(f"[DEBUG] LinkedIn direct URL error: {e}")
    
    # Web search
    if SERPAPI_KEY:
        try:
            search_query = f'site:linkedin.com/in/ "{name}"'
            if location:
                search_query += f' "{location}"'
            if company:
                search_query += f' "{company}"'
            
            params = {
                "engine": "google",
                "q": search_query,
                "api_key": SERPAPI_KEY,
                "num": 3
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            for result in results.get("organic_results", []):
                link = result.get("link")
                if link and "linkedin.com/in/" in link:
                    try:
                        profile = scrape_linkedin_profile(link)
                        if profile:
                            profile['source'] = 'web-search'
                            profiles.append(profile)
                    except Exception as e:
                        print(f"[DEBUG] LinkedIn scrape error for {link}: {e}")
        except Exception as e:
            print(f"[DEBUG] LinkedIn search error: {e}")
    
    return profiles

def scrape_linkedin_profile(url):
    """Improved LinkedIn profile scraping"""
    try:
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract name
        name = ""
        name_selectors = [
            'h1.text-heading-xlarge',
            '.text-heading-xlarge',
            'h1',
            '.pv-text-details__left-panel h1'
        ]
        
        for selector in name_selectors:
            name_elem = soup.select_one(selector)
            if name_elem:
                name = name_elem.get_text().strip()
                break
        
        # Extract headline
        headline = ""
        headline_selectors = [
            '.text-body-medium.break-words',
            '.pv-text-details__left-panel .text-body-medium',
            '.text-body-medium'
        ]
        
        for selector in headline_selectors:
            headline_elem = soup.select_one(selector)
            if headline_elem:
                headline = headline_elem.get_text().strip()
                break
        
        # Extract location
        location = ""
        location_selectors = [
            '.text-body-small.inline.t-black--light.break-words',
            '.pv-text-details__left-panel .text-body-small'
        ]
        
        for selector in location_selectors:
            location_elem = soup.select_one(selector)
            if location_elem:
                location = location_elem.get_text().strip()
                break
        
        # Extract image
        image_url = ""
        img_selectors = [
            'img.pv-top-card-profile-picture__image',
            '.pv-top-card__photo img',
            'img[alt*="profile"]'
        ]
        
        for selector in img_selectors:
            img_elem = soup.select_one(selector)
            if img_elem and img_elem.get('src'):
                image_url = img_elem['src']
                break
        
        return {
            'platform': 'LinkedIn',
            'username': name,
            'full_name': name,
            'bio': headline,
            'location': location,
            'company': '',
            'profile_url': url,
            'image_url': image_url,
            'followers_count': None,
            'public_repos': None,
            'email': None,
            'website': None,
        }
        
    except Exception as e:
        print(f"[DEBUG] LinkedIn scrape error: {e}")
        return None

# --- IMPROVED TWITTER SEARCH ---
def twitter_search(full_name, twitter_url=None, location=None, company=None):
    """Enhanced Twitter search with better error handling"""
    profiles = []
    
    # Direct URL
    if twitter_url and 'twitter.com/' in twitter_url:
        username = twitter_url.split('twitter.com/')[-1].split('/')[0]
        if username:
            profiles.append({
                'platform': 'Twitter',
                'username': username,
                'full_name': full_name,
                'bio': '',
                'location': location or '',
                'company': company or '',
                'profile_url': twitter_url,
                'image_url': '',
                'followers_count': None,
                'public_repos': None,
                'email': None,
                'website': None,
                'source': 'user-provided'
            })
            return profiles
    
    # API search (if available)
    if TWITTER_BEARER_TOKEN:
        try:
            api_profiles = twitter_api_search(full_name)
            profiles.extend(api_profiles)
        except Exception as e:
            print(f"[DEBUG] Twitter API search error: {e}")
    
    # Web search fallback
    if not profiles and SERPAPI_KEY:
        try:
            web_profiles = twitter_web_search(full_name, location, company)
            profiles.extend(web_profiles)
        except Exception as e:
            print(f"[DEBUG] Twitter web search error: {e}")
    
    return profiles

def twitter_api_search(full_name):
    """Search Twitter using API"""
    headers = {
        'Authorization': f'Bearer {TWITTER_BEARER_TOKEN}',
        'User-Agent': 'ProfileSearchApp'
    }
    
    profiles = []
    name_parts = full_name.split()
    
    # Try different username variations
    username_variations = [full_name.replace(' ', ''), full_name.replace(' ', '_')]
    if len(name_parts) > 1:
        username_variations.extend([name_parts[0], name_parts[-1]])
    
    for username in username_variations:
        try:
            url = f'https://api.twitter.com/2/users/by?usernames={username}&user.fields=name,description,location,public_metrics,profile_image_url,url,verified'
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    for user in data['data']:
                        profiles.append({
                            'platform': 'Twitter',
                            'username': user['username'],
                            'full_name': user['name'],
                            'bio': user.get('description', ''),
                            'location': user.get('location', ''),
                            'company': '',
                            'profile_url': f'https://twitter.com/{user["username"]}',
                            'image_url': user.get('profile_image_url', ''),
                            'followers_count': user.get('public_metrics', {}).get('followers_count'),
                            'public_repos': None,
                            'email': None,
                            'website': user.get('url'),
                            'source': 'api'
                        })
                    break  # Found results
            elif response.status_code == 429:
                print("[DEBUG] Twitter API rate limited")
                break
                
        except Exception as e:
            print(f"[DEBUG] Twitter API error for {username}: {e}")
            continue
    
    return profiles

def twitter_web_search(full_name, location=None, company=None):
    """Web search for Twitter profiles"""
    profiles = []
    
    try:
        search_query = f'site:twitter.com "{full_name}"'
        if location:
            search_query += f' "{location}"'
        if company:
            search_query += f' "{company}"'
        
        params = {
            "engine": "google",
            "q": search_query,
            "api_key": SERPAPI_KEY,
            "num": 3
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        for result in results.get("organic_results", []):
            link = result.get("link")
            if link and "twitter.com/" in link:
                username = link.split("twitter.com/")[-1].split("/")[0]
                if username and username not in ['search', 'hashtag']:
                    profiles.append({
                        'platform': 'Twitter',
                        'username': username,
                        'full_name': full_name,
                        'bio': '',
                        'location': location or '',
                        'company': company or '',
                        'profile_url': f'https://twitter.com/{username}',
                        'image_url': '',
                        'followers_count': None,
                        'public_repos': None,
                        'email': None,
                        'website': None,
                        'source': 'web-search'
                    })
    except Exception as e:
        print(f"[DEBUG] Twitter web search error: {e}")
    
    return profiles

# --- MAIN SEARCH FUNCTION ---
def candidate_search(request):
    """Main search function with improved error handling and accuracy"""
    form = CandidateSearchForm(request.POST or None, request.FILES or None)
    results = []
    uploaded_image_path = None
    
    if request.method == 'POST' and form.is_valid():
        search_data = form.cleaned_data
        print(f"[DEBUG] Search data: {search_data}")
        
        # Initialize face recognition if needed
        if not is_initialized():
            try:
                initialize_face_recognition()
            except Exception as e:
                print(f"[DEBUG] Face recognition initialization error: {e}")
        
        # Handle uploaded image
        if search_data.get('profile_photo'):
            try:
                uploaded_image_path = f"uploads/{search_data['profile_photo'].name}"
                os.makedirs("uploads", exist_ok=True)
                with open(uploaded_image_path, 'wb+') as destination:
                    for chunk in search_data['profile_photo'].chunks():
                        destination.write(chunk)
                print(f"[DEBUG] Uploaded image saved to: {uploaded_image_path}")
            except Exception as e:
                print(f"[DEBUG] Error saving uploaded image: {e}")
                uploaded_image_path = None
        
        # Deduplication set
        seen_profiles = set()
        
        def dedup_key(profile, platform):
            username = (profile.get('username') or '').strip().lower()
            url = (profile.get('profile_url') or '').strip().lower()
            return f"{platform}:{username or url}"
        
        # Search GitHub
        print("[DEBUG] Searching GitHub...")
        github_profiles = github_search(
            search_data['name'],
            search_data.get('city'),
            search_data.get('country'),
            search_data.get('github_profile')
        )
        
        for profile in github_profiles:
            key = dedup_key(profile, 'GitHub')
            if key not in seen_profiles:
                profile['confidence'] = calculate_confidence_score(profile, search_data, uploaded_image_path)
                profile['platform_display'] = 'GitHub'
                results.append(profile)
                seen_profiles.add(key)
        
        # Search LinkedIn
        print("[DEBUG] Searching LinkedIn...")
        linkedin_profiles = linkedin_search(
            search_data['name'],
            search_data.get('linkedin_profile'),
            search_data.get('city'),
            search_data.get('company')
        )
        
        for profile in linkedin_profiles:
            key = dedup_key(profile, 'LinkedIn')
            if key not in seen_profiles:
                profile['confidence'] = calculate_confidence_score(profile, search_data, uploaded_image_path)
                profile['platform_display'] = 'LinkedIn'
                results.append(profile)
                seen_profiles.add(key)
        
        # Search Twitter
        print("[DEBUG] Searching Twitter...")
        twitter_profiles = twitter_search(
            search_data['name'],
            search_data.get('twitter_profile'),
            search_data.get('city'),
            search_data.get('company')
        )
        
        for profile in twitter_profiles:
            key = dedup_key(profile, 'Twitter')
            if key not in seen_profiles:
                profile['confidence'] = calculate_confidence_score(profile, search_data, uploaded_image_path)
                profile['platform_display'] = 'Twitter'
                results.append(profile)
                seen_profiles.add(key)
        
        # Sort results by confidence score
        results.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        print(f"[DEBUG] Found {len(results)} total profiles")
        
        # Save search to database
        try:
            if search_data.get('profile_photo'):
                Candidate.objects.create(**search_data)
        except Exception as e:
            print(f"[DEBUG] Error saving to database: {e}")
    
    return render(request, 'profiles/candidate_search.html', {'form': form, 'results': results})
