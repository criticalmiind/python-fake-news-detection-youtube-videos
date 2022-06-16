from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Create your forms here.

class ContactForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email_address = forms.EmailField(max_length=150)
    message = forms.CharField(widget=forms.Textarea, max_length=2000)


class NewUserForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("username", "email", "password1", "password2")

	def save(self, commit=True):
		user = super(NewUserForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user

class VideoForm(forms.Form):
	video_url = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': "form-control form-control-lg form-control-borderless", 'Placeholder': 'Enter Youtube URL', 'type': 'search', 'id': 'url_input'}))

class ReviewForm(forms.Form):
	#review_text = forms.CharField(max_length=200, widget=forms.Textarea(attrs={'rows': 4, 'class': "form-control", 'Placeholder': 'Claim', 'id': 'review_text'}))
	CHOICES = [('True', 'True'), ('False', 'False')]
	review_status = forms.ChoiceField(required = True, widget=forms.RadioSelect, choices=CHOICES)
	review_reason = forms.CharField(required = True, max_length=200, widget=forms.Textarea(attrs={'rows': 4, 'class': "form-control", 'Placeholder': 'Reason', 'id': 'review_reason'}))