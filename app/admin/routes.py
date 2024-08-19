from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user  # type: ignore
from app import db
from app.models import User, Role, UserRoles, Game, ResourceLog
from app.admin.forms import AssignRoleForm, CreateRoleForm
from app.models import BuildingProgress, BuildingType, Buildings
from app.models import Quest, QuestProgress, QuestType, QuestRewards, QuestRequirements, QuestPrerequisites, QuestPreRequisitesProgress, QuestRequirementProgress
from app.models import Item, Inventory, InventoryItems, InventoryUser, InventoryType
from app.models import Hero, HeroProgress, HeroType, HeroSlots, RarityType
from app.game.buildings.building_services import GameBuildingService
from app.admin.decorators import admin_required
from app.admin import bp
from sqlalchemy.exc import SQLAlchemyError          # type:ignore


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
                           title='Admin - Users', 
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

    return render_template("admin/admin_roles.html", 
                           title='Admin - Roles', 
                           roles=roles, 
                           roleform=roleform)

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


        # Assign the user the default role
        assign_user_role = UserRoles(user_id=user_id, role_id=2)

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






## Game Admin Routes
# This route is used to render the admin page for the game users
@bp.route('/admin_models', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_models():

    games = db.session.query(Game).all()

    return render_template("admin/game/admin_models.html", 
                           title='Admin - All Games', 
                           games=games)


# This route is used to render the admin page for the game xp log
@bp.route('/admin_resourceslog', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_resourceslog():

    resourcelogs = db.session.query(ResourceLog).all()


    return render_template("admin/game/admin_resourceslog.html", 
                           title='Admin Resource Log', 
                           resourcelogs=resourcelogs)

# This route is used to render the admin page for level requirements
@bp.route('/admin_levelrequirements', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_levelrequirements():

    return render_template("admin/game/admin_levelrequirements.html", 
                           title='Admin - Level Requirements')


# This route is used to render the admin page for the game main quests
@bp.route('/admin_mainquests', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_mainquests():

    # Queries
    questtypes = db.session.query(QuestType).all()
    quests = db.session.query(Quest).all()
    questrewards  = db.session.query(QuestRewards).all()
    questprogresses = db.session.query(QuestProgress).all()
    quest_prerequisites = db.session.query(QuestPrerequisites).all()
    quest_requirements = db.session.query(QuestRequirements).all()
    quest_prerequisite_progress = db.session.query(QuestPreRequisitesProgress).all()
    quest_requirement_progress = db.session.query(QuestRequirementProgress).all()
        

    return render_template("admin/game/admin_mainquests.html", 
                           title='Admin - Quests',
                           quests=quests,
                           questtypes=questtypes,
                           questrewards=questrewards,
                           questprogresses=questprogresses,
                           quest_prerequisites=quest_prerequisites,
                           quest_requirements=quest_requirements,
                           quest_prerequisite_progress=quest_prerequisite_progress,
                           quest_requirement_progress=quest_requirement_progress)


# This route is used to render the admin page for the game buildings
@bp.route('/admin_buildings', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_buildings():
    
    try:
        # Queries
        games = db.session.query(Game).all()
        buildingtypes = db.session.query(BuildingType).all()
        buildings = db.session.query(Buildings).all()
        buildingprogress = db.session.query(BuildingProgress).all()
                
        # Calculate Accrued Resources

        for building in buildingprogress:
            service = GameBuildingService(building_progress_id=building.id)
            service.calculate_accrued_resources()

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}") 
        

    return render_template("admin/game/admin_buildings.html", 
                        title='Admin - Buildings', 
                        games=games,
                        buildingtypes=buildingtypes,
                        buildings=buildings,
                        buildingprogress=buildingprogress)


# This route is used to render the admin page for the game items
@bp.route('/admin_items', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_items():
    
    games = db.session.query(Game).all()
    items = db.session.query(Item).all()
    
    
    return render_template("admin/game/admin_items.html", 
                           title='Admin - Items',
                           games=games,
                           items=items)

# This route is used to render the admin page for the game inventories

@bp.route('/admin_inventories', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_inventories():
    
    games = db.session.query(Game).all()
    inventorytypes = db.session.query(InventoryType).all()
    inventories = db.session.query(Inventory).all()
    game_inventories = db.session.query(InventoryUser).all()
    inventoryitems = db.session.query(InventoryItems).all()
    
    
    return render_template("admin/game/admin_inventories.html", 
                           title='Admin - Inventories',
                           games=games,
                           inventorytypes=inventorytypes,
                           inventories=inventories,
                           game_inventories=game_inventories,
                           inventoryitems=inventoryitems)


# This route is used to render the admin page for the game heroes

@bp.route('/admin_heroes', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_heroes():
    
    games = db.session.query(Game).all()
    herotypes = db.session.query(HeroType).all()
    heroes = db.session.query(Hero).all()
    heroprogresses = db.session.query(HeroProgress).all()
    heroslots = db.session.query(HeroSlots).all()
    raritytypes = db.session.query(RarityType).all()
    
    
    return render_template("admin/game/admin_heroes.html", 
                           title='Admin - Heroes',
                           games=games,
                           herotypes=herotypes,
                           heroes=heroes,
                           heroprogresses=heroprogresses,
                           heroslots=heroslots,
                           raritytypes=raritytypes)
