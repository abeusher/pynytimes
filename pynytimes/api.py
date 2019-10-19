import datetime
import math

import requests

base_top_stories = "https://api.nytimes.com/svc/topstories/v2/"
base_most_popular = "https://api.nytimes.com/svc/mostpopular/v2/"
base_books = "https://api.nytimes.com/svc/books/v3/"
base_movie_reviews = "https://api.nytimes.com/svc/movies/v2/reviews/search.json"
base_book_reviews = base_books + "reviews.json"
base_best_sellers_lists = base_books + "lists/names.json"
base_best_sellers_list = base_books + "lists/"



class _get_results:
    def top_stories(key, section):
        api_key = { "api-key": key }
        url = base_top_stories + section + ".json"
        res = requests.get(url, params=api_key)
        res.raise_for_status()
        results =  res.json().get("results")
        return results

    def most_viewed(key, days):
        api_key = { "api-key": key }
        url = base_most_popular + "viewed/" + str(days) + ".json"
        res = requests.get(url, params=api_key)
        res.raise_for_status()
        results = res.json().get("results")
        return results

    def most_shared(key, days, method):
        api_key = { "api-key": key }
        if method is None:
            url = base_most_popular + "shared/" + str(days) + ".json"
        else:
            url = base_most_popular + "shared/" + str(days) + "/" + method + ".json"
        res = requests.get(url, params=api_key)
        res.raise_for_status()
        results = res.json().get("results")
        return results

    def book_reviews(key, author, isbn, title):
        params = {
            "api-key": key
        }
        if author is not None:
            params["author"] = author

        elif isbn is not None:
            params["isbn"] = str(isbn)

        elif title is not None:
            params["title"] = title

        url = base_book_reviews 
        res = requests.get(url, params=params)
        results = res.json().get("results")
        return results

    def best_sellers_lists(key):
        api_key = { "api-key": key }
        url = base_best_sellers_lists
        res = requests.get(url, params=api_key)
        res.raise_for_status()
        results = res.json().get("results")
        return results

    def best_sellers_list(key, date, name):
        api_key = { "api-key": key }
        url = base_best_sellers_list + date + "/" + name + ".json"
        res = requests.get(url, params=api_key)
        res.raise_for_status()
        results = res.json().get("results").get("books")
        return results

    def movie_reviews(key, keyword, critics, reviewer, order, opening, publication, max_results):
        params = { "api-key": key }
        
        if keyword is not None:
            params["query"] = keyword

        if critics is not None:
            params["critics-pick"] = critics

        if reviewer is not None:
            params["reviewer"] = reviewer
        
        if order is not None:
            params["order"] = order

        if opening is not None:
            params["opening-date"] = opening

        if publication is not None:
            params["publication-date"] = publication

        url = base_movie_reviews

        results = []

        for i in range(math.ceil(max_results/20)):
            offset = i*20
            params["offset"] = str(offset)
            res =  requests.get(url, params=params)
            res.raise_for_status()
            res_parsed = res.json()
            results += res_parsed.get("results")
            
            if res_parsed.get("has_more") is False:
                break
        
        return results

class nytAPI(object):
    def __init__(self, key=None):
        self.key = key
        if self.key is None:
            raise Exception("No API key")

    def top_stories(self, section=None):
        if section is None:
            section = "home"

        return _get_results.top_stories(self.key, section)

    def most_viewed(self, days=None):
        days_options = [1, 7, 30]
        if days is None:
            days = 1

        if days not in days_options:
            raise Exception("You can only select 1, 7 or 30 days")

        return _get_results.most_viewed(self.key, days)
        
    def most_shared(self, days=None, method=None):
        method_options = ["email", "facebook", "twitter"]
        days_options = [1, 7, 30]

        if days is None:
            days = 1

        if method not in method_options:
            raise Exception("Shared option does not exist")

        if days not in days_options:
            raise Exception("You can only select 1, 7 or 30 days")

        return _get_results.most_shared(self.key, days, method)

    def book_reviews(self, author=None, isbn=None, title=None):
        if author and isbn and title is None:
            raise Exception("Not all fields in reviews can be empty")

        if int(isbn is not None) + int(title is not None) + int(author is not None) is not 1:
            raise Exception("You can only define one of the following: ISBN, author or title.")

        return _get_results.book_reviews(self.key, author, isbn, title)

    def best_sellers_lists(self):
        return _get_results.best_sellers_lists(self.key)

    def best_sellers_list(self, date=None, name=None):
        if date is None:
            _date = "current"
        
        elif not isinstance(date, datetime.datetime):
            raise Exception("Date has to be a datetime object")

        else:
            _date = date.strftime("%Y-%m-%d")

        if name is None:
            name = "combined-print-and-e-book-fiction"
        
        return _get_results.best_sellers_list(self.key, _date, name)

    def movie_reviews(self, keyword=None, critics=None, opening_date_start=None, opening_date_end=None, order=None, publication_date_start=None, publication_date_end=None, reviewer=None, max_results=None):
        if order not in [None, "by-opening-date", "by-publication-date", "by-title"]:
            raise Exception("Order is not a valid option")
        
        if max_results is None:
            max_results = 20

        if opening_date_end is not None and opening_date_start is None:
            opening_date_start = datetime.datetime(1900, 1, 1)

        if publication_date_end is not None and opening_date_start is None:
            opening_date_start = datetime.datetime(1900, 1, 1)

        _opening_dates = None
        _publication_dates = None
        _critics_pick = None

        if opening_date_start is not None:
            _opening_dates = opening_date_start.strftime("%Y-%m-%d") + ";"

        if opening_date_end is not None:
            _opening_dates += opening_date_end.strftime("%Y-%m-%d")

        if publication_date_start is not None:
            _publication_dates = opening_date_start.strftime("%Y-%m-%d") + ";"

        if publication_date_end is not None:
            _publication_dates += opening_date_end.strftime("%Y-%m-%d")

        if critics is True:
            _critics_pick = "Y"
        
        return _get_results.movie_reviews(self.key, keyword, _critics_pick, reviewer, order, _opening_dates, _publication_dates, max_results)