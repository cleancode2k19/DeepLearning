import os
import re
import uuid
from datetime import datetime

import numpy as np
from flask import Flask, json, render_template, flash, request, redirect, session, send_from_directory, url_for

from pandas import *
import pandas as pd
from textblob import TextBlob
from werkzeug.utils import secure_filename
import xlrd
from os import listdir
from os.path import isfile, join


UPLOAD_FOLDER = './uploaded_files/'
OUTPUT_FOLDER = './output_files/'
DOMAINS_DICT = './domains_dictionary'


app = Flask(__name__)
app_name = 'VOXPopuli'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOMAINS_DICT'] = DOMAINS_DICT
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
app.secret_key = os.urandom(24)
ALLOWED_EXTENSIONS = set(['xlsx'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/')
def Index():
    title = 'Index'
    return render_template('index.html', title=title, app_name=app_name,scroll='intro'), 200



@app.route('/upload')
def upload_dictionary():
    title = 'upload'
    onlyfiles = [f for f in listdir(app.config['DOMAINS_DICT']) if isfile(join(app.config['DOMAINS_DICT'], f))]
    return render_template('index.html', title=title, scroll='wrap', app_name=app_name, onlyfiles = onlyfiles, asr = len(onlyfiles) ), 200



@app.route('/dictionary_uploader', methods=['GET','POST'])
def dictionary_uploader():
    if request.method == 'POST':
        nnn=request.form.get('Dictionary')
        if nnn:
            dic_fileloc = os.path.join(app.config['DOMAINS_DICT'],nnn)
        # check if the post request has the file part
        else:    
            if 'file' not in request.files:
                flash('There are no files to be uploaded')
                return redirect(request.url)
            dic_file = request.files['file']
            if dic_file.filename == '':
                flash('No file selected for uploading')
                return redirect(request.url)
    
            if dic_file and allowed_file(dic_file.filename):
                dic_filename = secure_filename(dic_file.filename)
                dic_fileloc = os.path.join(app.config['DOMAINS_DICT'], dic_filename)
                dic_file.save(dic_fileloc)
        session['dic_fileloc'] = dic_fileloc
        dm_names = getdic(session['dic_fileloc'])
        dm_names = dm_names.tolist()

        session['dm_names']=dm_names
        return render_template('index.html', title="radio",scroll='wrap', app_name=app_name, dm_names = dm_names, le = len(dm_names)),200
    else:
        flash('Only xlsx files are allowed to be uploaded')
        return redirect(request.url)

@app.route('/radio', methods=['GET', 'POST'])
def radio():
    if request.method == 'GET':
        dm_names = session.get('dm_names')
        r_l = []
    if request.method == 'POST':
        dm_names = session.get('dm_names')
        r = request.form.getlist('mycheckbox')
        r_l = [x for x in dm_names if x not in r]
    session['r_l'] = r_l
    return redirect(url_for('upload_file'))
@app.route('/clear_com')
def clear_com():
    msgo =''
    folder = app.config['OUTPUT_FOLDER']
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            msgo = "Direcotry of Output Folder clear."
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    return render_template('index.html', title="clear_com",scrollTo='clrCom',msgo=msgo, app_name=app_name),500

@app.route('/clear_doc')
def clear_doc():
    msg =''
    folder = app.config['UPLOAD_FOLDER']
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            msg = "Direcotry of Upload Folder clear."
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    return render_template('index.html', title="clear_doc",scrollTo='clrDoc', msg=msg, app_name=app_name),500

@app.route('/upload_file')
def upload_file():

    return render_template('index.html', title="upload_file",scroll='wrap', app_name=app_name),500
    #return redirect(url_for('upload_file'))
@app.route("/uploader", methods=['GET', 'POST'])
def uploader():
    if request.method == 'POST':
        # check if the post request has the file part
    
        if 'file' not in request.files:
            flash('There are no files to be uploaded')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            now = datetime.now()
            timestamp = datetime.timestamp(now)
            uniqueid = str(uuid.uuid4())
            filetosave = uniqueid + '_' + str(timestamp) + '_' + filename
            fileloc = os.path.join(app.config['UPLOAD_FOLDER'], filetosave)
            file.save(fileloc)
            outputfilename = 'output_' + os.path.splitext(filetosave)[0] + '.csv'
            outloc = os.path.join(app.config['OUTPUT_FOLDER'], outputfilename)
            session['outputfile'] = outputfilename
            session['outloc'] = outloc
            session['fileloc'] = fileloc
            return results()
        else:
            flash('Only xlsx files are allowed to be uploaded')
            return redirect(request.url)

@app.route('/download_output/')
def downloader():
    if 'outputfile' in session:
        return send_from_directory(app.config['OUTPUT_FOLDER'], session['outputfile'], as_attachment=True), 200
    else:
        return 'error', 404


@app.route("/results", methods=['GET', 'POST'])
def results():
    title = 'Results'
    if request.method=='POST':
        dm_names = session.get('dm_names')
        multiselect = request.form.getlist('fu')
        if multiselect == []:
            r_l = session.get('r_l')
        else:
            #r_l = multiselect
            r_l = [x for x in dm_names if x not in multiselect]
        
        domains, l, l_t = getResults(session['fileloc'], session['dic_fileloc'], r_l, session['outloc'])
        overall = json.dumps(domains, cls=NumpyEncoder)
        return render_template('results.html', title=title, app_name=app_name, overall = overall, l = l, k = len(l), l_t = l_t, dm_names= dm_names, le = len(dm_names)), 200

def getdic(domains_file):
    xls = ExcelFile(domains_file)  # synonyms for domains
    df = xls.parse(xls.sheet_names[0])
    df = df.drop(df.columns[0], axis=1)
    a = []
    for i in range(len(df.columns)):
        if (df.columns[i] == df.iloc[0, i]):
            a.append(i)
    if len(a) == 0:
        x = df.iloc[1, 0]
        a.append(0)
        for i in range(1, len(df.columns)):
            y = "[0-9]"
            pattern = re.compile((x + y))
            place = df.iloc[1, i]
            if not (pattern.search(place)):
                a.append(i)
                x = df.iloc[1, i]
    df.columns = df.iloc[0, :]
    df = df.drop([0, 1], axis=0)
    df = df.reset_index(drop=True)
    dm = df.iloc[:, a]
    dm_names = dm.columns
    return dm_names

def getdictionary(domains_file, r_l):
    xls = ExcelFile(domains_file)  # synonyms for domains
    df = xls.parse(xls.sheet_names[0])
    df = df.drop(df.columns[0], axis=1)
    a = []
    for i in range(len(df.columns)):
        if (df.columns[i] == df.iloc[0, i]):
            a.append(i)
    if len(a) == 0:
        x = df.iloc[1, 0]
        a.append(0)
        for i in range(1, len(df.columns)):
            y = "[0-9]"
            pattern = re.compile((x + y))
            place = df.iloc[1, i]
            if not (pattern.search(place)):
                a.append(i)
                x = df.iloc[1, i]
    df.columns = df.iloc[0, :]
    df = df.drop([0, 1], axis=0)
    df = df.reset_index(drop=True)
    dm = df.iloc[:, a]
    sd = []
    for i in range(1, len(a)):
        sd.append(df.iloc[:, a[i - 1] + 1:a[i]])
    sd.append(df.iloc[:, a[i] + 1:])
    b = []
    for i in range(len(dm.columns)):
        for j in range(len(r_l)):
            if (dm.columns[i] == r_l[j]):
                b.append(i)
    dm = dm.drop(dm.columns[b], axis=1)
    count = 0
    for i in range(len(b)-1):
        b[i] = b[i] - count
        sd.pop(b[i])
        count = count+1
        
        
    return dm, sd


def getreviews(comments_file):
    xls = ExcelFile(comments_file)
    df1 = xls.parse(xls.sheet_names[0])
    df1.columns = ['IMPROVE']
    return df1


def dandsd(df1, dm, sd):
    St = df1['IMPROVE'].tolist()
    li = dm.columns.tolist()
    for x in St:
        St1 = x
        a = []
        cc = []
        aa, bb = np.where(df1.values == St1)
        cou = 0
        tokens = [t.strip() for t in re.findall(r'\b.*?\S.*?(?:\b|$)', St1.lower())]
        for y in tokens:
            cou = cou + 1
            if (y == "," or y == "." or y == "!" or y == "?" or y == ";"):
                cou = cou - 1
            else:
                s = (dm == y).any()
                p = s.index[s]
                if (p.any() != 0):
                    if (len(p) > 1):
                        for i in p:
                            a.append(str(i))
                    else:
                        a.append(str(p[0]))
        a = np.unique(a)
        r, c = df1.shape
        if (len(a) != 0):
            df1.at[aa[0], bb[0] + 1] = a[0]
            for i in range(len(a) - 1):
                r1, c1 = df1.shape
                df1.at[r1, "IMPROVE"] = St1
                df1.at[r1, 1] = a[i + 1]
    df1 = df1.sort_values('IMPROVE')
    df1 = df1.reset_index(drop=True)
    r, c = df1.shape
    for i in range(r):
        countf = -1
        for xy in li:
            countf = countf + 1
            if (df1.iat[i, 1] == xy):
                tokens = [t.strip() for t in re.findall(r'\b.*?\S.*?(?:\b|$)', df1.iat[i, 0].lower())]
                b = []
                for y in tokens:
                    cou = cou + 1
                    if (y == "," or y == "." or y == "!" or y == "?" or y == ";"):
                        cou = cou - 1
                    else:
                        s = (sd[countf] == y).any()
                        p = s.index[s]
                        if (p.any() != 0):
                            if (len(p) > 1):
                                for k in p:
                                    b.append(str(k))
                            else:
                                b.append(str(p[0]))
                b = np.unique(b)
                if (len(b) != 0):
                    df1.at[i, 2] = b[0]
                    for j in range(len(b) - 1):
                        r1, c1 = df1.shape
                        df1.at[r1, "IMPROVE"] = df1.iat[i, 0]
                        df1.at[r1, 1] = df1.iat[i, 1]
                        df1.at[r1, 2] = b[j + 1]

    df1 = df1.sort_values('IMPROVE')
    df1 = df1.reset_index(drop=True)
    return (df1)

def getsentiment(df1):
    stemmed_sentences = df1['IMPROVE'].tolist()
    count = -1
    for row in stemmed_sentences:
        count = count + 1
        analysis = TextBlob(row)
        a = analysis.sentiment
        if a.polarity >= 0.1:
            df1.at[count, 3] = "positive"
        else:
            df1.at[count, 3] = "negative"
        df1.at[count, 4] = a.polarity     
    return df1


def store(df, url):
    df.columns = ['Comments', 'Domain', 'SUB-DOMAIN', 'SENTIMENT','SCORE']
    df.to_csv(url)


def createResultObj(newdf):
    newdf.columns = ['IMPROVE', 'DOMAIN', 'SUBDOMAIN', 'SENTIMENT', 'SCORE']
    g1 = newdf.groupby(["DOMAIN", "SUBDOMAIN", "SENTIMENT"]).count().reset_index()
    domnames = g1.DOMAIN.unique()
    l=[]
    l_t = domnames
    domains = {
        'chartTitle': 'Overall Results across all Domains',
        'labels': [],
        'positive': [],
        'negative': [],
        'both': [],
        'score': []
    }
    for i in range (len(l_t)):
        l.append ({
            #'chartTitle': 'Results for Comments on l[i]',
            'labels': [],
            'positive': [],
            'negative': [],
            'both': [],
            'score': []
            })

    
    for dom in domnames:
    
        dpcount = 0
        dncount = 0
        domains['labels'].append(dom)
        sc = newdf.query('DOMAIN == @dom').SCORE.unique()
        sdomnames = g1.query('DOMAIN == @dom').SUBDOMAIN.unique()
        for sdom in sdomnames:
            tp = g1.query('DOMAIN == @dom and SUBDOMAIN == @sdom and SENTIMENT == "positive"').IMPROVE.sum()
            tn = g1.query('DOMAIN == @dom and SUBDOMAIN == @sdom and SENTIMENT == "negative"').IMPROVE.sum()
          
            dpcount += tp
            dncount += tn
            for i in range(len(l_t)):
                if(l_t[i] == dom):
                    l[i]['labels'].append(sdom)
                    l[i]['positive'].append(int(tp))
                    l[i]['negative'].append(int(tn))
                    l[i]['both'].append(int(tn)+int(tp))
        domains['positive'].append(int(dpcount))
        domains['negative'].append(int(dncount))
        domains['both'].append(int(dpcount) + int(dncount))
        domains['score'].append(sc)
    return domains, l, l_t

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
            np.int16, np.int32, np.int64, np.uint8,
            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, 
            np.float64)):
            return float(obj)
        elif isinstance(obj,(np.ndarray,)): #### This is the fix
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def getResults(fileloc, dic_fileloc, r_l, outloc):
    #domainsDictFilename = "Domains-and-subdomains.xlsx"
    dm, sd = getdictionary(dic_fileloc, r_l)
    df1 = getreviews(fileloc)
    df1 = dandsd(df1, dm, sd)
    df1 = getsentiment(df1)
    store(df1, outloc)
    domains, l, l_t = createResultObj(df1)
    return domains, l, l_t


if __name__ == '__main__':
    app.run()

