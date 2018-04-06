"""Handle online APIs for relates ISBN and book info."""

import re
import time
import urllib.parse
import xml.etree.ElementTree as ET
import requests
import pyisbn
from bottlenose import Amazon
from bs4 import BeautifulSoup
from flask import flash
from bpslibrary import app
from bpslibrary.models import Author, Book, Category


def build_book(vol_info):
    """Build a book object from google volume info."""
    book = Book()
    # book title
    book.title = vol_info.get('title')
    # description
    book.description = vol_info.get('description')
    # isbn(s)
    if 'industryIdentifiers' in vol_info.keys():
        for ident in vol_info.get('industryIdentifiers'):
            if ident.get('type').upper() == 'ISBN_13':
                book.isbn13 = ident.get('identifier')
            elif ident.get('type').upper() == 'ISBN_10':
                book.isbn10 = ident.get('identifier')
    # author(s)
    if 'authors' in vol_info.keys():
        for author_name in vol_info.get('authors'):
            book.authors.append(Author(author_name))
    # categories
    if 'categories' in vol_info.keys():
        for category_name in vol_info.get('categories'):
            book.categories.append(Category(category_name))
    # thumbnail
    if 'imageLinks' in vol_info.keys():
        book.thumbnail_url = \
            vol_info.get('imageLinks').get('smallthumbnail') \
            or vol_info.get('imageLinks').get('thumbnail')
    # preview link
    book.preview_url = vol_info.get('previewLink')
    return book


class APIClient():
    """
    Online book information APIs handler.

    The primary function is to lookup book details on
    google books and it utilises other book info webservices
    to support that function.

    Parameters
    :param1 isbn_list (list):
    A list ISBNs to lookup.

    :param2 book_title (str):
    A title of a book to lookup.

    """

    def __init__(self, isbn_list, book_title):
        """Initialise an APIClient.

        :param1 isbn_list:
        A list ISBNs to lookup.

        :param2 book_title:
        A title of a book to lookup.
        """
        self.isbns = isbn_list if isbn_list else []
        self.book_title = book_title.strip() if book_title else ''
        self.google_key = app.config['GOOGLE_API_KEY']
        self.aws_access_key = app.config['AWS_ACCESS_KEY']
        self.aws_secret_key = app.config['AWS_SECRET_KEY']
        self.aws_associate_tag = app.config['AWS_ASSOCIATE_TAG']
        self.ebay_appname = app.config['EBAY_APPNAME']

    def find_books(self, direct_search_only=False):
        """
        Lookup book details on google books.

        Utilising book info web services to look up related isbn or title.

        :ISBN lookup:
        First lookup the ISBN on google books, if that yielded no
        results, the related ISBN are looked up on xISBN and librarything
        and the result is looked up on google books. If no related
        ISBNs found on xISBN or LibraryThing, the title is looked up
        on isbndb and isbnplus, and lookup the book on google books using
        the yielded title. If none of these steps.

        :Title lookup:
        If provided, books will be also looked up on google books by title.

        """
        found_books = []
        lookup_results = []
        errors = []

        found_books += self.lookup_by_title()

        if bool(self.isbns):
            for isbn in self.isbns:
                try:
                    isbn = isbn.strip()

                    # first search on google books
                    lookup_results += self.search_google_books(isbn, None)

                    # if not on google, search amazon
                    if not lookup_results:
                        lookup_results += self.search_amazon(isbn)

                    # if dirct_search_only is not set, then try related
                    # and title search
                    if not direct_search_only and not lookup_results:
                        lookup_results += self.lookup_by_related_isbn(isbn)

                        if not lookup_results:
                            lookup_results = self.lookup_by_title(
                                self.lookup_title(isbn)
                            )

                    # ensure that all results have the targeted isbn
                    # pylint: disable=C0200
                    for i in range(len(lookup_results)):
                        if len(isbn) == 13:
                            lookup_results[i].isbn13 = isbn
                            lookup_results[i].isbn10 = pyisbn.convert(isbn)
                        else:
                            lookup_results[i].isbn10 = isbn
                            lookup_results[i].isbn13 = pyisbn.convert(isbn)

                    found_books += lookup_results
                except Exception as err:
                    errors.append(
                        time.strftime('%Y-%m-%d_%H:%M:%S - ') + str(err)
                        )
                    continue

        found_books = sorted(set(found_books), key=lambda b: b.title)
        if errors:
            flash(errors)
        return found_books

    def search_google_books(self, isbn, title):
        """Look up a book on google books api.

        This method uses the `Volumes: list` method. It is designed for v1
        of the API.
        (https://developers.google.com/books/docs/v1/reference/volumes/list)
        """
        api_url = 'https://www.googleapis.com/books/v1/volumes?q={}' + \
            '&printType=books&key=' + self.google_key
        search_query = ''

        if title and title.strip():
            search_query = '+intitle:' + urllib.parse.quote_plus(title)

        if isbn and isbn.strip():
            search_query = search_query + '+isbn:' + isbn

        if not search_query:
            return []

        search_result = requests.get(api_url.format(search_query))

        # pylint: disable=E1101
        if search_result.status_code != requests.codes.ok:
            return []

        if int(search_result.json().get('totalItems')) <= 0 or \
           'items' not in search_result.json().keys():
            return []

        found_books = []
        for item in search_result.json().get('items'):

            if 'volumeInfo' not in item.keys():
                continue

            book = build_book(item.get('volumeInfo'))

            if book and book.title:
                found_books.append(book)
        return found_books

    def lookup_by_related_isbn(self, isbn):
        """
        Lookup related ISBN for the same work.

        :param1 isbn: (str)
        The isbn to lookup.
        """
        found_on_google = []

        # xisbn web service
        xisbn_url = 'http://xisbn.worldcat.org/webservices/xid/isbn/{}' + \
            '?method=getEditions&format=json'

        xisbn_result = requests.get(xisbn_url.format(isbn)).json()

        if xisbn_result and xisbn_result.get('stat').lower() == 'ok':
            for risbn in xisbn_result.get('list'):
                found_on_google += \
                    self.search_google_books(risbn.get('isbn')[0], None)
                if found_on_google:
                    return found_on_google

        # libraryThing web service
        lib_thing_url = 'http://www.librarything.com/api/thingISBN/{}'
        lt_result = ET.fromstring(
            requests.get(lib_thing_url.format(isbn)).text)

        for data in lt_result.iter('isbn'):
            found_on_google += self.search_google_books(data.text, None)
            if found_on_google:
                return found_on_google
        return found_on_google

    def lookup_title(self, isbn):
        """
        Lookup book title by ISBN.

        :param1 isbn: (str)
        The isbn to lookup.
        """
        # ebay
        ebay_url = 'http://svcs.ebay.com/services/search/FindingService/v1' + \
            '?OPERATION-NAME=findItemsAdvanced&RESPONSE-DATA-FORMAT=JSON' + \
            '&SECURITY-APPNAME=' + self.ebay_appname + \
            '&GLOBAL-ID=EBAY-GB&categoryId=267&keywords={}'
        ebay_result = requests.get(ebay_url.format(isbn)).json()

        if ebay_result:
            response = ebay_result.get('findItemsAdvancedResponse')[0]
            if response.get('ack')[0].lower() == 'success' and \
               int(response.get('searchResult')[0].get('@count')) > 0:
                return response.get('searchResult')[0].get('item')[0] \
                    .get('title')[0].replace(isbn, '')

    def lookup_by_title(self, title=None):
        """Look up a book by its title."""
        if not title:
            title = self.book_title

        results = []
        results += self.search_google_books(None, title)

        # remove books with mismatching titles
        for i, book in enumerate(results):
            gb_title = re.sub(r'[^\w\s]', '', book.title.lower())
            s_title = re.sub(r'[^\w\s]', '', title.lower())
            if gb_title not in s_title and s_title not in gb_title:
                del results[i]

        return results

    def search_amazon(self, isbn):
        """Look up book info on amazon."""
        amazon = Amazon(self.aws_access_key,
                        self.aws_secret_key,
                        self.aws_associate_tag,
                        Region='UK',
                        Parser=lambda text: BeautifulSoup(text))
        result = amazon.ItemLookup(
            ItemId=isbn,
            ResponseGroup='EditorialReview,Images,ItemAttributes',
            SearchIndex='Books',
            IdType='EAN'
        )

        found_books = []
        if result and not result.find('errors'):
            book = Book()

            # title
            title_tag = result.find('title')
            book.title = title_tag.text if title_tag else ''

            # preview url
            detail_url_tag = result.find('detailpageurl')
            book.preview_url = detail_url_tag.text if detail_url_tag else ''

            # description
            description_tag = result.find('editorialreview')
            if description_tag:
                if description_tag.find('content'):
                    book.description = description_tag.find('content').text
                else:
                    book.description = description_tag.text
            else:
                if book.preview_url:
                    desc_html = requests.get(book.preview_url)
                    if desc_html and desc_html.text:
                        desc_div = BeautifulSoup(desc_html.text).find(
                            id="bookDescription_feature_div")
                        if desc_div and desc_div.find('noscript'):
                            desc_text = desc_div.find('noscript').text
                            bool.description = re.sub(
                                re.compile(r'<.*?>|\n|\t|\r|\s{2,10}'),
                                '', desc_text)

            # thumbnail
            image_tag = result.find('largeimage')
            image_url_tag = image_tag.find('url') if image_tag else None
            book.thumbnail_url = image_url_tag.text if image_url_tag else None

            # authors
            for author_name in result.find_all('author'):
                book.authors.append(Author(author_name.text))

            # categories
            book.categories.append(Category("Children's Books"))

            found_books.append(book)
        return found_books
