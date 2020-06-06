class Book:
    counter = 1
    def __init__(self,isbn,title,author,year):
        self.id = Book.counter
        Book.counter +=1
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year

class User:
    def __init__(self, name, password):
        self.name = name
        self.password = password

    def adduser(self,u):
        u.name = self.name
        u.password = self.password

    def login(self,u):
        return


class Review:
    def __init__(self, rating, review):
        self.rating = rating
        self.review = review
