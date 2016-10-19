import cherrypy
import os
import os.path
from pprint import pprint
from nearestNeighborClassifier import Classifier
from database import database
from mako.lookup import TemplateLookup

lookup = TemplateLookup(directories=['html'])


class Index:
    def __init__(self):
        # initialize the database
        self.db = database()

    # the first page to be displayed is the login page
    @cherrypy.expose
    def index(self):
        if 'username' in cherrypy.session:
            raise cherrypy.HTTPRedirect("/main")
        log_template = lookup.get_template("login.html")
        return log_template.render(error=0)

    # when a user attempts to register
    @cherrypy.expose
    def register(self, username, password):
        query = 'select * from users where username = "' + username + '"'
        users = self.db.read_from_db(query)

        # if there is no such record
        if len(users) == 0:
            query = 'insert into users(`username`, `password`) values ("' + username + ' ", "' + self.db.encrypt_pw(
                password) + '")'
            # registration successful, return to login page
            self.db.write_to_db(query)
            raise cherrypy.HTTPRedirect("/login")
        # if such a record exists display error message
        else:
            log_template = lookup.get_template("login.html")
            return log_template.render(err=1, msg="User already exists. Please try another username.")

    # when a user attempts to log in
    @cherrypy.expose
    def login(self, username=None, password=None):
        if 'username' in cherrypy.session:
            raise cherrypy.HTTPRedirect("/main")

        if username is None or password is None:
            raise cherrypy.HTTPRedirect("/")

        query = 'select * from users where username = "' + username + '" and password ="' + self.db.encrypt_pw(
            password) + '"'
        users = self.db.read_from_db(query)
        # print users

        # if successful login redirect to the main page - with given user
        if len(users) == 1:
            cherrypy.session['username'] = users[0]['username']
            cherrypy.session['user_id'] = users[0]['id']
            raise cherrypy.HTTPRedirect("/main")
        # else redirect to login page again with error message
        else:
            log_template = lookup.get_template("login.html")
            return log_template.render(err=1, msg="This account does not exist!")

    # when a user is logged in, display the main page
    @cherrypy.expose
    def eatit(self, itemid):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        query = "insert into itemlikes(`userid`, `itemid`) values({}, {})".format(cherrypy.session['user_id'], itemid)
        self.db.write_to_db(query)

    @cherrypy.expose
    def dislike(self, itemid):
        cherrypy.response.headers['Content-Type'] = 'application/json'
        query = "delete from itemlikes where userid={} and itemid={}".format(cherrypy.session['user_id'], itemid)
        self.db.write_to_db(query)

    def getKey(self, items):
        return items[1]

    @cherrypy.expose
    def main(self):
        if 'username' not in cherrypy.session:
            raise cherrypy.HTTPRedirect("/login")

        # get the list of items and send it to main.html
        query = 'select * from items'
        items = self.db.read_from_db(query)

        query = 'select `itemId`, \*...*\ `class` from items'
        items_f = self.db.read_from_db(query)

        query = 'select * from itemlikes'
        item_likes_db = self.db.read_from_db(query)

        format = ("name", "num", "num", "num", "num", "num", "num", "num",
                  "num", "num", "num", "num", "num", "num", "class")

        items_formated = list()
        for i in items_f:
            l = list()
            l.append(str(i['itemId']))
            """
            l.append(str(i[...]))
            ...
            """
            l.append(str(i['class']))
            items_formated.append(l)

        classifier = Classifier(format, items_formated)

        item_neighbors = []
        item_id_count = 0
        for elements in items_formated:

            element_vector = []
            column_count = 0
            for columns in elements:
                if format[column_count] == "num":
                    element_vector.append(float(columns))
                column_count += 1
            item_neighbors.append((item_id_count, classifier.nearestNeighbor(classifier.normalizeVector(element_vector)
                                  , 3, item_id_count)[0][0]
                                  , classifier.nearestNeighbor(classifier.normalizeVector(element_vector)
                                  , 3, item_id_count)[1][0]
                                  , classifier.nearestNeighbor(classifier.normalizeVector(element_vector)
                                  , 3, item_id_count)[2][0]))
            item_id_count += 1

        pprint(item_neighbors)

        upvotes = list()
        for i in range(len(items)):
            upvotes.append(0)

        user_likes = list()

        liked_classes = list()

        for i in item_likes_db:
            if i['userid'] == cherrypy.session['user_id']:
                user_likes.append(i['itemid'])
                liked_classes.append(items[i['itemid']]['class'])

            upvotes[int(i['itemid'])] += 1

        liked_classes_count = []

        count = 0
        tup = ['', 0]

        for classes in liked_classes:
            entered = False
            liked_id = 0
            liked_perm = 0
            for lcc in liked_classes_count:
                if lcc[0] == classes:
                    entered = True
                    liked_perm = liked_id
                liked_id += 1
            if entered:
                liked_classes_count[liked_perm][1] += 1
            else:
                tup = [classes, 1]
                liked_classes_count.append(tup)
            count += 1

        sorted_liked_classes = sorted(liked_classes_count, key=self.getKey, reverse=True)
        sorted_liked_classes2 = []

        if len(sorted_liked_classes) < 3:
            for item in items:
                app = True
                for slc2 in sorted_liked_classes:
                    if item['class'] == slc2[0]:
                        app = False
                if app:
                    sorted_liked_classes2.append([item['class'], 0])
                    print(sorted_liked_classes2)
        else:
            for i2 in range(3):
                sorted_liked_classes2.append(sorted_liked_classes[i2])


        main_template = lookup.get_template("main.html")
        return main_template.render(username=cherrypy.session['username'], itemlist=items, size=len(items),
                                    userlikes=user_likes, itemlikes=upvotes, itemneighbors=item_neighbors,
                                    likedclasses=liked_classes, slc=sorted_liked_classes2)

    # when an item is clicked its specific page is opened
    @cherrypy.expose
    def item(self, item_title):
        log_template = lookup.get_template("item.html")
        return log_template.render(username=cherrypy.session['username'], itemName=item_title)

    @cherrypy.expose
    def logout(self):
        del cherrypy.session['username']
        raise cherrypy.HTTPRedirect("/login")


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }

    root = Index()
    cherrypy.quickstart(root, '/', conf)
