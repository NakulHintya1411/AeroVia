"""initial schema: organizations, users, memberships, scenarios, usage

Revision ID: 0001
Revises: 
Create Date: 2026-11-19 01:13:31.584552
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('organizations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('plan', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('failed_login_count', sa.Integer(), nullable=False),
    sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)

    op.create_table('memberships',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('org_id', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'org_id', name='uq_membership_user_org')
    )
    with op.batch_alter_table('memberships', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_memberships_org_id'), ['org_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_memberships_user_id'), ['user_id'], unique=False)

    op.create_table('scenarios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('org_id', sa.Integer(), nullable=False),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('inputs', sa.JSON(), nullable=False),
    sa.Column('economics', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('org_id', 'name', name='uq_scenario_org_name')
    )
    with op.batch_alter_table('scenarios', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_scenarios_org_id'), ['org_id'], unique=False)

    op.create_table('usage_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('org_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('kind', sa.String(length=40), nullable=False),
    sa.Column('model', sa.String(length=80), nullable=True),
    sa.Column('input_tokens', sa.Integer(), nullable=False),
    sa.Column('output_tokens', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('usage_events', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_usage_events_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_usage_events_org_id'), ['org_id'], unique=False)



def downgrade() -> None:
    with op.batch_alter_table('usage_events', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_usage_events_org_id'))
        batch_op.drop_index(batch_op.f('ix_usage_events_created_at'))

    op.drop_table('usage_events')
    with op.batch_alter_table('scenarios', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_scenarios_org_id'))

    op.drop_table('scenarios')
    with op.batch_alter_table('memberships', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_memberships_user_id'))
        batch_op.drop_index(batch_op.f('ix_memberships_org_id'))

    op.drop_table('memberships')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')
    op.drop_table('organizations')
