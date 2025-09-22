from flask import Flask, render_template
from source.config import Config
from source.models import db
from source.auth import auth_bp
from source.appointments import appointments_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)


    app.register_blueprint(auth_bp)
    app.register_blueprint(appointments_bp)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        return render_template('index.html')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=3001, debug=True)