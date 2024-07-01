from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.financeapp.forms import TransactionForm, AccountForm, TransactionCategoryForm
from app.models import Transaction, Account, TransactionCategory
from app import db
from app.financeapp import bp



#PERSONAL ROUTES

@bp.route('/pfhome', methods=['GET', 'POST'])
@login_required
def pfhome():

    transactionform = TransactionForm(request.form)
    accountform = AccountForm(request.form)
    transactioncategoryform = TransactionCategoryForm(request.form)
    
    # Query to return user specific transactions
    transactions = []
    try:
        transactions = db.session.query(Transaction).filter_by(user_id=current_user.id).all()
    except Exception as e:
        print("Error in view all transactions",e )

    # Process Transaction Form and update the database
    if request.method == 'POST' and transactionform.validate():
        transaction = Transaction(transaction_date=transactionform.transaction_date.data,
                                  category_id=transactionform.category_id.data, 
                                  account_id=transactionform.account_id.data, 
                                  user_id=current_user.id,
                                  item_name=transactionform.item_name.data,
                                  amount=transactionform.amount.data)
        db.session.add(transaction)
        db.session.commit()
        flash("Transaction Added")

        return redirect(url_for('financeapp.pfhome'))
    
    # Query to return user specific accounts
    accounts = []
    try:
        accounts = db.session.query(Account).filter_by(user_id=current_user.id).all()
    except Exception as e:
        print("Error in view all accounts", e)
    
    # Process Account Form and update the database
    if request.method == 'POST' and accountform.validate():
        account = Account(account_name=accountform.account_name.data, 
                                  user_id=current_user.id)
        db.session.add(account)
        db.session.commit()
        flash("Account Added")

        return redirect(url_for('financeapp.pfhome'))
    
    # Query to return user specific categories
    categories = []
    try:
        categories = db.session.query(TransactionCategory).filter_by(user_id=current_user.id).all()
    except Exception as e:
        print("Error in categories", e)

    # Process TransactionCategory Form and update the database
    if request.method == 'POST' and transactioncategoryform.validate():
        category = TransactionCategory(category_name=transactioncategoryform.category_name.data,
                                       user_id=current_user.id)
        db.session.add(category)
        db.session.commit()
        flash("Category Added")

        return redirect(url_for('financeapp.pfhome'))

    
    
    return render_template("financeapp/pfhome.html", 
                           title='Personal Finance', 
                           transactionform=transactionform, 
                           transactions=transactions,
                           accountform=accountform,
                           accounts=accounts,
                           transactioncategoryform=transactioncategoryform,
                           categories=categories)