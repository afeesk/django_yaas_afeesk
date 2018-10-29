import re
from django.shortcuts import render,HttpResponseRedirect,Http404
from django.contrib.auth import logout,login,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import LoginForm, RegistrationForm, ModifyForm
from .models import EmailConfirmed

# Create your views here.

def logout_view(request):
	logout(request)
	messages.success(request, "Successful Logged out. Welcome back to Login again")
	return HttpResponseRedirect('%s'%(reverse("auth_login")))


def login_view(request):
	form = LoginForm(request.POST or None)
	btn = "Login"
	if form.is_valid():
		username = form.cleaned_data["username"]
		password = form.cleaned_data["password"]
		#parameters dont change, thats why d colors are different
		user = authenticate(username=username, password= password)

		login(request, user)
		messages.success(request, "Successful Logged in. Welcome back")
		return HttpResponseRedirect("/")
		#user.emailconfirmed.activate_user_email() Not necessary again on login
	context = {
		"form":form,
		"submit_btn": btn,
	}
	return render(request, "form.html", context)

def modify_view(request):
	if request.user.is_authenticated:
		user = request.user
		form = ModifyForm((request.POST or None), instance=user)
		btn  = "Modify"
		if form.is_valid():
			new_user = form.save(commit = False)
			new_user.save()
			form.save()
			#messages.success(request, "You have successful modiefied your")
			page_message = "You have successful modified your account details"
			context = {"page_message": page_message}
			return render(request, "modify_complete.html", context)
			#return HttpResponseRedirect("/")
		context = {
		"form":form,
		"submit_btn": btn,
			}
		return render(request, "form.html", context)
	else:
		return HttpResponseRedirect('%s'%(reverse("auth_login")))



def registration_view(request):
	form = RegistrationForm(request.POST or None)
	btn  = "Join"
	if form.is_valid():
		new_user = form.save(commit = False)
		#new_user.first_name = "Justin" this is where you can do stuff with the model form
		new_user.save()
		messages.success(request, "Successful registered. Please confirm your email now.")
		return HttpResponseRedirect("/")

	context = {
		"form":form,
		"submit_btn": btn,
	}
	return render(request, "form.html", context)


SHA1_RE = re.compile('^[a-f0-9]{40}$')
def activation_view(request, activation_key):
	if SHA1_RE.search(activation_key):
		print("activation key is real")
		try:
			instance = EmailConfirmed.objects.get(activation_key = activation_key)
		except EmailConfirmed.DoesNotExist:
			instance = None
			messages.success(request, "There was an error with your request")
			#raise Http404
			HttpResponseRedirect("/")
		if instance is not None and not instance.confirmed:
			page_message = "Confirmation successful! Welcome"
			instance.confirmed = True
			instance.activation_key = "Confirmed"
			instance.save()
			messages.success(request, "Successful confirmed. Please Log in")
		elif instance is not None and instance.confirmed:
			page_message = "Already Confirmed"
			messages.success(request, "Already confirmed")
		else:
			page_message = ""
		context = {"page_message": page_message}
		return render(request, "activation_complete.html", context)
	else:
		raise Http404



