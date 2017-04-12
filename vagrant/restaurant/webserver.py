from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from sqlalchemy import create_engine, asc
# , desc, func
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant
# , MenuItem
import cgi

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
    <p>Name: <input name='name' type='text' /></p>\
    <input type='submit' value='Submit' />\
    </form>"

    def getRestaurantsList(self):
        """Query all of the restaurants and return the results in ascending alphabetical order"""
        output = ""
        restaurants = session.query(Restaurant).order_by(asc(Restaurant.name)).all()
        for restaurant in restaurants:
            output += "<p>%s</p>" % restaurant.name
            output += "<a href='/restaurants/edit?restaurantid=%s'>Edit</a><br/>" % restaurant.id
            output += "<a href='/restaurants/delete?restaurantid=%s'>Delete</a><br/><br/>" % restaurant.id

        return output

    def deleteRestaurant(self, rest_id):
        """Delete record with id given, return name of restaurant deleted"""
        to_delete = session.query(Restaurant).filter(Restaurant.id == rest_id).one()
        name = to_delete.name
        session.delete(to_delete)
        session.commit()
        return name

    def setGetHeaders(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def setPostHeaders(self):
        self.send_response(301)
        self.end_headers()

    def setPutHeaders(self):
        self.send_response(204)  # good but no content
        self.end_headers()

    def setDelHeaders(self):
        self.send_response(200)
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

            elif route.endswith("/restaurants/delete"):
                self.do_DELETE()

            output += "</body></html>"
            self.wfile.write(output)
            # print output
            return

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            self.setPostHeaders()
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

            output = ""
            output += "<html><body>"

            if self.path.endswith("/hello") or self.path.endswith("/hola"):
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')

                output += "<h2> %s </h2>" % messagecontent[0]
                output += self.FORM_METHOD
            elif self.path.endswith("/restaurants/add"):
                print "adding restaurant"
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    rest_name = fields.get('name')[0]

                if rest_name:
                    print "adding %s" % rest_name
                    item = Restaurant()
                    item.name = rest_name
                    session.add(item)
                    print item.name
                    session.commit()

                output += self.ADD_RESTAURANT_FORM
                output += self.BACK_TO_LIST

            output += "</body></html>"
            self.wfile.write(output)
            return

        except IOError:
            self.send_error(404, "nothing good here")

    def do_DELETE(self):
        try:
            self.setDelHeaders()
            output = ""
            output += "<html><body>"
            path_ = self.path.split('?')
            if len(path_) > 1:
                route = path_[0]
                rest_id = cgi.parse_qs(path_[1]).get('restaurantid')[0]  # why is everything a list?

                if route.endswith("/restaurants/delete"):
                    rest_name = self.deleteRestaurant(rest_id)
                    output += "<p>%s Deleted</p>" % rest_name
            else:
                output += "No ID supplied"

            output += self.BACK_TO_LIST
            output += "</body></html>"
            self.wfile.write(output)
            # print output
            return

        except IOError:
            pass


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
