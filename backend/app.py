from flask import Flask
from routes.cleaner_routes import cleaner_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(cleaner_bp)

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)
