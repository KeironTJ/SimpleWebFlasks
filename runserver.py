import sqlalchemy as sa
import sqlalchemy.orm as so
from app.models import User
from app import create_app, db, socketio


app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)

@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User}



# Custom filter for date formatting
def format_datetime(value, format='%d-%m-%Y @ %H:%M'):
    if value is None:
        return "None"
    return value.strftime(format)

# Register the filter with the app
app.jinja_env.filters['datetime'] = format_datetime