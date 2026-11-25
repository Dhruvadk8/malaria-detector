import calendar
from datetime import datetime, timedelta
from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required, current_user
from sqlalchemy import func
from backend.models import db, Detection

main = Blueprint('main', __name__)

@main.route('/')
def home():
    """Render the home page."""
    return render_template('home.html')

@main.route('/login')
def login_page():
    """Render the login page."""
    return render_template('login.html')

@main.route('/signup')
def signup_page():
    """Render the signup page."""
    return render_template('signup.html')

@main.route('/phases')
@jwt_required(optional=True)
def phases():
    """Render the dedicated Phases of Malaria guide and visualizer."""
    user_id = current_user.id if (current_user and hasattr(current_user, 'id')) else None
    
    # Get phase counts for display
    ring_count = Detection.query.filter(Detection.parasite_stage.like('%Ring%')).count()
    trophozoite_count = Detection.query.filter(Detection.parasite_stage.like('%Trophozoite%')).count()
    schizont_count = Detection.query.filter(Detection.parasite_stage.like('%Schizont%')).count()
    gametocyte_count = Detection.query.filter(Detection.parasite_stage.like('%Gametocyte%')).count()
    
    return render_template(
        'phases.html',
        current_user=current_user,
        active_page='phases',
        ring_count=ring_count,
        trophozoite_count=trophozoite_count,
        schizont_count=schizont_count,
        gametocyte_count=gametocyte_count
    )

@main.route('/dashboard')
@jwt_required(optional=True)
def dashboard():
    """Render the dashboard page with real detection history and phase metrics."""
    user_id = current_user.id if (current_user and hasattr(current_user, 'id')) else None
    
    if user_id:
        detections = Detection.query.filter_by(user_id=user_id).order_by(Detection.created_at.desc()).limit(15).all()
        total_analyses = Detection.query.filter_by(user_id=user_id).count()
        parasitized_count = Detection.query.filter_by(user_id=user_id, result='Parasitized').count()
        uninfected_count = Detection.query.filter_by(user_id=user_id, result='Uninfected').count()
        ring_count = Detection.query.filter(Detection.user_id == user_id, Detection.parasite_stage.like('%Ring%')).count()
        trophozoite_count = Detection.query.filter(Detection.user_id == user_id, Detection.parasite_stage.like('%Trophozoite%')).count()
        schizont_count = Detection.query.filter(Detection.user_id == user_id, Detection.parasite_stage.like('%Schizont%')).count()
        gametocyte_count = Detection.query.filter(Detection.user_id == user_id, Detection.parasite_stage.like('%Gametocyte%')).count()
    else:
        detections = Detection.query.order_by(Detection.created_at.desc()).limit(15).all()
        total_analyses = Detection.query.count()
        parasitized_count = Detection.query.filter_by(result='Parasitized').count()
        uninfected_count = Detection.query.filter_by(result='Uninfected').count()
        ring_count = Detection.query.filter(Detection.parasite_stage.like('%Ring%')).count()
        trophozoite_count = Detection.query.filter(Detection.parasite_stage.like('%Trophozoite%')).count()
        schizont_count = Detection.query.filter(Detection.parasite_stage.like('%Schizont%')).count()
        gametocyte_count = Detection.query.filter(Detection.parasite_stage.like('%Gametocyte%')).count()

    return render_template(
        'dashboard.html',
        current_user=current_user,
        active_page='dashboard',
        detections=detections,
        total_analyses=total_analyses,
        parasitized_count=parasitized_count,
        uninfected_count=uninfected_count,
        ring_count=ring_count,
        trophozoite_count=trophozoite_count,
        schizont_count=schizont_count,
        gametocyte_count=gametocyte_count
    )

@main.route('/new_analysis')
@jwt_required(optional=True)
def new_analysis():
    """Render the new analysis page."""
    return render_template('new_analysis.html', current_user=current_user, active_page='new_analysis')

@main.route('/analysis_history')
@jwt_required(optional=True)
def analysis_history():
    """Render the analysis history page with complete detection records."""
    user_id = current_user.id if (current_user and hasattr(current_user, 'id')) else None
    
    if user_id:
        detections = Detection.query.filter_by(user_id=user_id).order_by(Detection.created_at.desc()).all()
    else:
        detections = Detection.query.order_by(Detection.created_at.desc()).all()

    return render_template(
        'analysis_history.html',
        current_user=current_user,
        active_page='history',
        detections=detections
    )

@main.route('/statistics')
@jwt_required(optional=True)
def statistics():
    """Render the statistics page with phase breakdown and trends."""
    user_id = current_user.id if (current_user and hasattr(current_user, 'id')) else None
    
    if user_id:
        total_analyses = Detection.query.filter_by(user_id=user_id).count()
        parasitized_count = Detection.query.filter_by(user_id=user_id, result='Parasitized').count()
        uninfected_count = Detection.query.filter_by(user_id=user_id, result='Uninfected').count()
        ring_count = Detection.query.filter(Detection.user_id == user_id, Detection.parasite_stage.like('%Ring%')).count()
        trophozoite_count = Detection.query.filter(Detection.user_id == user_id, Detection.parasite_stage.like('%Trophozoite%')).count()
        schizont_count = Detection.query.filter(Detection.user_id == user_id, Detection.parasite_stage.like('%Schizont%')).count()
        gametocyte_count = Detection.query.filter(Detection.user_id == user_id, Detection.parasite_stage.like('%Gametocyte%')).count()
    else:
        total_analyses = Detection.query.count()
        parasitized_count = Detection.query.filter_by(result='Parasitized').count()
        uninfected_count = Detection.query.filter_by(result='Uninfected').count()
        ring_count = Detection.query.filter(Detection.parasite_stage.like('%Ring%')).count()
        trophozoite_count = Detection.query.filter(Detection.parasite_stage.like('%Trophozoite%')).count()
        schizont_count = Detection.query.filter(Detection.parasite_stage.like('%Schizont%')).count()
        gametocyte_count = Detection.query.filter(Detection.parasite_stage.like('%Gametocyte%')).count()
        
    monthly_stats = []
    today = datetime.utcnow()
    for i in range(11, -1, -1):
        month_date = today - timedelta(days=i*30)
        month_name = calendar.month_abbr[month_date.month]
        
        query = Detection.query.filter(
            func.strftime('%Y-%m', Detection.created_at) == month_date.strftime('%Y-%m')
        )
        if user_id:
            query = query.filter_by(user_id=user_id)
            
        total = query.count()
        parasitized = query.filter_by(result='Parasitized').count()
        uninfected = query.filter_by(result='Uninfected').count()
        
        monthly_stats.append({
            'month': month_name,
            'total': total,
            'parasitized': parasitized,
            'uninfected': uninfected
        })
        
    return render_template(
        'statistics.html',
        current_user=current_user,
        active_page='statistics',
        total_analyses=total_analyses,
        parasitized_count=parasitized_count,
        uninfected_count=uninfected_count,
        ring_count=ring_count,
        trophozoite_count=trophozoite_count,
        schizont_count=schizont_count,
        gametocyte_count=gametocyte_count,
        monthly_stats=monthly_stats
    )

@main.route('/documentation')
@jwt_required(optional=True)
def documentation():
    """Render the documentation page."""
    return render_template('documentation.html', current_user=current_user, active_page='documentation')

@main.route('/settings')
@jwt_required(optional=True)
def settings():
    """Render the settings page."""
    return render_template('settings.html', current_user=current_user, active_page='settings')
