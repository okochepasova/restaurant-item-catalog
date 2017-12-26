from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant


# Handler #Full Stack Web Developer Nanodegree - Udacity
class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Database Connection
            engine = create_engine('sqlite:///restaurantmenu.db')
            Base.metadata.bind = engine
            DBSession = sessionmaker(bind = engine)
            session = DBSession()

            # Variables
            output = []
            path = self.path

            # Body
            if path.endswith('/restaurants'):
                self.success()
                output += self.html_start()

                # List
                for r in session.query(Restaurant).all():
                    output += "<div class='restaurant --teal-item'>\n"
                    output += '<label>%s</label><br>\n'%r.name
                    output += '<a href="/restaurants/%d/edit">Edit</a><br>\n'%r.id
                    output += '<a href="/restaurants/%d/delete">Delete</a>\n'%r.id
                    output += '</div>\n\n'

                output += '<br>\n'
                output += "<a href='/restaurants/new'>Make a New Restaurant Here</a>\n"

                # Closing
                output = self.html_end(output)

            elif path.endswith('/restaurants/new'):
                # New Restaurant
                self.success()
                output += self.html_start()
                output += self.form('Make a New Restaurant', '/new', 'Create')
                output = self.html_end(output)

            elif path.startswith('/restaurants') and path.endswith('/edit'):
                r1 = None
                id = self.get_id('GET')

                if id.isdigit():
                    try: r1 = session.query(Restaurant).filter(Restaurant.id == int(id)).one()
                    except: self.home_redirect()

                # Edit
                if r1:
                    self.success()
                    output += self.html_start()
                    output += self.form(r1.name, '/%d/edit'%r1.id, 'Edit')
                    output = self.html_end(output)
                else:
                    self.home_redirect()

            elif path.startswith('/restaurants') and path.endswith('/delete'):
                r1 = None
                id = self.get_id('GET')

                if id.isdigit():
                    try: r1 = session.query(Restaurant).filter(Restaurant.id == int(id)).one()
                    except: self.home_redirect()

                # Delete
                if r1:
                    self.success()
                    output += self.html_start()
                    output += self.del_form(r1.name, r1.id)
                    output = self.html_end(output)
                #else:
                    #self.home_redirect()

            # Closing
            #print ''.join(output)
            return

        except:
            self.send_error(404, 'File Not Found %s'%self.path)


    def do_POST(self):
        try:
            # Database Connection
            engine = create_engine('sqlite:///restaurantmenu.db')
            Base.metadata.bind = engine
            DBSession = sessionmaker(bind = engine)
            session = DBSession()

            # Variables
            r_name = ''
            output = []
            path = self.path

            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                feilds = cgi.parse_multipart(self.rfile, pdict)
                r_name = feilds.get('name')[0]

            # Body
            if path.endswith('/restaurants/new'):
                if r_name:
                    session.add(Restaurant(name = r_name))
                    session.commit()
                    print 'POST: added %s'%r_name
                    self.home_redirect()
                else:
                    self.success()
                    output += self.html_start()
                    output += self.form('Make a New Restaurant', '/new', 'Create')
                    output = self.html_end(output)

            elif path.startswith('/restaurants') and path.endswith('/edit'):
                r1 = None
                id = self.get_id('POST')

                if id.isdigit():
                    try: r1 = session.query(Restaurant).filter(Restaurant.id == int(id)).one()
                    except: self.home_redirect()

                # Editing
                if r1 and r_name:
                    r1.name = self.safe(r_name)
                    session.commit()
                    self.home_redirect()

                elif r1:
                    self.success()
                    output += self.html_start()
                    output += self.form(r1.name, '/%s/edit'%id, 'Edit')
                    output = self.html_end(output)

                else:
                    self.home_redirect()

            elif path.startswith('/restaurants') and path.endswith('/delete'):
                r1 = None
                id = self.get_id('POST')

                if id.isdigit():
                    try: r1 = session.query(Restaurant).filter(Restaurant.id == int(id)).one()
                    except: self.home_redirect()

                # Deletion
                if r1:
                    print 'POST: deleted %s'%r1.name
                    session.delete(r1)
                    session.commit()
                    self.home_redirect()

            # Closing
            #print ''.join(output)
            return

        except: pass

    def success(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def home_redirect(self):
        # Redirect to Home Page
        print 'Redirecting to Home Page'
        self.send_response(301)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', '/restaurants')
        self.end_headers()

    def html_start(self):
        list = []
        list += '<html><head>\n'
        list += '<title>Restaurants</title>\n'

        with open('main.css', 'r') as style:
            list += '<style>\n%s</style>\n'%style.read()

        list += '</head>\n\n<body>\n'
        return list

    def html_end(self, list):
        list += '</body></html>\n'
        self.wfile.write(''.join(list))
        return list

    def form(self, name='', path='', does_what=''):
        return ("\n<form method='post' enctype='multipart/form-data' " +
                "action='/restaurants%s' class='--teal-item'>\n"%path +
                '  <h1>%s</h1>\n'%name +
                "  <input name='name' type='text' maxlength='80'>\n" +
                "  <input type='submit' value='%s'>\n</form>\n\n"%does_what +
                "<br>\n<a href='/restaurants'>Cancel</a>\n")

    def del_form(self, name, id):
        return ("\n<form method='post' enctype='multipart/form-data' " +
                "action='/restaurants/%d/delete' class='--teal-item'>\n"%id +
                '  <h1>Are you sure you want to delete %s?</h1>\n'%name +
                "  <input name='name' type='text' value='delete' hidden>\n" +
                "  <input type='submit' value='Delete'>\n</form>\n\n"+
                "<br>\n<a href='/restaurants'>Cancel</a>\n")

    def safe(self, name):
        word = []
        for c in name:
            if c == '"': word += '&#34;'
            elif c == "'": word += '&#39;'
            elif c == '(': word += '&#40;'
            elif c == ')': word += '&#41;'
            elif c == "/": word += '&#47;'
            elif c == '<': word += '&#60;'
            elif c == '>': word += '&#62;'
            else: word += c
        return ''.join(word)

    def get_id(self, type=''):
        id = self.path.split('/')[2]
        print '%s: path= %s, id= %s\n'%(type, self.path, id)
        return str(id)


# MAIN()
def main():
    try:
        # Web Server
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)

        # Test
        print "\n----------------------------------------"
        if 'a' > 'A': print "TEST: 'a' > 'A'"
        else: print "TEST: 'a' < 'A'"
        print "----------------------------------------"

        # Output
        print 'Web server running on port %d'%port
        server.serve_forever()

    except KeyboardInterrupt:
        print ' entered, stopping web server...'
        server.socket.close()


if __name__ == '__main__':
    main()
