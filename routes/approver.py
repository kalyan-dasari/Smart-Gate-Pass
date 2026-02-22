from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from models import db, GatePass, Role

approver_bp = Blueprint('approver', __name__, url_prefix='/approver')

@approver_bp.route('/pending')
@login_required
def pending():
    if current_user.role == Role.INCHARGE:
        passes = GatePass.query.filter_by(status='pending_incharge').order_by(GatePass.date_requested.desc()).all()
    elif current_user.role == Role.HOD:
        passes = GatePass.query.filter_by(status='pending_hod').order_by(GatePass.date_requested.desc()).all()
    else:
        passes = []
    return render_template('approver_list.html', passes=passes)

@approver_bp.route('/view/<int:pass_id>')
@login_required
def view_pass(pass_id):
    gp = GatePass.query.get_or_404(pass_id)
    return render_template('approver_view.html', gp=gp)

@approver_bp.route('/decide/<int:pass_id>', methods=['POST'])
@login_required
def decide(pass_id):
    gp = GatePass.query.get_or_404(pass_id)
    action = request.form.get('action')
    remarks = request.form.get('remarks', '').strip()
    if current_user.role == Role.INCHARGE:
        if action == 'approve':
            gp.status = 'pending_hod'
            gp.incharge_remarks = remarks
        else:
            gp.status = 'rejected'
            gp.incharge_remarks = remarks
    elif current_user.role == Role.HOD:
        if action == 'approve':
            gp.status = 'approved'
            gp.hod_remarks = remarks
        else:
            gp.status = 'rejected'
            gp.hod_remarks = remarks
    else:
        flash('Unauthorized', 'danger')
        return redirect(url_for('approver.pending'))
    db.session.commit()
    flash('Decision recorded', 'success')
    return redirect(url_for('approver.pending'))
