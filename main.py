from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = "test_key" # Change this to a secure key in production
    
    from routes import init_routes
    init_routes(app)
    
    return app 
    