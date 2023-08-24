import sqlite3
from datetime import datetime
from flask import Flask,redirect,url_for,render_template,request,flash,session,abort


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key="c31e3ca09abe7e653734d9430fd03cbcb2be620b693b01bf5e1d404bafb6f8e2"


# ------------------- Create table carnet and users ------------------------

con = sqlite3.connect("database.db")
con.execute(
  """
    CREATE TABLE IF NOT EXISTS carnet(
      id INTEGER PRIMARY KEY, 
      titre TEXT NOT NULL, 
      contenu TEXT NOT NULL, 
      marquage TEXT, 
      username TEXT NOT NULL,
      Date DATETIME DEFAULT (date('now'))) 
  """)
con.execute(
  """
    CREATE TABLE IF NOT EXISTS users(
      user_id INTEGER PRIMARY KEY, 
      username TEXT NOT NULL UNIQUE, 
      password TEXT NOT NULL UNIQUE,
      confirm TEXT NOT NULL UNIQUE)
  """)
con.close()


def get_db_connection():
  connexion = sqlite3.connect("database.db")
  connexion.row_factory = sqlite3.Row
  return connexion


# ------------------- Page open first ------------------------
  
@app.route("/")
def index():
    return render_template('login.html')
  

# ------------------- Dashboard ------------------------

@app.route("/dashboard")
def dashboard():
  # Check if user is logged_in
  if 'logged_in' in session:
      con = get_db_connection()
      cursor = con.cursor()

      sql = "SELECT * FROM carnet WHERE username = ?"
      username = session['username']
      cursor.execute(sql, (username,))
      liste_notes = cursor.fetchall()
      
      search = request.args.get('search')
      
        
      con.close()
      return render_template('dashboard.html', username=session['username'], data = liste_notes)
    
  return redirect(url_for("index"))


# ------------------- open add.html ------------------------

@app.route("/add")
def add():
    return render_template('add.html', username=session['username'])


# ------------------- Add new note ------------------------

@app.route("/addData", methods=["POST", "GET"])
def addData():
    if request.method=='POST':
        try:
            titre = request.form['titre']
            contenu = request.form['contenu']
            marquage = request.form['marquage']
            username = session['username']
            # Connexion a la base de donnée database.db
            con = sqlite3.connect("database.db")
            cur = con.cursor()
            # Requette sql et execution
            sql = "INSERT INTO carnet (titre, contenu, marquage, username) VALUES (?, ?, ?, ?)"
            value = (titre, contenu, marquage, username)
            cur.execute(sql, value)
            con.commit()
            # Fermer connection
            cur.close()
            con.close()
            # Message afficher si la requette est valider
            flash("Insertion SUCCESS","success")
            
        except sqlite3.Error as error:
            flash(f"Erreur d'insertion {error}","danger",)
        finally:
            return redirect(url_for("dashboard"))
            
    return render_template('add.html', username=session['username'])
            

# ------------------- Update ------------------------

@app.route('/update/<string:id>', methods=["POST", "GET"])
def update(id):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM carnet where id=?", (id))
    liste_notes = cursor.fetchone()
    con.close()
   
    if request.method == "POST":
        try:
          titre = request.form['titre']
          contenu = request.form['contenu']
          marquage = request.form['marquage']
          
          con = sqlite3.connect('database.db')
          cursor = con.cursor()
          print("Connexion réussie à SQLite")
          
          sql = "UPDATE carnet SET titre=?, contenu=?, marquage=? WHERE id=?"
          value = (titre, contenu, marquage, id)
          con.execute(sql, value)
          con.commit()
          flash("Update successfully", "success")
          
          cursor.close()
          con.close()
          print("Connexion SQLite est fermée")
          
        except sqlite3.Error as error:
          print("Erreur lors du mis à jour dans la table person", error)
          flash('Update error', 'danger')
        finally:
          return redirect(url_for("dashboard"))
    
    return render_template('update.html', username=session['username'], data = liste_notes)


# ------------------- Delete ------------------------

@app.route("/delete/<string:id>")
def delete(id):
    try:
      con = sqlite3.connect("database.db")
      cursor = con.cursor()
      cursor.execute("DELETE FROM carnet where id=?",(id))
      con.commit()
      flash("Delete successfully", "success")
    except:
      flash('Delete error', 'danger')
    finally:
      return redirect(url_for('dashboard'))


# ------------------- archive ------------------------

@app.route("/archive")
def archive():
    return render_template('archive.html', username=session['username'])
  

# ------------------- Login ------------------------

@app.route("/login", methods=["POST", "GET"])
def login():
    # check if username and password POST request exist
    if request.method == "POST" and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        # Check if user exists
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cursor = con.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? and password = ?",(username, password,))
        data = cursor.fetchone()
        # If user exists
        if data:
          # Create session data
            session['logged_in'] = True
            session['id'] = data['user_id']
            session["username"] = data["username"]
            # Redirect to home page
            return redirect(url_for('dashboard'))
        else:
            # If user doesn not exist
            flash("username ou password incorrect","danger")
     
    return render_template('login.html')
    
    
# ------------------- Sign up ------------------------

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
      try:
        username = request.form["username"]
        password = request.form["password"]
        confirm = request.form["confirm"]
        
        if password == confirm:
          con = sqlite3.connect("database.db")
          cursor = con.cursor()
          cursor.execute("INSERT INTO users(username,password,confirm) VALUES (?,?,?)",(username, password, confirm))
          con.commit()
          flash('Inscription valider', "success")
        else:
          flash('Password invalid', 'danger')
          return render_template('signup.html')
      except:
        flash('Username ou mot de passe existe dèja !', 'danger')
        return render_template('signup.html')
      finally:
        return render_template('login.html')
        
    return render_template('signup.html')


# ------------------- Logout ------------------------

@app.route("/logout")
def logout():
  # Remove session data
    session.pop('logged_in', None)
    session.pop('id', None)
    session.pop('username', None)
    
    # redirect to login page
    return redirect(url_for('index'))



if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run(port=5000,debug=True) 