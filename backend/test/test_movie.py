from re import A
from backend import test, movie


def print_movie(m):
    print()
    print("movie.title    =", m.title)
    print("movie.year     =", m.year)
    print("movie.director =", m.director)
    print("movie.poster   =", m.poster)
    print("movie.imdb_id  =", m.imdb_id)
    print("movie.id       =", m.id)
    print()


class TestMovie(test.TestCase):
    def test_fake_fetch(self):
        movie.Movie.fetch_movies(real=False)
        assert movie.Movie.query().count() == 100

    def test_real_fetch(self):
        movie.Movie.fetch_movies(real=True)
        assert movie.Movie.query().count() == 100

    def test_create(self):
        obj = movie.Movie.create(title="Terminator", director="James Cameron")
        self.assertEqual(obj, movie.Movie.get(obj.id))
        self.assertTrue(obj.title == "Terminator")
        self.assertTrue(obj.director == "James Cameron")

        by_title = movie.Movie.get_by_title(title="Terminator")
        assert by_title.title == "Terminator"

    def test_fake_fetch_by_title(self):
        title = "The Terminator"
        movie.Movie.fetch_movie_by_title(title, real=False)
        assert movie.Movie.get_by_title(title)
        title = "The Terminator The Terminator The Terminator"
        movie.Movie.fetch_movie_by_title(title, real=False)
        assert movie.Movie.get_by_title(title) == None

    def test_real_fetch_by_title(self):
        title = "The Terminator"
        movie.Movie.fetch_movie_by_title(title, real=True)
        m = movie.Movie.get_by_title(title)
        assert m
        title = "The Terminator The Terminator The Terminator"
        movie.Movie.fetch_movie_by_title(title, real=True)
        assert movie.Movie.get_by_title(title) == None

    def test_is_empty(self):
        assert movie.Movie.is_empty()
        movie.Movie.fetch_movies(real=False)
        assert not movie.Movie.is_empty()

    def test_fetch_if_empty(self):
        assert movie.Movie.query().count() == 0
        movie.Movie.fetch_if_empty(real=False)
        assert movie.Movie.query().count() == 100
        movie.Movie.fetch_if_empty(real=False)
        assert movie.Movie.query().count() == 100
        title = "The Terminator"
        m = movie.Movie.get_by_title(title)
        m.key.delete()
        movie.Movie.fetch_if_empty(real=False)
        assert movie.Movie.query().count() == 99
        title = "Akira"
        m = movie.Movie.get_by_title(title)
        m.key.delete()
        movie.Movie.fetch_if_empty(real=False)
        assert movie.Movie.query().count() == 98

    def test_list(self):
        movies = list(movie.Movie.list())
        assert len(movies) == 100


class TestMovieApi(test.TestCase):
    def test_get(self):
        title = "The Terminator"
        result = self.api_client.post("movie.bytitle", dict(title=title))
        assert result["title"] == title
        title = "Akira"
        result = self.api_client.post("movie.bytitle", dict(title=title))
        assert result["title"] == title

    def test_add(self):
        title = "The Fly"
        result = self.api_client.post("movie.add", dict(title=title))
        assert result["title"] == title
        m = movie.Movie.get_by_title(title)
        assert m.title == title
        result = self.api_client.post("movie.list", dict(page=1, per_page=200))
        success = False
        for r in result["movies"]:
            if r["title"] == title:
                success = True
        assert success
        result = self.api_client.post("movie.bytitle", dict(title=title))
        assert result["title"] == title

    def test_list(self):
        result = self.api_client.post("movie.list", dict(page=1, per_page=1))
        assert result["movies"][0]["title"] == "10 Cloverfield Lane"
        result = self.api_client.post("movie.list", dict(page=100, per_page=1))
        assert result["movies"][0]["title"] == "Æon Flux"
        result = self.api_client.post("movie.list", dict(page=1, per_page=100))
        assert result["movies"][99]["title"] == "Æon Flux"

    def test_delete(self):
        resp = self.api_client.post(
            "user.create", dict(email="test@gmail.com", password="test")
        )
        access_token = resp.get("access_token")
        movie.Movie.fetch_if_empty()
        result = self.api_client.post("movie.list", dict(page=1, per_page=1))
        first_title = result["movies"][0]["title"]
        first_id = result["movies"][0]["id"]
        resp = self.api_client.post(
            "movie.delete",
            dict(id=first_id),
            headers=dict(authorization=access_token),
        )

        result = self.api_client.post("movie.list", dict(page=1, per_page=1))
        second_title = result["movies"][0]["title"]
        second_id = result["movies"][0]["id"]
        assert first_id != second_id
        assert first_title != second_title
