from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user  # type: ignore
from app import db
from app.models import User, Role, UserRoles, GTNSettings, TestGame, TestGameResourceLog
from app.admin.forms import AssignRoleForm, CreateRoleForm, LevelRequirementsForm
from app.models import TestGameBuildingProgress, TestGameBuildingType, TestGameBuildings
from app.models import TestGameQuest, TestGameQuestProgress, TestGameQuestType, TestGameQuestRewards, RewardItemAssociation
from app.models import TestGameItem, TestGameInventory, TestGameInventoryItems, TestGameInventoryUser, TestGameInventoryType
from app.testgame.game_logic import GameService, GameCreation, GameBuildingService
from app.admin.decorators import admin_required
from app.admin import bp


## Admin Routes

@bp.route('/admin_home', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_home():


    return render_template("admin/admin_home.html", title='Admin Home')

@bp.route('/admin_users', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_users():

    user_roles = db.session.query(UserRoles).all()
    users = db.session.query(User).all()
    roles= db.session.query(Role).all()

    assign_role_form = AssignRoleForm()

    if request.method == 'POST' and assign_role_form.validate():

        assign_role = UserRoles(user_id=assign_role_form.user_id.data, 
                                role_id=assign_role_form.role_id.data)
        db.session.add(assign_role)
        db.session.commit()
        flash("Role Assigned")
        return redirect(url_for('admin.admin_users'))

    return render_template("admin/admin_users.html", 
                           title='Admin Users', 
                           users=users, 
                           assign_role_form=assign_role_form, 
                           roles=roles,
                           user_roles=user_roles)

@bp.route('/admin_roles', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_roles():
    roles = db.session.query(Role).all()
    roleform = CreateRoleForm()

    if request.method == 'POST' and roleform.validate():
        role = Role(name=roleform.role_name.data)
        db.session.add(role)
        db.session.commit()
        flash("Role Added")
        return redirect(url_for('admin.admin_roles'))

    return render_template("admin/admin_roles.html", title='Admin Roles', roles=roles, roleform=roleform)

@bp.route('/deactivate_user<user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def deactivate_user(user_id):
    user = db.session.query(User).get(user_id)
    user.active = False # Deactivate the user
    db.session.commit()
    flash("User Deactivated")

    return redirect(url_for('admin.admin_users'))

# This route is used to reactivate a user account
@bp.route('/activate_user/<user_id>', methods=['GET', 'POST'])
def activate_user(user_id):

    user = db.session.query(User).get(user_id)

    # Check if the user exists and is inactive
    if user:
        user.active = True

        # Create default GTNSettings for the user
        gtnsettings = GTNSettings(user_id=user_id, startrange=1, endrange=100)

        # Assign the user the default role
        assign_user_role = UserRoles(user_id=user_id, role_id=2)

        db.session.add(gtnsettings)
        db.session.add(assign_user_role)
        db.session.commit()
        flash("Account Reactivated")

        # Redirect to the login page (or admin users if admin)
        try:
            for role in current_user.role:
                if role.name == 'admin':
                    return redirect(url_for('admin.admin_users'))
            return redirect(url_for('auth.login'))
        except Exception as e:
            # Log the error if logging is set up
            print(f"Error: {e}")  # Replace with logging if applicable
            return redirect(url_for('auth.login'))
        
    # If the user does not exist or is already active
    else:
        return redirect(url_for('main.index'))

# This route is used to render a page that denies access to an admin page
@bp.route('/not_admin', methods=['GET', 'POST'])
@login_required
def not_admin():
    return render_template("admin/not_admin.html", title='Not Admin')






## Test Game Admin Routes
# This route is used to render the admin page for the test game users
@bp.route('/admin_testgame_models', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_testgame_models():

    testgames = db.session.query(TestGame).all()


    return render_template("admin/testgame/admin_testgame_models.html", 
                           title='Admin Test Game Users', 
                           testgames=testgames)


# This route is used to render the admin page for the test game xp log
@bp.route('/admin_testgame_resourceslog', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_testgame_resourceslog():

    resourcelogs = db.session.query(TestGameResourceLog).all()


    return render_template("admin/testgame/admin_testgame_resourceslog.html", 
                           title='Admin Test Game XP Log', 
                           resourcelogs=resourcelogs)

# This route is used to render the admin page for for test game level requirements
@bp.route('/admin_testgame_levelrequirements', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_testgame_levelrequirements():


    return render_template("admin/testgame/admin_testgame_levelrequirements.html", 
                           title='Admin Test Game Level Requirements')


# This route is used to render the admin page for the test game main quests
@bp.route('/admin_testgame_mainquests', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_testgame_mainquests():

    # Queries
    questtypes = db.session.query(TestGameQuestType).all()
    quests = db.session.query(TestGameQuest).all()
    questrewards  = db.session.query(TestGameQuestRewards).all()
    questprogresses = db.session.query(TestGameQuestProgress).all()
        

    return render_template("admin/testgame/admin_testgame_mainquests.html", 
                           title='Admin Test Game Main Quests',
                           quests=quests,
                           questtypes=questtypes,
                           questrewards=questrewards,
                           questprogresses=questprogresses)


# This route is used to render the admin page for the test game buildings
@bp.route('/admin_testgame_buildings', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_testgame_buildings():
    
    # Queries
    testgames = db.session.query(TestGame).all()
    buildingtypes = db.session.query(TestGameBuildingType).all()
    buildings = db.session.query(TestGameBuildings).all()
    buildingprogress = db.session.query(TestGameBuildingProgress).all()
    
    # Calculate Accrued Resources
    for building in buildingprogress:
        service = GameBuildingService(building_progress_id=building.id)
        accrued_resources = service.calculate_accrued_resources()
        building.accrued_resources = accrued_resources
    
    db.session.commit()   
        

    return render_template("admin/testgame/admin_testgame_buildings.html", 
                        title='Admin Test Game Buildings', 
                        testgames=testgames,
                        buildingtypes=buildingtypes,
                        buildings=buildings,
                        buildingprogress=buildingprogress)


# This route is used to render the admin page for the test game items
@bp.route('/admin_testgame_items', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_testgame_items():
    
    testgames = db.session.query(TestGame).all()
    items = db.session.query(TestGameItem).all()
    
    
    return render_template("admin/testgame/admin_testgame_items.html", 
                           title='Admin Test Game Items',
                           testgames=testgames,
                           items=items)

# This route is used to render the admin page for the test game inventories

@bp.route('/admin_testgame_inventories', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_testgame_inventories():
    
    testgames = db.session.query(TestGame).all()
    inventorytypes = db.session.query(TestGameInventoryType).all()
    inventories = db.session.query(TestGameInventory).all()
    game_inventories = db.session.query(TestGameInventoryUser).all()
    inventoryitems = db.session.query(TestGameInventoryItems).all()
    
    
    return render_template("admin/testgame/admin_testgame_inventories.html", 
                           title='Admin Test Game Inventories',
                           testgames=testgames,
                           inventorytypes=inventorytypes,
                           inventories=inventories,
                           game_inventories=game_inventories,
                           inventoryitems=inventoryitems)
