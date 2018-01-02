import sys
sys.path.insert(0, '/home/grader/projects/restaurant-item-catalog')

import configuration
configuration.setup_lightsail()

from project import app as application
application.secret_key = configuration.secret_key
