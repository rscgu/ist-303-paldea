
from my_paldea import create_app
app = create_app()
#app.env="development" to run the application in the developement environ
# the reloader indicates the application is being run in debug mode
# and that the application will reload whenever a change is made in the code
if __name__=='__main__':
   app.run(debug=True,ssl_context='adhoc')