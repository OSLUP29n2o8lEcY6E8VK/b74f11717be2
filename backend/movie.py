import requests
import dotenv
import os

from google.cloud import ndb
from backend import error

from backend.favorite_movies import favorites
from backend.fake_data import fake


class NotFound(error.Error):
    pass


dotenv.load_dotenv()

API_KEY = os.getenv("API_KEY")
URL = "https://www.omdbapi.com/"


class Movie(ndb.Model):
    title = ndb.StringProperty()
    year = ndb.IntegerProperty()
    director = ndb.StringProperty()
    poster = ndb.StringProperty()
    imdb_id = ndb.StringProperty()

    @staticmethod
    def fetch_if_empty(real=True):
        if Movie.is_empty():
            Movie.fetch_movies(real)

    @staticmethod
    def fetch_movies(real=False):
        if real:
            Movie.real_fetch_movies()
        else:
            Movie.fake_fetch_movies()

    @staticmethod
    def fake_fetch_movies():
        for f in fake:
            new_move = Movie(
                title=f["Title"],
                year=int(f["Year"]),
                director=f["Director"],
                poster=f["Poster"],
                imdb_id=f["imdbID"],
            )
            new_move.put()

    @staticmethod
    def real_fetch_movies():
        for f in favorites:
            result = requests.get(URL, {"i": f, "apikey": API_KEY})
            j = result.json()
            new_move = Movie(
                title=j["Title"],
                year=int(j["Year"]),
                director=j["Director"],
                poster=j["Poster"],
                imdb_id=j["imdbID"],
            )
            new_move.put()

    @staticmethod
    def fetch_movie_by_title(title, real=True):
        Movie.fetch_if_empty()
        if real:
            m = Movie.real_fetch_movie_by_title(title)
        else:
            m = Movie.fake_fetch_movie_by_title(title)
        if m and not Movie.get_by_imdb_id(m["imdbID"]):
            new_move = Movie(
                title=m["Title"],
                year=int(m["Year"]),
                director=m["Director"],
                poster=m["Poster"],
                imdb_id=m["imdbID"],
            )
            new_move.put()

    @staticmethod
    def fake_fetch_movie_by_title(title):
        for f in fake:
            if title == f["Title"]:
                return f
        return None

    @staticmethod
    def real_fetch_movie_by_title(title):
        result = requests.get(URL, {"t": title, "apikey": API_KEY})
        if not "Error" in result.json():
            if not Movie.get_by_imdb_id(result.json()["imdbID"]):
                return result.json()
        return None

    @staticmethod
    def is_empty():
        return Movie.query().count() == 0

    @classmethod
    def get(cls, id):
        Movie.fetch_if_empty()
        entity = ndb.Key(urlsafe=id).get()

        if entity is None or not isinstance(entity, cls):
            raise NotFound("No user movie with id: %s" % id)
        return entity

    @classmethod
    def get_by_title(cls, title):
        Movie.fetch_if_empty()
        entities = cls.query(cls.title == title).fetch(1)
        return entities[0] if entities else None

    @classmethod
    def get_by_imdb_id(cls, imdb_id):
        Movie.fetch_if_empty()
        entities = cls.query(cls.imdb_id == imdb_id).fetch(1)
        return entities[0] if entities else None

    @classmethod
    def create(cls, title, director):
        Movie.fetch_if_empty()
        entity = cls(title=title, director=director)
        entity.put()
        return entity

    @property
    def id(self):
        return self.key.urlsafe().decode("utf-8")

    @staticmethod
    def list(per_page=10, page=1):
        Movie.fetch_if_empty()
        all = Movie.query()
        return all
