from extensions import *

load_dotenv('.venv')
app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=30)
csrf = CSRFProtect(app)
conn = psycopg2.connect(database="flask_db", 
                        user="postgres",
                        password="root", 
                        host="localhost", port="5432")

db = SQLAlchemy(app)



@app.route('/')
def hello_world():
    return 'Hello World'

if __name__ == '__main__':
    app.run()
    
    