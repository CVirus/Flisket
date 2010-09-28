from flask import Flask, url_for, jsonify, request, Response, json, g
import urllib2, sqlite3

app = Flask(__name__)
DATABASE = 'poi.db'

def connect_db():
	return sqlite3.connect(DATABASE)

@app.before_request
def before_request():
	g.db = connect_db()

@app.after_request
def after_request(response):
	g.db.close()
	return response

def query_db(query, args=(), one=False):
	cur = g.db.execute(query, args)
	rv = [dict((cur.description[idx][0], value) for idx, value in enumerate(row)) for row in cur.fetchall()]
	return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
	return "Index Page !"

@app.route('/address', methods=['GET'])
def reverseGeoCode():
	lat = request.args.get('lat')
	lng = request.args.get('lng')
	addressURL = "http://maps.google.com/maps/api/geocode/json?latlng=" + str(lat) + "," + str(lng) + "&sensor=false"
	response = urllib2.urlopen(addressURL)
	jsonData = response.read()
	return Response(jsonData, content_type='application/json; charset=UTF-8')

@app.route('/poi', methods=['GET', 'POST'])
def pointOfInterest():
	if request.method == 'POST':
		lat = request.form.get('lat')
		lng = request.form.get('lng')
		address = request.form.get('address')
		try:
			inputStatus = query_db('insert into places (lat, lng, address) values (?, ?, ?)', [lat, lng, address], one=True)
			g.db.commit()
			return jsonify(status="Success", msg="Place added")
		except:
			return jsonify(status="Error", msg="Place probably exists")
	else:
		lat = request.args.get('lat')
		lng = request.args.get('lng')
		place = query_db('select * from places where lat = ? and lng = ?', [lat, lng], one=True)
		if place is None:
			return jsonify(status="Error", msg="Place doesn't exist")
		else:
			placeID = place['placeID']
			#comments = query_db('select comment from comments where placeID = ?', [placeID], one=True)
			#return str(comments)
			comments = []
			for comment in query_db('select comment from comments where placeID = ?', [placeID]):
				comments.append(comment)
			#return str(comments)
			return jsonify(status="Success", msg="", comments=query_db('select comment from comments where placeID = ?', [placeID]))

			#print the_username, 'has the id', user['user_id']

		pass
		#display all info(id, lat, lng, address, comments) for this poi


@app.route('/comment', methods=['POST'])
def comment():
	lat = request.form.get('lat')
	lng = request.form.get('lng')
	comment = request.form.get('comment')
	place = query_db('select placeID from places where lat = ? and lng= ?', [lat, lng], one=True)
	if place is None:
		return jsonify(status="Error", msg="Place doesn't exist")
	else:
		placeID = place['placeID']
		inputStatus = query_db('insert into comments (placeID, comment) values (?, ?)', [placeID, comment], one=True)
		g.db.commit()
		return jsonify(status="Success", msg="Comment added")

"""
@app.route('/login')
def login():
	pass

@app.route('/hello')
def hello():
	return "Hello World !"

@app.route('/user/<username>')
def profile(username):
	#x = "hello there <b>" + username + "</b>"
	#return jsonify(x)
	#pass

@app.route('/post/<int:post_id>')
def show_post(post_id):
	#return "This is post number: " + str(post_id)

@app.route('/foo')
def foo():
	#pass

@app.route('/projects/')
def projects():
	return "projects"

@app.route('/about')
def about():
	return "about"
"""
with app.test_request_context():
	print url_for('index')
	print url_for('login')
	print url_for('login', next='/')
	print url_for('profile', username='John Doe')

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)
