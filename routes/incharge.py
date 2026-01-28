from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, GatePass, Role
from utils.notify import send_email, send_sms

incharge_bp = Blueprint('incharge', __name__, url_prefix='/incharge')

@incharge_bp.before_request
def check_role():
    if not current_user.is_authenticated or current_user.role != Role.INCHARGE:
        return "Unauthorized", 403

@incharge_bp.route('/dashboard')
@login_required
def dashboard():
    passes = GatePass.query.filter_by(status='pending_incharge').order_by(GatePass.date_requested.desc()).all()
    return render_template('incharge_dashboard.html', passes=passes)

@incharge_bp.route('/view/<int:pass_id>')
@login_required
def view_request(pass_id):
    gp = GatePass.query.get_or_404(pass_id)
    return render_template('incharge_view.html', gp=gp)

@incharge_bp.route('/decide/<int:pass_id>', methods=['POST'])
@login_required
def decide(pass_id):
    gp = GatePass.query.get_or_404(pass_id)
    action = request.form.get('action')
    remarks = request.form.get('remarks')

    if action == 'approve':
        gp.status = 'pending_hod'
        gp.incharge_remarks = remarks

        db.session.commit()   # ✅ Commit before sending notifications

        # ✅ Send notifications
        send_email(
            "Gate Pass Forwarded to HOD ✅",
            gp.student.email,
            f"Your Gate Pass #{gp.id} has been approved by the Incharge and sent to HOD for final approval."
        )

        # If student.phone is stored:
        if gp.student.phone:
            send_sms(
                gp.student.phone,
                f"Incharge approved your Gate Pass #{gp.id}. Sent to HOD."
            )

        flash("Forwarded to HOD ✅", "success")

    else:
        gp.status = 'rejected'
        gp.incharge_remarks = remarks
        db.session.commit()

        send_email(
            "Gate Pass Rejected ❌",
            gp.student.email,
            f"Your Gate Pass #{gp.id} has been rejected by the Incharge. Reason: {remarks}"
        )

        if gp.student.phone:
            send_sms(
                gp.student.phone,
                f"Your Gate Pass #{gp.id} was rejected by the Incharge."
            )

        flash("Request Rejected ❌", "danger")

    return redirect(url_for('incharge.dashboard'))



@incharge_bp.route('/logs')
@login_required
def logs():
    passes = GatePass.query.filter(GatePass.exit_time != None).order_by(GatePass.exit_time.desc()).all()
    return render_template("logs_view.html", passes=passes)
