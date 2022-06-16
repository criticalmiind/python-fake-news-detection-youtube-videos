from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("contact", views.contact, name="contact"),
	path("register", views.register_request, name="register"),
	path("login", views.login_request, name="login"),
	path("logout", views.logout_request, name="logout"),
	path("video", views.getVideo, name="video"),
	path("captions", views.generate_claims, name="captions"),
	path("save", views.saveFact, name="saveFact"),
	path("delete", views.deleteFact, name="deleteFact"),
	path("savedFacts", views.savedFacts, name="savedFacts"),
	path("checkClaims", views.result_view, name="checkClaims"),
	path("saveReview", views.saveReview, name="saveReview"),
]
