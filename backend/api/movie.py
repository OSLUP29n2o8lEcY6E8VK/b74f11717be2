import time
import json

from backend.wsgi import remote, messages, message_types

from backend import api, movie
from backend.oauth2 import oauth2, Oauth2
from backend.swagger import swagger


class AddRequest(messages.Message):
    title = messages.StringField(1, required=True)


class MovieResponse(messages.Message):
    title = messages.StringField(1, required=True)
    year = messages.IntegerField(2, required=True)
    director = messages.StringField(3, required=True)
    poster = messages.StringField(4, required=True)
    imdb_id = messages.StringField(5, required=True)
    id = messages.StringField(6, required=True)


class ListRequest(messages.Message):
    page = messages.IntegerField(2, required=False, default=1)
    per_page = messages.IntegerField(1, required=False, default=10)


class ListResponse(messages.Message):
    movies = messages.StringField(1, required=True)


# https://cloud.google.com/appengine/docs/standard/python/tools/protorpc
class MoveListResponse(messages.Message):
    movies = messages.MessageField(MovieResponse, 1, repeated=True)


class DeleteRequest(messages.Message):
    id = messages.StringField(1, required=True)


def make_pages(movie_list, page_size):
    ret = []
    for i in range(0, len(movie_list), page_size):
        ret.append(movie_list[i : i + page_size])
    return ret


@api.endpoint(path="movie", title="Movie API")
class Movie(remote.Service):
    @swagger("Adds a movie")
    @remote.method(AddRequest, MovieResponse)
    def add(self, request):
        movie.Movie.fetch_movie_by_title(request.title, real=True)
        m = movie.Movie.get_by_title(request.title)
        # print("adding", request.title)
        return MovieResponse(
            title=m.title,
            year=m.year,
            director=m.director,
            poster=m.poster,
            imdb_id=m.imdb_id,
            id=m.id,
        )

    @swagger("Get a movie by title")
    @remote.method(AddRequest, MovieResponse)
    def bytitle(self, request):
        m = movie.Movie.get_by_title(request.title)
        return MovieResponse(
            title=m.title,
            year=m.year,
            director=m.director,
            poster=m.poster,
            imdb_id=m.imdb_id,
            id=m.id,
        )

    @swagger("Get a list of movies")
    @remote.method(ListRequest, MoveListResponse)
    def list(self, request):
        movies = list(movie.Movie.list())
        move_list_response = []
        for m in movies:
            new_movie = MovieResponse(
                title=m.title,
                year=m.year,
                director=m.director,
                poster=m.poster,
                imdb_id=m.imdb_id,
                id=m.id,
            )
            move_list_response.append(new_movie)
        move_list_response = sorted(
            move_list_response,
            key=lambda x: x.title,
        )
        pages = make_pages(move_list_response, request.per_page)
        if request.page < 1:
            page = 1
        elif request.page + 1 > len(pages):
            page = len(pages) - 1
        else:
            page = request.page - 1
        ret = MoveListResponse(movies=pages[page])
        return ret

    @swagger("Delete movie")
    @oauth2.required()
    @remote.method(DeleteRequest, message_types.VoidMessage)
    def delete(self, request):
        m = movie.Movie.get(request.id)
        m.key.delete()
        return message_types.VoidMessage()
