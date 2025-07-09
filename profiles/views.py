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
import face_recognition

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def get_face_encoding(image_file):
    try:
        img = face_recognition.load_image_file(image_file)
        if img.ndim == 2:  # grayscale
            img = np.stack((img,)*3, axis=-1)
        elif img.shape[2] == 4:  # RGBA
            img = img[:, :, :3]
        img = np.ascontiguousarray(img)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            return encodings[0]
    except Exception as e:
        print(f"[DEBUG] Face encoding error: {e}")
    return None

def get_all_face_encodings(image_file):
    try:
        img = face_recognition.load_image_file(image_file)
        if img.ndim == 2:
            img = np.stack((img,)*3, axis=-1)
        elif img.shape[2] == 4:
            img = img[:, :, :3]
        img = np.ascontiguousarray(img)
        encodings = face_recognition.face_encodings(img)
        return encodings
    except Exception as e:
        print(f"[DEBUG] Face encoding error: {e}")
    return []

def compare_faces(user_encoding, profile_encodings):
    if user_encoding is None or not profile_encodings:
        return 0.0
    distances = [np.linalg.norm(user_encoding - enc) for enc in profile_encodings]
    if not distances:
        return 0.0
    min_distance = min(distances)
    similarity = max(0, 1 - min_distance / 0.6)
    return similarity

def calculate_string_similarity(str1, str2):
    # Simple Levenshtein distance-based similarity
    import difflib
    return difflib.SequenceMatcher(None, str1, str2).ratio()

def calculate_confidence_score(profile, search_data, user_face_encoding=None):
    score = 0
    # Name matching (20%)
    name_score = 0
    if profile.get('full_name') and search_data.get('name'):
        similarity = calculate_string_similarity(profile['full_name'].lower(), search_data['name'].lower())
        name_score = similarity * 20
    # Image matching (40%)
    image_score = 0
    image_similarity = 0
    if user_face_encoding is not None and profile.get('image_url'):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_img:
                img_data = requests.get(profile['image_url']).content
                temp_img.write(img_data)
                temp_img.flush()
                profile_face_encodings = get_all_face_encodings(temp_img.name)
                if profile_face_encodings:
                    image_similarity = compare_faces(user_face_encoding, profile_face_encodings)
                    image_score = image_similarity * 40
                else:
                    print(f"[DEBUG] No face found in profile image: {profile.get('image_url')}")
            os.unlink(temp_img.name)
        except Exception as e:
            print(f"[DEBUG] Image matching error: {e}")
    # Metadata matching (30%)
    meta_fields = ['city', 'country', 'profession']
    meta_matches = 0
    total_meta = 0
    for field in meta_fields:
        if search_data.get(field):
            total_meta += 1
            if profile.get('location') and search_data[field].lower() in profile['location'].lower():
                meta_matches += 1
            if field == 'profession' and profile.get('bio') and search_data[field].lower() in profile['bio'].lower():
                meta_matches += 1
    meta_score = (meta_matches / total_meta) * 30 if total_meta else 0
    # Activity (10%)
    activity_score = 0
    if profile.get('followers_count'):
        activity_score = min(profile['followers_count'] / 1000, 1) * 10
    total_score = name_score + image_score + meta_score + activity_score
    # Boost for strong image match
    if image_similarity > 0.9:
        total_score += 20
    elif image_similarity > 0.7:
        total_score += 10
    total_score = min(round(total_score, 2), 100)
    print(f"[DEBUG] Score breakdown for {profile.get('username')}: name={name_score}, image={image_score}, meta={meta_score}, activity={activity_score}, boost={(20 if image_similarity > 0.9 else 10 if image_similarity > 0.7 else 0)}, total={total_score}")
    return total_score

def github_search(full_name, city=None, country=None):
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'ProfileSearchApp'
    }
    def do_search(query):
        url = f'https://api.github.com/search/users?q={requests.utils.quote(query)}&per_page=5'
        print(f"[DEBUG] GitHub search URL: {url}")
        resp = requests.get(url, headers=headers)
        print(f"[DEBUG] GitHub response: {resp.status_code} {resp.text}")
        profiles = []
        if resp.ok:
            for user in resp.json().get('items', []):
                user_details = requests.get(f'https://api.github.com/users/{user["login"]}', headers=headers).json()
                print(f"[DEBUG] GitHub user details for {user['login']}: {user_details}")
                profiles.append({
                    'platform': 'GitHub',
                    'username': user['login'],
                    'full_name': user_details.get('name') or user['login'],
                    'bio': user_details.get('bio', ''),
                    'location': user_details.get('location', ''),
                    'company': user_details.get('company', ''),
                    'profile_url': user_details.get('html_url'),
                    'image_url': user_details.get('avatar_url'),
                    'followers_count': user_details.get('followers'),
                    'public_repos': user_details.get('public_repos'),
                    'email': user_details.get('email'),
                    'website': user_details.get('blog'),
                })
        return profiles
    # Try with all fields
    query = full_name
    if city:
        query += f' location:{city}'
    elif country:
        query += f' location:{country}'
    profiles = do_search(query)
    # Fallback: try with just name if no results
    if not profiles:
        print("[DEBUG] GitHub fallback: searching with name only")
        profiles = do_search(full_name)
    return profiles[:5]

def twitter_search(full_name):
    headers = {
        'Authorization': f'Bearer {TWITTER_BEARER_TOKEN}',
        'User-Agent': 'ProfileSearchApp'
    }
    def do_search(name):
        url = f'https://api.twitter.com/2/users/by?usernames={requests.utils.quote(name)}&user.fields=name,description,location,public_metrics,profile_image_url,url,verified'
        print(f"[DEBUG] Twitter search URL: {url}")
        resp = requests.get(url, headers=headers)
        print(f"[DEBUG] Twitter response: {resp.status_code} {resp.text}")
        profiles = []
        if resp.ok and resp.json().get('data'):
            for user in resp.json()['data']:
                print(f"[DEBUG] Twitter user details: {user}")
                profiles.append({
                    'platform': 'Twitter',
                    'username': user['username'],
                    'full_name': user['name'],
                    'bio': user.get('description', ''),
                    'location': user.get('location', ''),
                    'company': '',
                    'profile_url': f'https://twitter.com/{user["username"]}',
                    'image_url': user.get('profile_image_url', ''),
                    'followers_count': user.get('public_metrics', {}).get('followers_count', 0),
                    'website': user.get('url'),
                })
        return profiles
    profiles = do_search(full_name)
    # Fallback: try with just the first word if no results
    if not profiles and ' ' in full_name:
        first_word = full_name.split()[0]
        print(f"[DEBUG] Twitter fallback: searching with first word '{first_word}'")
        profiles = do_search(first_word)
    return profiles[:5]

def youtube_search(full_name):
    url = (
        f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={requests.utils.quote(full_name)}&key={YOUTUBE_API_KEY}&maxResults=5"
    )
    print(f"[DEBUG] YouTube search URL: {url}")
    resp = requests.get(url)
    print(f"[DEBUG] YouTube response: {resp.status_code} {resp.text}")
    profiles = []
    if resp.ok and resp.json().get('items'):
        for item in resp.json()['items']:
            snippet = item['snippet']
            channel_id = item['id']['channelId']
            # Get channel statistics
            stats_url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={YOUTUBE_API_KEY}"
            stats_resp = requests.get(stats_url)
            stats = stats_resp.json()['items'][0]['statistics'] if stats_resp.ok and stats_resp.json().get('items') else {}
            profiles.append({
                'platform': 'YouTube',
                'username': snippet.get('title'),
                'full_name': snippet.get('title'),
                'bio': snippet.get('description', ''),
                'location': '',
                'company': '',
                'profile_url': f"https://www.youtube.com/channel/{channel_id}",
                'image_url': snippet['thumbnails']['high']['url'] if 'high' in snippet['thumbnails'] else '',
                'followers_count': int(stats.get('subscriberCount', 0)),
                'public_repos': None,
                'email': None,
                'website': None,
            })
    return profiles

def google_linkedin_search(name):
    query = f'site:linkedin.com/in/ "{name}"'
    url = f'https://www.google.com/search?q={requests.utils.quote(query)}'
    print(f"[DEBUG] Google search for LinkedIn: {url}")
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'html.parser')
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'linkedin.com/in/' in href:
            # Extract the actual URL from Google's redirect
            start = href.find('https://www.linkedin.com/in/')
            if start != -1:
                end = href.find('&', start)
                return href[start:end] if end != -1 else href[start:]
    return None

def scrape_linkedin_profile(url):
    print(f"[DEBUG] Scraping LinkedIn profile: {url}")
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'html.parser')
    name = soup.find('h1')
    headline = soup.find('div', class_='text-body-medium')
    location = soup.find('span', class_='text-body-small')
    about = soup.find('div', {'id': 'about'})
    img = soup.find('img', {'class': 'profile-photo-edit__preview'})
    return {
        'platform': 'LinkedIn',
        'username': name.text.strip() if name else '',
        'full_name': name.text.strip() if name else '',
        'bio': headline.text.strip() if headline else '',
        'location': location.text.strip() if location else '',
        'company': '',
        'profile_url': url,
        'image_url': img['src'] if img and img.has_attr('src') else '',
        'followers_count': None,
        'public_repos': None,
        'email': None,
        'website': None,
    }

def linkedin_search(name, linkedin_url=None):
    profiles = []
    if linkedin_url:
        try:
            profiles.append(scrape_linkedin_profile(linkedin_url))
        except Exception as e:
            print(f"[DEBUG] LinkedIn scrape error: {e}")
    else:
        try:
            found_url = google_linkedin_search(name)
            if found_url:
                profiles.append(scrape_linkedin_profile(found_url))
        except Exception as e:
            print(f"[DEBUG] LinkedIn search/scrape error: {e}")
    return profiles

def google_social_search(name, site):
    query = f'site:{site} "{name}"'
    url = f'https://www.google.com/search?q={requests.utils.quote(query)}'
    print(f"[DEBUG] Google search for {site}: {url}")
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'lxml')
    for a in soup.find_all('a', href=True):
        href = a['href']
        if site in href:
            start = href.find(f'https://{site}/')
            if start != -1:
                end = href.find('&', start)
                return href[start:end] if end != -1 else href[start:]
    return None

def scrape_facebook_profile(url):
    print(f"[DEBUG] Scraping Facebook profile: {url}")
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'lxml')
    name = soup.find('title')
    img = soup.find('img', {'alt': 'Profile picture'})
    return {
        'platform': 'Facebook',
        'username': name.text.strip() if name else '',
        'full_name': name.text.strip() if name else '',
        'bio': '',
        'location': '',
        'company': '',
        'profile_url': url,
        'image_url': img['src'] if img and img.has_attr('src') else '',
        'followers_count': None,
        'public_repos': None,
        'email': None,
        'website': None,
    }

def facebook_search(name, facebook_url=None):
    profiles = []
    if facebook_url:
        try:
            profiles.append(scrape_facebook_profile(facebook_url))
        except Exception as e:
            print(f"[DEBUG] Facebook scrape error: {e}")
    else:
        try:
            found_url = google_social_search(name, 'facebook.com')
            if found_url:
                profiles.append(scrape_facebook_profile(found_url))
        except Exception as e:
            print(f"[DEBUG] Facebook search/scrape error: {e}")
    return profiles

def scrape_instagram_profile(url):
    print(f"[DEBUG] Scraping Instagram profile: {url}")
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'lxml')
    name = soup.find('title')
    img = soup.find('img', {'alt': 'Profile photo'})
    bio = soup.find('meta', {'name': 'description'})
    return {
        'platform': 'Instagram',
        'username': name.text.strip() if name else '',
        'full_name': name.text.strip() if name else '',
        'bio': bio['content'] if bio and bio.has_attr('content') else '',
        'location': '',
        'company': '',
        'profile_url': url,
        'image_url': img['src'] if img and img.has_attr('src') else '',
        'followers_count': None,
        'public_repos': None,
        'email': None,
        'website': None,
    }

def instagram_search(name, instagram_url=None):
    profiles = []
    if instagram_url:
        try:
            profiles.append(scrape_instagram_profile(instagram_url))
        except Exception as e:
            print(f"[DEBUG] Instagram scrape error: {e}")
    else:
        try:
            found_url = google_social_search(name, 'instagram.com')
            if found_url:
                profiles.append(scrape_instagram_profile(found_url))
        except Exception as e:
            print(f"[DEBUG] Instagram search/scrape error: {e}")
    return profiles

def candidate_search(request):
    form = CandidateSearchForm(request.POST or None, request.FILES or None)
    results = None
    api_profiles = []
    user_face_encoding = None
    if request.method == 'POST' and form.is_valid():
        search_data = form.cleaned_data
        # Get face encoding from uploaded photo
        if search_data.get('profile_photo'):
            user_face_encoding = get_face_encoding(search_data['profile_photo'])
        # Search GitHub
        api_profiles.extend(github_search(search_data['name'], search_data.get('city'), search_data.get('country')))
        # Search Twitter
        api_profiles.extend(twitter_search(search_data['name']))
        # Search YouTube
        api_profiles.extend(youtube_search(search_data['name']))
        # Search LinkedIn
        api_profiles.extend(linkedin_search(search_data['name'], search_data.get('linkedin_profile')))
        # Search Facebook
        api_profiles.extend(facebook_search(search_data['name']))
        # Search Instagram
        api_profiles.extend(instagram_search(search_data['name']))
        # Calculate confidence score
        for profile in api_profiles:
            profile['confidence'] = calculate_confidence_score(profile, search_data, user_face_encoding)
        # Sort by confidence
        api_profiles.sort(key=lambda x: x['confidence'], reverse=True)
        results = api_profiles
        # Optionally save the search locally
        if search_data.get('profile_photo'):
            Candidate.objects.create(**search_data)
    return render(request, 'profiles/candidate_search.html', {'form': form, 'results': results})
