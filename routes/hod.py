from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, GatePass, Role, User
from utils.qr_utils import generate_qr_for_pass
from utils.notify import send_email, send_sms
from datetime import date



hod_bp = Blueprint('hod', __name__, url_prefix='/hod')

@hod_bp.before_request
def check_role():
    if not current_user.is_authenticated or current_user.role != Role.HOD:
        return "Unauthorized", 403

@hod_bp.route('/dashboard')
@login_required
def dashboard():
    passes = GatePass.query.filter_by(status='pending_hod').order_by(GatePass.date_requested.desc()).all()
    all_passes = GatePass.query.all()

    today = date.today()
    total_exits_today = sum(1 for gp in all_passes if gp.exit_time and gp.exit_time.date() == today)
    monthly_exit_count = sum(
        1 for gp in all_passes if gp.exit_time and gp.exit_time.year == today.year and gp.exit_time.month == today.month
    )

    section_map = {}
    for gp in all_passes:
        section = gp.student.department if gp.student and gp.student.department else 'Unknown'
        section_map[section] = section_map.get(section, 0) + 1
    section_distribution = [{"section": key, "count": value} for key, value in section_map.items()]

    decided = [gp for gp in all_passes if gp.status in ('approved', 'rejected')]
    approved = [gp for gp in decided if gp.status == 'approved']
    approval_rate = round((len(approved) / len(decided)) * 100, 1) if decided else 0

    per_student = {}
    for gp in all_passes:
        name = gp.student.name if gp.student else 'Unknown'
        per_student[name] = per_student.get(name, 0) + 1
    high_risk_students_rows = sorted(per_student.items(), key=lambda item: item[1], reverse=True)[:5]

    unusual_section = None
    if section_distribution:
        peak = max(section_distribution, key=lambda item: item['count'])
        unusual_section = f"{peak['section']} has highest exits ({peak['count']})"

    odd_time_count = 0
    for gp in all_passes:
        if gp.exit_time and (gp.exit_time.hour < 8 or gp.exit_time.hour > 18):
            odd_time_count += 1

    incharge_users = User.query.filter_by(role=Role.INCHARGE).all()
    lenient_alerts = []
    strict_alerts = []
    for user in incharge_users:
        reviewed = GatePass.query.filter(GatePass.incharge_remarks.isnot(None), GatePass.student.has(department=user.department)).all()
        if not reviewed:
            continue
        approved_count = sum(1 for gp in reviewed if gp.status in ('pending_hod', 'approved'))
        rejected_count = sum(1 for gp in reviewed if gp.status == 'rejected')
        total = approved_count + rejected_count
        if total >= 5:
            rate = (approved_count / total) * 100
            if rate >= 95:
                lenient_alerts.append(f"{user.name}: approval rate {rate:.1f}%")
            if rate <= 20:
                strict_alerts.append(f"{user.name}: approval rate {rate:.1f}%")

    past_scans = GatePass.query.filter(GatePass.exit_time.isnot(None)).order_by(GatePass.exit_time.desc()).limit(15).all()

    return render_template(
        'hod_dashboard.html',
        passes=passes,
        total_exits_today=total_exits_today,
        monthly_exit_count=monthly_exit_count,
        section_distribution=section_distribution,
        approval_rate=approval_rate,
        high_risk_students=high_risk_students_rows,
        unusual_section=unusual_section,
        odd_time_count=odd_time_count,
        lenient_alerts=lenient_alerts,
        strict_alerts=strict_alerts,
        past_scans=past_scans
    )

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
    passes = GatePass.query.filter(GatePass.exit_time.isnot(None)).order_by(GatePass.exit_time.desc()).all()
    return render_template("logs_view.html", passes=passes)
