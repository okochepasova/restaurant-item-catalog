from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi


# Handler
class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Variables
            output = ''

            # Body
            if self.path.endswith('/hello'):
                # English
                self.success()
                output += '<html><body>\n'
                output += '<h1>Hello!</h1>\n'
                output += self.form()
                output += '</body></htm>'

                # Closing
                self.wfile.write(output)

            elif self.path.endswith('/hola'):
                # Espanol
                self.success()
                output += '<html><body>\n'
                output += '<h1>&#161Hola!</h1>\n'
                output += '<a href="/hello">Volver a "Hello"</a>\n'
                output += self.form()
                output += '</body></htm>'

                # Closing
                self.wfile.write(output)

            # Closing
            print output
            return

        except:
            self.send_error(404, 'File Not Found %s'%self.path)

    def do_POST(self):
        try:
            self.send_response(301)
            self.end_headers()

            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

            if ctype == 'multipart/form-data':
                # Variables
                feilds = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = feilds.get('message')
                output = ''

                output += '<html><body>\n'
                output += '<h2 style="font-weight: 300;">Okay, how about this:'
                output += ' </h2>\n<h1>%s</h1><br>\n'% messagecontent[0]
                output += self.form()

                # Closing
                output += '</body></htm>\n'
                self.wfile.write(output)
                print output

        except: pass

    def success(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def form(self):
        return ("\n<form method='post' enctype='multipart/form-data' "+
                "action='/hello'>\n<h2>What would you like me to say?</h2>\n"+
                "<input name='message' type='text'>\n"+
                "<input type='submit' value='Submit'></form>\n\n")


# MAIN()
def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)

        # Output
        print 'Web server running on port %d'%port
        server.serve_forever()

    except KeyboardInterrupt:
        print ' entered, stopping web server...'
        server.socket.close()


if __name__ == '__main__':
    main()