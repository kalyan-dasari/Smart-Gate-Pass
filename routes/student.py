from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, GatePass
from flask import send_from_directory
import os

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@login_required
def dashboard():
    # Student sees only their gate passes
    passes = GatePass.query.filter_by(student_id=current_user.id).order_by(GatePass.id.desc()).all()
    return render_template('student_dashboard.html', passes=passes)

@student_bp.route('/request', methods=['GET','POST'])
@login_required
def request_pass():
    if request.method == 'POST':
        reason = request.form['reason']
        from_time = request.form['from_time']
        to_time = request.form['to_time']
        parent_contact = request.form['parent_contact']

        gp = GatePass(
            student_id=current_user.id, 
            reason=reason,
            from_time=from_time,
            to_time=to_time,
            parent_contact=parent_contact,
            status='pending_incharge'
        )

        db.session.add(gp)
        db.session.commit()
        flash("Gate pass request submitted to Class In-Charge ✅", "success")
        return redirect(url_for('student.dashboard'))

    return render_template('student_request.html')


@student_bp.route('/qr/<int:pass_id>')
@login_required
def serve_qr(pass_id):
    gp = db.session.get(GatePass, pass_id)
    if not gp:
        return "Not found", 404

    if gp.student_id != current_user.id:
        return "Unauthorized", 403

    if not gp.qr_code_filename:
        flash("QR not generated yet", "danger")
        return redirect(url_for('student.dashboard'))

    # Ensure correct path handling
    qr_path = gp.qr_code_filename.replace("\\", "/")

    if "/" in qr_path:
        directory, filename = qr_path.rsplit("/", 1)
    else:
        directory = "static/qr"
        filename = qr_path

    return send_from_directory(directory, filename, as_attachment=True)