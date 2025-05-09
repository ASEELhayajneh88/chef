from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from werkzeug.utils import secure_filename
from collections import defaultdict

# إنشاء قاعدة البيانات إذا لم تكن موجودة
def create_db():
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    ingredients TEXT NOT NULL,
                    instructions TEXT NOT NULL,
                    image TEXT,
                    confidence REAL NOT NULL)''')
    conn.commit()
    conn.close()

create_db()

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# بيانات تسجيل دخول الأدمن
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.args.get('next', url_for('admin_dashboard', action='add'))  # افتراضي: إضافة وصفة
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            # التحقق من أن next_page آمن
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('admin_dashboard', action='add')
            return redirect(next_page)
        else:
            flash('بيانات تسجيل الدخول غير صحيحة', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route('/recipes')
def recipes():
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute('SELECT * FROM recipes')
    recipes = c.fetchall()
    conn.close()
    return render_template('recipes.html', recipes=recipes)

@app.route('/search', methods=['GET', 'POST'])
def search():
    recipes = []
    query = ''
    results_with_confidence = []

    if request.method == 'POST':
        query = request.form['query'].strip()
        conn = sqlite3.connect('recipes.db')
        c = conn.cursor()

        c.execute("SELECT * FROM recipes WHERE title LIKE ?", ('%' + query + '%',))
        recipes = c.fetchall()

        if not recipes:
            c.execute("SELECT * FROM recipes")
            all_recipes = c.fetchall()
            query_ingredients = [x.strip().lower() for x in query.replace('،', ',').split(',')]
            scores = defaultdict(float)

            for recipe in all_recipes:
                ingredients = [ing.strip().lower() for ing in recipe[2].split(',')]
                intersection = set(ingredients) & set(query_ingredients)
                if intersection:
                    confidence = len(intersection) / len(set(query_ingredients))
                    scores[recipe] = confidence

            results_with_confidence = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            recipes = [(r[0][0], r[0][1], r[0][2], r[0][3], r[0][4], r[1]) for r in results_with_confidence]

        conn.close()

    return render_template('search.html', recipes=recipes, query=query, results_with_confidence=results_with_confidence)

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
        c.execute('INSERT INTO recipes (title, ingredients, instructions, image, confidence) VALUES (?, ?, ?, ?, ?)',
                  (title, ingredients, instructions, image_filename, 1.0))
        conn.commit()
        conn.close()
        flash('تمت إضافة الوصفة بنجاح!', 'success')
        return redirect(url_for('recipes'))

    return render_template('add_recipe.html')

@app.route('/edit_all')
def edit_all():
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute('SELECT * FROM recipes')
    recipes = c.fetchall()
    conn.close()

    return render_template('edit_all.html', recipes=recipes)

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

        image_filename = recipe[4]
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

@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    if not session.get('admin'):
        return redirect(url_for('login'))

    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute('SELECT image FROM recipes WHERE id = ?', (recipe_id,))
    recipe = c.fetchone()
    if recipe and recipe[0]:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], recipe[0]))
        except FileNotFoundError:
            pass

    c.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,))
    conn.commit()
    conn.close()
    flash('تم حذف الوصفة بنجاح!', 'danger')
    return redirect(url_for('edit_all'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        # تمرير next للعودة إلى نفس الصفحة بعد تسجيل الدخول
        return redirect(url_for('login', next=request.url))

    action = request.args.get('action', 'add')  # القيمة الافتراضية "add"

    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM recipes')
    total_recipes = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM recipes WHERE image IS NOT NULL AND image != ""')
    recipes_with_images = c.fetchone()[0]

    recipes_without_images = total_recipes - recipes_with_images

    if action == 'edit_all':
        c.execute('SELECT * FROM recipes')
        recipes = c.fetchall()
        conn.close()
        return render_template('edit_all.html', recipes=recipes,
                              total=total_recipes,
                              with_images=recipes_with_images,
                              without_images=recipes_without_images)
    else:  # action == 'add' or any other value
        conn.close()
        return render_template('add_recipe.html', total=total_recipes,
                              with_images=recipes_with_images,
                              without_images=recipes_without_images)


if __name__ == '__main__':
    app.run(debug=True)


