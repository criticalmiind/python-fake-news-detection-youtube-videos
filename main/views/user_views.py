import json
import sys
from datetime import datetime

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import BadHeaderError, send_mail
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from main.forms import ContactForm, NewUserForm, VideoForm
from main.models import Review, Stmt
from youtube_transcript_api import YouTubeTranscriptApi


def homepage(request):
    # if this is a POST request we need to process the form data
    form = VideoForm()
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = VideoForm(request.POST, auto_id=False)
		# check whether it's valid:
        if form.is_valid():
            print('form is valid')
    else:
        print('form is not valid')
        form = VideoForm(auto_id=False)
    return render(request=request, template_name='main/home.html', context={'video_form': form})

def contact(request):
	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():
			subject = "Website Inquiry"
			body = {
				'first_name': form.cleaned_data['first_name'], 
				'last_name': form.cleaned_data['last_name'], 
				'email': form.cleaned_data['email_address'], 
				'message':form.cleaned_data['message'], 
			}
			message = "\n".join(body.values())

			try:
				send_mail(subject, message, 'admin@example.com', ['admin@example.com']) 
			except BadHeaderError:
				return HttpResponse('Invalid header found.')

			messages.success(request, "Message sent." )
			return redirect ("main:homepage")
		messages.error(request, "Error. Message not sent.")

	form = ContactForm()
	return render(request, "main/contact.html", {'form':form})

def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("main:homepage")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm
	return render (request=request, template_name="main/register.html", context={"register_form":form})

def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("main:homepage")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="main/login.html", context={"login_form":form})

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("main:homepage")

def saveFact(request):
  stmt_text = request.POST['text']
  stmt_status = request.POST['status']
  stmt_date = datetime.now()
  stmt_owner = request.POST['owner']
  user = User.objects.get(id=stmt_owner)
  newStmt = Stmt(stmt_text=stmt_text, stmt_status=stmt_status, stmt_date=stmt_date, stmt_owner=user)
  result = newStmt.save(stmt_text, stmt_owner)
  res = {'done': 1}
  if (result == False):
    res['done'] = 0
  return JsonResponse(res)

def saveReview(request):
  text = request.POST['claim']
  status = request.POST['status']
  reason = request.POST['reason']
  submitter = request.POST['submitter']
  user = User.objects.get(id=submitter)
  newReview = Review(claim_text=text, claim_status=status, claim_reason=reason, claim_submitter=user)
  if Review.objects.filter(claim_text = text, claim_submitter = user):
      res = {'done': 0}
  else:
      try:
        newReview.save()
        db_status, db_prob, db_data = check_database_single(text)
        res = {'done': 1, 'db_status':db_status, 'db_prob':db_prob, 'db_data':db_data}
      except:
        res = {'done': 0}
  return JsonResponse(res)

def savedFacts(request):
  # user = User.objects.get(id=stmt_owner)
  objects = Stmt.objects.all().filter(stmt_owner=request.user)
  # print(objects)
  context = {"object_list": objects}
  return render(request, "main/savedFacts.html", context)

def deleteFact(request):
  stmt_text = request.POST['text']
  stmt_owner = request.POST['owner']
  user = User.objects.get(id=stmt_owner)
  newStmt = get_object_or_404(Stmt, stmt_text=stmt_text)
  result = newStmt.delete()

  res = {'done': 1}
  if (result == False):
    res['done'] = 0

  return JsonResponse(res)

def check_database_single(claim):
    cutoff = 0.5

    query = Review.objects.filter(claim_text = claim).values('claim_status', 'claim_reason')
    if query:
        true_p = round(query.filter(claim_status = 'True').count() / query.count(),2)
        print(true_p)
        if true_p > cutoff:
            db_status = ('True')
            db_prob= true_p
        else:
            db_status = 'False'
            db_prob = 1-true_p
        db = list(query)
    else:
        db_status = 'None'
        db_prob = -1
        db = None

    db_prob = round(100 *db_prob, 2)
    return db_status, db_prob, db