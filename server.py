
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
import datetime
from decimal import Decimal
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
DATABASEURI = "postgresql://tm3149:513888@34.73.36.248/project1" # Modify this with your own credentials you received from Joseph!


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#

#engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
#);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("select p.name, sum (score)as goals From matchstat m,player p where m.playerid=p.playerid Group by p.name order by goals desc;")
  names = []
  goals=[]
  for result in cursor:
      names.append(result['name'])
      goals.append(result['goals'])# can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names, data1=goals)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)


@app.route('/playerhome')
def playerhome():
  """
  """
  print(request.args)
  cursor = g.conn.execute("select p.name, sum (score)as goals From matchstat m,player p where m.playerid=p.playerid Group by p.name order by goals desc;")
  names = []
  goals =[]
  for result in cursor:
      names.append(result[0])
      goals.append(result[1])# can also be accessed using result[0]
  cursor.close()
  cursor = g.conn.execute(";select p.name,sum(m.assist) as total from matchstat m, player p where m.playerid=p.playerid group by p.name order by total desc;")
  names1 = []
  assists =[]
  for result in cursor:
      names1.append(result[0])
      assists.append(result[1])# can also be accessed using result[0]
  cursor.close()
  cursor = g.conn.execute(";select p.name,sum(m.save) as total from matchstat m, player p where m.playerid=p.playerid group by p.name order by total desc;")
  names2 = []
  saves =[]
  for result in cursor:
      names2.append(result[0])
      saves.append(result[1])# can also be accessed using result[0]
  cursor.close()



  context = dict(data = names,data1=goals,data2=names1,data3=assists,data4=names2,data5=saves)
  return render_template("playerhome.html", **context)

@app.route('/matchhome')
def matchhome():
  """
  """
  print(request.args)
  cursor=g.conn.execute("select t.homeground, t1.homeground,m1.playdate from (select p.teamid as c1, p1.teamid as c2, p.matchid as c3 from playbetween p, playbetween p1 where p.matchid=p1.matchid and p.teamid<p1.teamid) m, team t, team t1,match m1 where m.c1=t.teamid and m.c2=t1.teamid and m.c3=m1.matchid and m1.playdate> date(now())")
  team4 = []
  team5 =[]
  date1=[]
  for result in cursor:
      team4.append(result[0])
      team5.append(result[1])
      date1.append(result[2])# can also be accessed using result[0]
  cursor.close()

  #cursor = g.conn.execute("select t.homeground, t1.homeground,m1.playdate from (select p.teamid as c1, p1.teamid as c2, p.matchid as c3 from playbetween p, playbetween p1 where p.matchid=p1.matchid and p.teamid<p1.teamid) m, team t, team t1,match m1 where m.c1=t.teamid and m.c2=t1.teamid and m.c3=m1.matchid;")
  cursor=g.conn.execute("select t.homeground, t1.homeground,m1.playdate,m.c4,m.c5 from (select p.teamid as c1, p1.teamid as c2, p.matchid as c3, p.teamscore as c4, p1.teamscore as c5 from playbetween p, playbetween p1 where p.matchid=p1.matchid and p.teamid<p1.teamid) m, team t, team t1,match m1 where m.c1=t.teamid and m.c2=t1.teamid and m.c3=m1.matchid and m1.playdate<=date(now());")
  team1 = []
  team2 =[]
  date=[]
  score=[]
  for result in cursor:
      team1.append(result[0])
      team2.append(result[1])
      date.append(result[2])# can also be accessed using result[0]
      score.append(str(result[3])+" - "+str(result[4]))
  cursor.close()

  context = dict(data = team1,data1=team2,data2=date, data3=score, data4=team4, data5=team5, data6=date1)
  return render_template("matchhome.html", **context)


@app.route('/player')

def player():
  """
  """
  print(request.args)
  cursor = g.conn.execute("SELECT * FROM player;")
  player = []
  for result in cursor:
    player.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = player)
  return render_template("player.html", **context)

# Example of adding new data to the database
@app.route('/addplayer', methods=['POST'])
def addplayer():
  day=request.form['day']
  month=request.form['month']
  year=request.form['year']

  name = request.form['name']
  nationality = request.form['nationality']
  playerid=request.form['playerid']
  dob=datetime.date(int(year),int(month),int(day))
  position=request.form['position']
  salary=Decimal(request.form['salary'])

  g.conn.execute('INSERT INTO player(playerid,dob,name,position,salary,nationality) VALUES (%s,%s,%s,%s,%s,%s)',playerid,dob,name,position,salary,nationality)
  return redirect('/player')

@app.route('/team')
def team():
  """
  """
  print(request.args)
  cursor = g.conn.execute("SELECT * FROM team;")
  team = []
  for result in cursor:
    team.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = team)
  return render_template("team.html", **context)

# Example of adding new data to the database
@app.route('/addteam', methods=['POST'])
def addteam():
  homeground = request.form['homeground']
  nationality = request.form['nationality']
  teamid=request.form['teamid']
  budget=Decimal(request.form['budget'])
  manager=request.form['manager']
  g.conn.execute('INSERT INTO team(teamid,homeground,manager,budget,nationality) VALUES (%s,%s,%s,%s,%s)',teamid,homeground,manager,budget,nationality)
  return redirect('/team')

@app.route('/match')
def match():
  """
  """
  print(request.args)
  cursor = g.conn.execute("SELECT * FROM match;")
  match = []
  for result in cursor:
    match.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = match)
  return render_template("match.html", **context)

# Example of adding new data to the database
@app.route('/addmatch', methods=['POST'])
def addmatch():
  day=request.form['day']
  month=request.form['month']
  year=request.form['year']

  stadium = request.form['stadium']
  matchid=request.form['matchid']
  playdate=datetime.date(int(year),int(month),int(day))

  g.conn.execute('INSERT INTO match(matchid,stadium,playdate) VALUES (%s,%s,%s)',matchid,stadium,playdate)
  return redirect('/match')

@app.route('/tournament')
def tournament():
  """
  """
  print(request.args)
  cursor = g.conn.execute("SELECT * FROM tournament;")
  tournament = []
  for result in cursor:
    tournament.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = tournament)
  return render_template("tournament.html", **context)

# Example of adding new data to the database
@app.route('/addtournament', methods=['POST'])
def addtournament():
  sday=request.form['sday']
  smonth=request.form['smonth']
  syear=request.form['syear']
  eday=request.form['eday']
  emonth=request.form['emonth']
  eyear=request.form['eyear']

  nationality = request.form['nationality']
  tourid=request.form['tourid']
  startdate=datetime.date(int(syear),int(smonth),int(sday))
  enddate=datetime.date(int(eyear),int(emonth),int(eday))
  prize=Decimal(request.form['prize'])
  g.conn.execute('INSERT INTO tournament(tourid,startdate,enddate,prize,nationality) VALUES (%s,%s,%s,%s,%s)',tourid,startdate,enddate,prize,nationality)
  return redirect('/tournament')


@app.route('/sponsor')
def sponsor():
  """
  """
  print(request.args)
  cursor = g.conn.execute("SELECT * FROM sponsor;")
  sponsor = []
  for result in cursor:
    sponsor.append(result)  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = sponsor)
  return render_template("sponsor.html", **context)

# Example of adding new data to the database
@app.route('/addsponsor', methods=['POST'])
def addsponsor():
  budget = Decimal(request.form['budget'])
  sponsorid=request.form['sponsorid']

  g.conn.execute('INSERT INTO sponsor(sponsorid,budget) VALUES (%s,%s)',sponsorid,budget)
  return redirect('/sponsor')





@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
