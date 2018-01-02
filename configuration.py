secrets_path = 'client_secrets.json'
secret_key = 'super_secret_key'

engine_url = 'sqlite:///restaurantmenuwithusers.db'

def setup_lightsail():
    global secrets_path, engine_url
    secrets_path = '/home/grader/client_secrets.json'
    engine_url = 'postgresql://grader:udacity@localhost:5432/grader'
