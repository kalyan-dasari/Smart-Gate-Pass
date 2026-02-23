from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
from models import db, GatePass, Role
from datetime import datetime, timedelta

security_bp = Blueprint('security', __name__, url_prefix='/security')


def _dt_short(value):
    return value.strftime('%Y-%m-%d %H:%M') if value else None

# ✅ BEFORE REQUEST: only scanner page requires login
@security_bp.before_request
def protect_routes():
    # Allow public verify API
    if request.endpoint == "security.verify":
        return None

    # Everything else requires security login
    if not current_user.is_authenticated or current_user.role != Role.SECURITY:
        return "Unauthorized", 403


# ✅ Security Scanner Page (Webcam)
@security_bp.route('/scan')
@login_required
def scan_page():
    return render_template("security_scan.html")


# ✅ Public QR Verification API
last_scan_time = {}  # prevent rapid rescan

@security_bp.route('/verify/<int:pass_id>')
def verify(pass_id):
    gp = db.session.get(GatePass, pass_id)
    if not gp:
        return jsonify({"status": "not_found"})

    # anti rapid scan (0.8 sec gap)
    now = datetime.utcnow()
    if pass_id in last_scan_time and (now - last_scan_time[pass_id]).total_seconds() < 0.8:
        return jsonify({"status": "wait"})

    last_scan_time[pass_id] = now

    if gp.status != "approved":
        return jsonify({"status": "invalid"})

    # ✅ First scan → OUT
    if gp.exit_time is None:
        gp.exit_time = datetime.utcnow()
        db.session.commit()
        return jsonify({
            "status": "exit",
            "student": gp.student.name,
            "time": _dt_short(gp.exit_time)
        })

    # ✅ Second scan → IN (Optional)
    if gp.entry_time is None:
        if (datetime.utcnow() - gp.exit_time) > timedelta(minutes=5):
            gp.entry_time = datetime.utcnow()
            db.session.commit()
            return jsonify({
                "status": "entry",
                "student": gp.student.name,
                "time": _dt_short(gp.entry_time)
            })
        else:
            return jsonify({"status": "skip"})

    return jsonify({"status": "done"})


@security_bp.route('/logs')
@login_required
def logs():
    passes = GatePass.query.filter(GatePass.exit_time.isnot(None)).order_by(GatePass.exit_time.desc()).all()
    return render_template('logs_view.html', passes=passes)
