import cgi
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant  # , MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


class webserverHandler(BaseHTTPRequestHandler):
    BACK_TO_LIST = "<p><a href='/restaurants'>Back to list</a></p>"

    FORM_METHOD = "<form method='POST' enctype='multipart/form-data' \
    action='/hello'>\
    <p>Enter greeting message</p>\
    <input name='message' type='text' />\
    <input type='submit' value='Submit' />\
    </form>"

    ADD_RESTAURANT_FORM = "<form method='POST' enctype='multipart/form-data' \
    action='/restaurants/add'>\
    <p>Enter restaurant details</p>\
    <p>Name: <input name='name' type='text' placeholder='Name' /></p>\
    <input type='submit' value='Create' />\
    </form>"

    def getRestaurantsList(self):
        """Query all of the restaurants and return the results in ascending alphabetical order"""
        output = ""
        restaurants = session.query(Restaurant).order_by(asc(Restaurant.name)).all()
        for restaurant in restaurants:
            output += "<p>%s</p>" % restaurant.name
            output += "<a href='/restaurants/%s/edit'>Edit</a><br/>" % restaurant.id
            output += "<a href='/restaurants/%s/delete'>Delete</a><br/><br/>" % restaurant.id

        return output

    def getRestaurantById(self, restId):
        """get instance of restaurant by given id."""
        return session.query(Restaurant).filter(id == restId).one()

    def deleteRestaurantById(self, restId):
        """Delete record with id given"""
        toDelete = self.getRestaurantById(restId)
        session.delete(toDelete)
        session.commit()
        return

    def setGetHeaders(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def setPostHeaders(self, redirectPath=None):
        self.send_response(301)
        if redirectPath:
            self.send_header('Location', redirectPath)
        self.end_headers()

    def do_GET(self):
        try:
            self.setGetHeaders()
            output = ""
            output += "<html><body>"

            route = self.path.split('?')[0]

            if route.endswith("/hello"):
                output += "Hello world!"
                output += self.FORM_METHOD

            elif route.endswith("/hola"):
                output += "<p>&#161Buenos Dias Mundo!</p><a href='/hello'>Back to hello</a>"
                output += self.FORM_METHOD

            elif route.endswith("/restaurants"):
                output += "<a href='/restaurants/add'>Add a new restaurant</a>"
                output += self.getRestaurantsList()

            elif route.endswith("/restaurants/add"):
                output += self.ADD_RESTAURANT_FORM
                output += self.BACK_TO_LIST

            elif route.endswith("/edit"):
                self.updateRestaurantName()

            elif route.endswith("/delete"):
                self.deleteRestaurant()

            output += "</body></html>"
            self.wfile.write(output)
            # print output
            return

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)

            output = ""
            output += "<html><body>"

            if self.path.endswith("/hello") or self.path.endswith("/hola"):
                self.setPostHeaders()
                messagecontent = [""]
                if fields != []:
                    messagecontent = fields.get('message')

                output += "<h2> %s </h2>" % messagecontent[0]
                output += self.FORM_METHOD
            elif self.path.endswith("/restaurants/add"):
                self.setPostHeaders("/restaurants")
                rest_name = [""]
                if fields != []:
                    rest_name = fields.get('name')[0]
                    item = Restaurant()
                    item.name = rest_name
                    session.add(item)
                    session.commit()
            elif self.path.endswith("/edit"):
                self.setPostHeaders("/restaurants")
                rest_name = [""]
                item = self.getRestaurantById(self.path.split('/')[2])
                if fields != [] and item != []:
                    newName = fields.get('newName')[0]
                    item.name = newName
                    session.add(item)
                    session.commit()
            elif self.path.endswith("/delete"):
                self.setPostHeaders("/restaurants")
                item = self.deleteRestaurantById(self.path.split('/')[2])

            output += "</body></html>"
            self.wfile.write(output)
            return

        except IOError:
            self.send_error(404, "nothing good here")

    def updateRestaurantName(self):
        """Assumes restaurant path only"""
        self.setGetHeaders()
        restId = self.path.split('/')[2]
        restaurant = self.getRestaurantById(restId)
        output = ""
        output += "<html><body>"
        output += "<h2>%s</h2><br/>" % restaurant.name
        output += "<form method='POST' enctype='multipart/form-data' \
        action='/restaurant/%s/edit' >" % restId
        output += "<input name='newName' type='text' \
        placeholder='%s' />" % restaurant.name
        output += "<input type='submit' value='Rename' />"
        output += "</form>"
        output += self.BACK_TO_LIST
        output += "</body></html>"
        self.wfile.write(output)
        # print output
        return

    def deleteRestaurant(self):
        """Assumes restaurant path only"""
        self.setGetHeaders()
        restId = self.path.split('/')[2]
        restaurant = self.getRestaurantById(restId)
        output = ""
        output += "<html><body>"
        output += "<h2>Delete %s?</h2>" % restaurant.name
        output += "<form method='POST' \
        action='/restaurant/%s/delete' >" % restId
        output += "<input type='submit' value='Delete' />"
        output += "</form>"
        output += self.BACK_TO_LIST
        output += "</body></html>"
        self.wfile.write(output)
        # print output
        return


def main():
    try:
        port = 8088
        server = HTTPServer(('', port), webserverHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping server"
        server.socket.close()


if __name__ == '__main__':
    main()
