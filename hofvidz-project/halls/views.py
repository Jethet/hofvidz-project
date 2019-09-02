from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from .models import Hall, Video
from .forms import VideoForm, SearchForm
from django.http import Http404
import urllib
import requests
from django.forms.utils import ErrorList

YOUTUBE_API_KEY = 'AIzaSyAi8koxjjBI-An8Ayo62-sxQOaIEV6qfjk'

def home(request):
    return render(request, 'halls/home.html')

def dashboard(request):
    return render(request, 'halls/dashboard.html')

def add_video(request, pk):  #this is the pk of the hall the user is looking at
    # With formset_factory you can create a specified number of one form on the page:
    # code would be: VideoFormSet = formset_factory(VideoForm, extra=5)
    # !You would need to replace VideoForm with VideoFormSet in all the code!
    # The brackets mean that an object will be instantiated when calling this
    form = VideoForm()
    search_form = SearchForm()
    hall = Hall.objects.get(pk=pk)
    if not hall.user == request.user:
        raise Http404
    if request.method == 'POST':
        # Create a Video object (from .models Video is imported, above)
        filled_form = VideoForm(request.POST)
        if filled_form.is_valid():
            video = Video()
            video.hall = hall
            video.url = filled_form.cleaned_data['url']
            parsed_url = urllib.parse.urlparse(video.url)
            video_id = urllib.parse.parse_qs(parsed_url.query).get('v')
            if video_id:
                video.youtube_id = video_id[0]
                response = requests.get(f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={ video_id[0] }&key={YOUTUBE_API_KEY}')
                json = response.json()
                title = json['items'][0]['snippet']['title']
                print(title)
                #video.title =
                #video.save()

    return render(request, 'halls/add_video.html', {'form':form, 'search_form':search_form, 'hall':hall})

class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('dashboard')
    template_name = 'registration/signup.html'
    # This is meant to combine the user's signup with the creation of a hall:
    def form_valid(self, form):
        view = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return view

# CRUD: Create a hall:
class CreateHall(generic.CreateView):
    model = Hall
    fields = ['title']
    template_name = 'halls/create_hall.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        super(CreateHall, self).form_valid(form)
        return redirect('home')

# CRUD: Read - user should be able to see details, without changing anything
class DetailHall(generic.DetailView):
    model = Hall
    template_name = 'halls/detail_hall.html'

# CRUD: Update
class UpdateHall(generic.UpdateView):
    model = Hall
    template_name = 'halls/update_hall.html'
    fields = ['title']
    success_url = reverse_lazy('dashboard')

# CRUD: Delete
class DeleteHall(generic.DeleteView):
    model = Hall
    template_name = 'halls/delete_hall.html'
    success_url = reverse_lazy('dashboard')
