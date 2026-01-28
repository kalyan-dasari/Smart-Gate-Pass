from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, GatePass, Role
from utils.qr_utils import generate_qr_for_pass
from utils.notify import send_email, send_sms



hod_bp = Blueprint('hod', __name__, url_prefix='/hod')

@hod_bp.before_request
def check_role():
    if not current_user.is_authenticated or current_user.role != Role.HOD:
        return "Unauthorized", 403

@hod_bp.route('/dashboard')
@login_required
def dashboard():
    passes = GatePass.query.filter_by(status='pending_hod').order_by(GatePass.date_requested.desc()).all()
    return render_template('hod_dashboard.html', passes=passes)

@hod_bp.route('/view/<int:pass_id>')
@login_required
def view_request(pass_id):
    gp = GatePass.query.get_or_404(pass_id)
    return render_template('hod_view.html', gp=gp)

@hod_bp.route('/decide/<int:pass_id>', methods=['POST'])
@login_required
def decide(pass_id):
    gp = GatePass.query.get_or_404(pass_id)
    action = request.form.get('action')
    remarks = request.form.get('remarks')

    if action == 'approve':
        gp.status = 'approved'
        gp.hod_remarks = remarks
        
        # generate QR
        filename = generate_qr_for_pass(gp.id)
        gp.qr_code_filename = filename
        
        db.session.commit()

        # send email & SMS
        send_email(
            "Gate Pass Approved ✅",
            gp.student.email,
            f"Your gate pass #{gp.id} has been approved.\n\nYou can download your QR from dashboard."
            )

        if gp.student.phone:
            # send SMS to student only
            send_sms(
                gp.student.phone,
                f"✅ Gate Pass Approved!\nPass ID: {gp.id}\nYou may leave the campus."
            )



        flash("Approved & QR sent ✅", "success")

    else:
        gp.status = 'rejected'
        gp.hod_remarks = remarks
        db.session.commit()
        flash("Request Rejected ❌", "danger")

    return redirect(url_for('hod.dashboard'))


@hod_bp.route('/logs')
@login_required
def logs():
    passes = GatePass.query.filter(GatePass.exit_time != None).order_by(GatePass.exit_time.desc()).all()
    return render_template("logs_view.html", passes=passes)
