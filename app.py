from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# معرف المستخدم والبيانات
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'

# التحقق من امتدادات الملفات
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# الصفحة الرئيسية
@app.route('/')
def home():
    return render_template('home.html')

# تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('add_recipe'))
        else:
            flash('بيانات تسجيل الدخول غير صحيحة', 'danger')
    return render_template('login.html')

# تسجيل الخروج
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

# عرض الوصفات
@app.route('/recipes')
def recipes():
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute('SELECT * FROM recipes')
    recipes = c.fetchall()
    conn.close()
    return render_template('recipes.html', recipes=recipes)

# البحث عن وصفات
@app.route('/search', methods=['GET', 'POST'])
def search():
    recipes = []
    query = ''
    if request.method == 'POST':
        query = request.form['query']
        conn = sqlite3.connect('recipes.db')
        c = conn.cursor()
        c.execute("SELECT * FROM recipes WHERE title LIKE ?", ('%' + query + '%',))
        recipes = c.fetchall()
        conn.close()
    return render_template('search.html', recipes=recipes, query=query)

# إضافة وصفة جديدة
@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if not session.get('admin'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        image = request.files['image']

        image_filename = None
        if image and image.filename != '':
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        conn = sqlite3.connect('recipes.db')
        c = conn.cursor()
        c.execute('INSERT INTO recipes (title, ingredients, instructions, image) VALUES (?, ?, ?, ?)',
                  (title, ingredients, instructions, image_filename))
        conn.commit()
        conn.close()
        flash('تمت إضافة الوصفة بنجاح!', 'success')
        return redirect(url_for('recipes'))

    return render_template('add_recipe.html')

# تعديل الوصفة
@app.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute('SELECT * FROM recipes WHERE id = ?', (recipe_id,))
    recipe = c.fetchone()

    if request.method == 'POST':
        title = request.form['title']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        image = request.files['image']

        image_filename = recipe[4]  # الاحتفاظ بالصورة القديمة إذا لم يتم تحميل صورة جديدة
        if image and image.filename != '':
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        c.execute('UPDATE recipes SET title = ?, ingredients = ?, instructions = ?, image = ? WHERE id = ?',
                  (title, ingredients, instructions, image_filename, recipe_id))
        conn.commit()
        conn.close()
        flash('تمت عملية التعديل بنجاح!', 'success')
        return redirect(url_for('recipes'))

    conn.close()
    return render_template('edit_recipe.html', recipe=recipe)

# حذف الوصفة
@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute('SELECT image FROM recipes WHERE id = ?', (recipe_id,))
    recipe = c.fetchone()
    if recipe[0]:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], recipe[0]))  # حذف الصورة إذا كانت موجودة

    c.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,))
    conn.commit()
    conn.close()
    flash('تم حذف الوصفة بنجاح!', 'danger')
    return redirect(url_for('recipes'))

if __name__ == '__main__':
    app.run(debug=True)
