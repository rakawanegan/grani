import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# アップロードされたファイルを保存するディレクトリ
UPLOAD_FOLDER = 'temp'
OUTPUT_FOLDER = 'output'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

@app.route('/')
def upload_form():
    return render_template('form.html')

@app.route('/', methods=['POST'])
def upload_file():
    # アップロードされたファイルを取得
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        # ファイルを指定されたディレクトリに保存
        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename))
        return redirect(url_for('upload_success'))
    else:
        return 'ファイルが選択されていません'

@app.route('/upload_success')
def upload_success():
    return render_template('success.html')

@app.route('/collect_results', methods=['GET'])
def collect_results():
    # ここでアンケート結果を回収する処理を実行
    return redirect(url_for('upload_success'))

if __name__ == '__main__':
    app.run(debug=True)