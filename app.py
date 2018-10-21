import datetime
import markdown
from flask import Flask, render_template, request, session, redirect, url_for, flash

from mongo_db import MongoDBClient

app = Flask(__name__)
db_client = MongoDBClient()

# used to sign the session cookie
app.secret_key = '\x86\xdb;\x91\x9dQfX4\x151\xc0\xf1\x9c\xc1\xac\x87\xb1uk\x19$\xd0\xbb'


def from_txt_to_html(txt):
    return markdown.markdown(txt)


app.jinja_env.globals.update(from_txt_to_html=from_txt_to_html)


def is_logged_in():
    if 'user' in session:
        return True
    return False


@app.route('/')
def post_list():
    page = int(request.args.get('page', 1))
    posts = db_client.get_lists(page)
    next_page = page + 1
    pre_page = page - 1
    total_page = db_client.get_total_page()
    return render_template('index.html', posts=posts, action='list', current_page=page, next_page=next_page,
                           pre_page=pre_page, total_page=total_page)


@app.route('/show/<post_id>')
def show_post(post_id):
    post = db_client.get_post(post_id)
    if post:
        return render_template('index.html', posts=[post], action='show')
    else:
        flash('Can not find post', 'warning')
        return redirect(url_for('post_list'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login_form.html')

    if request.method == 'POST':
        user = db_client.find_user({'name': request.form['user_name'], 'password': request.form['password']})
        if user:
            session['user'] = user['name']
            msg = 'Login successfully!'
            msg_type = 'success'
            action = 'post_list'
        else:
            msg = 'Can not login!'
            msg_type = 'danger'
            action = 'login'

        flash(msg, msg_type)
        return redirect(url_for(action))


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logout successfully', 'info')
    return redirect(url_for('post_list'))


@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if not is_logged_in():
        flash('You should login first', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = request.form.to_dict()
        data['created_at'] = data['updated_at'] = datetime.datetime.now()
        data['creator'] = session['user']

        if not data['title']:
            flash('Title can not be empty', 'warning')
            return render_template('edit_post_form.html', post=data)

        if db_client.create_post(data):
            flash('Create post successfully', 'success')
            return redirect(url_for('post_list'))
        else:
            flash('Failed to create post', 'danger')
            return redirect(url_for('create_post'))

    return render_template('create_post_form.html')


@app.route('/edit_post/<post_id>')
def edit_post(post_id):
    if not is_logged_in():
        flash('You should login first', 'danger')
        return redirect(url_for('login'))

    post = db_client.get_post(post_id)
    if post:
        return render_template('edit_post_form.html', post=post)
    else:
        flash('Can not find this post', 'warning')
        return redirect(url_for('post_list'))


@app.route('/update_post', methods=['POST'])
def update_post():
    if not is_logged_in():
        flash('You should login first', 'danger')
        return redirect(url_for('login'))

    data = request.form.to_dict()
    if not data['title']:
        flash('Title can not be empty', 'warning')
        return render_template('edit_post_form.html', post=data)

    data['updated_at'] = datetime.datetime.now()
    post_id = data.pop('id', None)
    db_client.update(post_id, data)
    flash('Edit successfully', 'success')
    return redirect(url_for('show_post', post_id=post_id))


@app.route('/delete_post/<post_id>')
def del_post(post_id):
    if not is_logged_in():
        flash('You should login first', 'danger')
        return redirect(url_for('login'))

    post = db_client.get_post(post_id)
    if post:
        db_client.delete_post(post_id)
        flash('Delete successfully', 'success')
        return redirect(url_for('post_list'))
    else:
        flash('Can not find this post to delete', 'warning')
        return redirect(url_for('post_list'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
