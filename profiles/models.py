from django.db import models

# Create your models here.

class Candidate(models.Model):
    name = models.CharField(max_length=255)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    profession = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    primary_email = models.EmailField(blank=True, null=True)
    secondary_email = models.EmailField(blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    github_profile = models.URLField(blank=True, null=True)
    facebook_profile = models.URLField(blank=True, null=True)
    instagram_profile = models.URLField(blank=True, null=True)
    twitter_profile = models.URLField(blank=True, null=True)
    youtube_profile = models.URLField(blank=True, null=True)
    pinterest_profile = models.URLField(blank=True, null=True)
    reddit_profile = models.URLField(blank=True, null=True)
    medium_profile = models.URLField(blank=True, null=True)
    quora_profile = models.URLField(blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

def twitter_search(full_name, twitter_url=None):
    profiles = []
    if twitter_url:
        profiles.append({
            'platform': 'Twitter',
            'username': '',
            'full_name': '',
            'bio': '',
            'location': '',
            'company': '',
            'profile_url': twitter_url,
            'image_url': '',
            'followers_count': None,
            'public_repos': None,
            'email': None,
            'website': None,
            'source': 'user-provided'
        })
        return profiles
    # ... existing API search logic ...
