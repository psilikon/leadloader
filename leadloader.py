import time, MySQLdb, random, json, os, itertools, csv, time
from collections import defaultdict
from flask import (Flask, request, render_template, jsonify, redirect, session, abort, url_for, Response, flash, escape)
from werkzeug import secure_filename


app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['UPLOAD_FOLDER'] = '/var/www/leadloader/uploads/'


@app.route('/stream', methods=['POST','GET'])
def stream():
	def cmdResponse():
		yield "<p>running command</p>"
		with open(app.config['UPLOAD_FOLDER']+'1422696865.csv') as f:
			for line in f:
				time.sleep(.025)
				yield line+"<br>"
	return Response(cmdResponse(), mimetype="text/html")

@app.route('/processUpload', methods=['GET','POST'])
def processUpload():
	valueList = []
	keyList = []
	for k, v in request.json.iteritems():
		valueList.append(str(v))
		keyList.append(str(k))
	db = MySQLdb.connect(user="root", passwd="po12Kch0pz", host="127.0.0.1", db="datastore")
	conn = db.cursor()
	epoch = int(time.time())
	csvOutputFile = app.config['UPLOAD_FOLDER']+str(epoch)+'.csv'
	with open(csvOutputFile, 'w') as outputFile:
		reader = csv.DictReader(open(session['filename'], 'rb'), delimiter=',')   
		writer = csv.writer(outputFile, delimiter=',')
		for row in reader:
			rowList = []
			for header in valueList:
				rowList.append(row[header])
			writer.writerow(rowList)
	columns = ', '.join(keyList)
	#format_strings = ','.join(['%s'] * len(keyList))
#	conn.execute("LOAD DATA INFILE '/var/www/leadloader/uploads/test.csv' INTO TABLE LEADS FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 ROWS (%s)" % columns)
	conn.execute("LOAD DATA INFILE '%s' INTO TABLE LEADS FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' (%s)" % (csvOutputFile, columns))
	return render_template('/test.html')

@app.route('/upload', methods=['GET','POST'])
def upload():
	db = MySQLdb.connect(user="cron", passwd="1234", host="127.0.0.1", db="datastore")
	conn = db.cursor()
	conn.execute("SHOW COLUMNS FROM LEADS")
	fields = []
	result = conn.fetchall()
	for item in result:
		fields.append(str(item[0]))
	file = request.files['file']
	filename = secure_filename(file.filename)
	file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	reader = csv.DictReader(open(app.config['UPLOAD_FOLDER']+filename, 'rb'), delimiter=',')   
	headerList = []
	for row in itertools.islice(reader,1):
		headerRow = row
	for item in headerRow:
		if str(item) != 'None' and str(item) != '':
			headerList.append(item)
	session['filename'] = app.config['UPLOAD_FOLDER']+filename
	return render_template('/fieldmap.html', valueList=headerList, keyList=fields)

@app.route('/', methods=['POST','GET'])
def index():
	return render_template('/index.html')

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)

