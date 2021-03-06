from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, get_object_or_404
from .forms import CustomUserCreationForm
import requests
from bs4 import BeautifulSoup
import imdb
import urllib.request
import tmdbsimple as tmdb
from collections import Counter
tmdb.API_KEY = 'eb9f535abc9a24f973e9fdcb9a17c0bb'
from multiprocessing.pool import ThreadPool
import time

i = imdb.IMDb()
history = []
user_history = []
class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


def spider(url):
	word_list = []
	try:
		source_code = requests.get(url)
		plain_text =  source_code.text
		soup = BeautifulSoup(plain_text, features="lxml")
		for link in soup.find('div', attrs = {'id':'gnodMap'}):
		    title = link.string
		    word_list.append(title)
	except:
		pass
	return word_list

def info(movie_name):
	s = ''
	try:
		a = i.search_movie(movie_name)
		b = a[0]
		i.update(b)
		s = b.summary()
	except:
		search = tmdb.Search()
		response = search.movie(query=movie_name)
		for m in search.results:
			x = m['overview']
			s = x
			break

	return s

def image(movie_query):
	image_url = ''
	try:
		image_url = ''
		search = tmdb.Search()
		response = search.movie(query=movie_query)
		for s in search.results:
			x = s['poster_path']
			image_url = x
			break
	except:
		pass
	return image_url

def similar(number_of_movies, movie_name_list):
	similar_movie_list = []
	s = 1
	for _ in movie_name_list:
		try:
			movie_name_list.remove('\n')
		except:
			break

	for x in range(s, (number_of_movies+s)):
		try:
			mov_dict = {}
			a = movie_name_list[x]
			img = image(a)
			if len(img) >= 1:
				final_dict = {'name':a, 'link':img}
				mov_dict.update(final_dict)
				similar_movie_list.append(mov_dict)
			else:
				continue
		except:
			pass
	return similar_movie_list

def youtube_link(search_query):
	import urllib.request
	from bs4 import BeautifulSoup
	yt_link = ''
	textToSearch = search_query
	query = urllib.parse.quote(textToSearch)
	url = "https://www.youtube.com/results?search_query=" + query + "trailer"
	response = urllib.request.urlopen(url)
	print(response)
	html = response.read()
	soup = BeautifulSoup(html, 'html.parser')
	for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
	    x = ('https://www.youtube.com' + vid['href'])
	    yt_link = x
	    break

	return yt_link

def all_info(movie_query):

	try:
		image_url = ''
		movie_information = ''
		l = []
		mov_detail = {}
		search = tmdb.Search()
		response = search.movie(query=movie_query)
		for s in search.results:
			#image_url = s['poster_path']
			#movie_information = s['overview']
			mov_detail = s
			l = search.results
			l.remove(s)
			break
			
	except:
		pass

	return mov_detail, l


def search(request, query):
	query = query
	history.append(query)
	if request.user.is_authenticated == True:
		user = request.user.username
		user_history.append({user:query})

	url = "https://www.movie-map.com/" + query + ".html"
	#yt = 'https://www.youtube.com/results?search_query='+query+' trailer'
	yt = 'trailer/'
	#movie_list = spider(url)
	#movie_image = image(query)
	#similar_movies = similar(12, movie_list)
	#pool = ThreadPool(processes=3)
	#async_result = pool.apply_async(info, [query])
	#movie_info = async_result.get()
	everything = all_info(query)
	#yt = youtube_link(query)
	movie_detail = everything[0]
	similar_movies = everything[1]

	#recommended_movie = recommend()
	#recommended_movie = recommended_movie[0]
	#new_url = "https://www.movie-map.com/" + recommended_movie + ".html"
	#recommended_movies_list = spider(new_url)
	#recommended_movies_info = similar(10, recommended_movies_list)

	context = {
		'word': query,
		'movie': movie_detail,
		'similar': similar_movies,
		'youtube': yt,
		#'detail':movie_info,
		#'recommend': recommended_movies_info
	}
	return render(request, 'search.html', context)
	

def trailer(request, query):
	yt = youtube_link(query)
	return render(request, 'trailer.html', {'youtube':yt})