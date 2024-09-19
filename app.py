from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config, db
from deposit import deposit
from withdraw import withdraw

app = Flask(__name__)
app.config.from_object(Config)  # Load configurations




@app.route('/')
def index():
    """
    Render the dashboard page if user is logged in,
    otherwise redirect to login page.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM expenses WHERE user_id = %s AND is_deleted = FALSE",
        (session['user_id'],)
    )
    expenses = cursor.fetchall()
    cursor.close()

    return render_template('dashboard.html', expenses=expenses)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handle user signup. If request method is POST, create a new user.
    """
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        cursor = db.cursor()
        try:
            cursor.execute(
                """INSERT INTO users (username, email, password)
                VALUES (%s, %s, %s)""",
                (username, email, hashed_password)
            )
            db.commit()
            flash('Account created successfully. Please log in.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            cursor.close()

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login. If request method is POST,
    verify credentials and set session.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute(
            "SELECT id, password FROM users WHERE username = %s", (username,)
        )
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """
    Log out the current user and redirect to login page.
    """
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/transaction')
def transaction():
    """
    Render the transaction page where users can deposit or withdraw funds.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('transaction.html')

@app.route('/add_expense', methods=['POST'])
def add_expense():
    """
    Add a new expense for the logged-in user.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    category = request.form['category']
    amount = request.form['amount']
    date = request.form['date']

    cursor = db.cursor()
    cursor.execute(
        """INSERT INTO expenses (user_id, category, amount, date)
        VALUES (%s, %s, %s, %s)""",
        (session['user_id'], category, amount, date)
    )
    db.commit()
    cursor.close()

    return redirect(url_for('manage_expenses'))


@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    """
    Mark an expense as deleted for the logged-in user.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = db.cursor()
    cursor.execute(
        "UPDATE expenses SET is_deleted = TRUE WHERE id = %s AND user_id = %s",
        (expense_id, session['user_id'])
    )
    db.commit()
    cursor.close()

    return redirect(url_for('manage_expenses'))


@app.route('/manage_expenses')
def manage_expenses():
    """
    Display all non-deleted expenses for the logged-in user.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM expenses WHERE user_id = %s AND is_deleted = FALSE",
        (session['user_id'],)
    )
    expenses = cursor.fetchall()
    cursor.close()

    return render_template('manage_expenses.html', expenses=expenses)


@app.route('/history')
def history():
    """
    Render the history page for the logged-in user.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('history.html')


@app.route('/account', methods=['GET', 'POST'])
def account():
    """
    Handle user account updates. If request method is POST,
    update the user's information.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = db.cursor()
    if request.method == 'POST':
        new_username = request.form['username']
        new_email = request.form['email']
        new_password = request.form['password']

        if new_password:
            hashed_password = generate_password_hash(new_password)
            cursor.execute(
                """UPDATE users SET username = %s, email = %s,
                password = %s WHERE id = %s""",
                (new_username, new_email, hashed_password, session['user_id'])
            )
        else:
            cursor.execute(
                "UPDATE users SET username = %s, email = %s WHERE id = %s",
                (new_username, new_email, session['user_id'])
            )

        db.commit()
        cursor.close()

        flash('Account updated successfully.', 'success')
        return redirect(url_for('account'))

    cursor.execute(
        "SELECT username, email FROM users WHERE id = %s",
        (session['user_id'],)
    )
    user = cursor.fetchone()
    cursor.close()

    return render_template('account.html', user=user)


@app.route('/deposit', methods=['POST'])
def handle_deposit():
    """
    Handle deposit requests.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        amount = float(request.form['amount'])
        deposit(session['user_id'], amount)
        flash('Deposit successful!', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')

    return redirect(url_for('index'))

@app.route('/withdraw', methods=['POST'])
def handle_withdrawal():
    """
    Handle withdrawal requests.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    try:
        amount = float(request.form['amount'])
        withdraw(session['user_id'], amount)
        flash('Withdrawal successful!', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)