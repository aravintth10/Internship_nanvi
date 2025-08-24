from django import forms
from .models import Candidate

class CandidateSearchForm(forms.ModelForm):
    company = forms.CharField(max_length=255, required=False, label='Company')
    class Meta:
        model = Candidate
        fields = [
            'name', 'profile_photo', 'country', 'city', 'profession', 'date_of_birth',
            'primary_email', 'secondary_email', 'linkedin_profile', 'github_profile', 'facebook_profile', 'instagram_profile', 'twitter_profile', 'youtube_profile', 'pinterest_profile', 'reddit_profile', 'medium_profile', 'quora_profile', 'company'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Select Country'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city'}),
            'profession': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Select Industry'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'dd-mm-yyyy', 'type': 'date'}),
            'primary_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Primary email'}),
            'secondary_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Secondary email (optional)'}),
            'linkedin_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/username'}),
            'github_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/username'}),
            'facebook_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://facebook.com/username'}),
            'instagram_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/username'}),
            'twitter_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://twitter.com/username'}),
            'youtube_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://youtube.com/@username'}),
            'pinterest_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://pinterest.com/username'}),
            'reddit_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://reddit.com/user/username'}),
            'medium_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://medium.com/@username'}),
            'quora_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://quora.com/profile/username'}),
        } 