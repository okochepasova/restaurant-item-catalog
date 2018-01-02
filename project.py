import configuration
from project_code import app

# MAIN
if __name__ == '__main__':
    app.secret_key = configuration.secret_key
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
