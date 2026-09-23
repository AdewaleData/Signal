"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-09-23
"""

from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("role", sa.String(64), nullable=False),
        sa.Column("reliability_score", sa.Float(), nullable=False),
        sa.Column("reports_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("confirmed_reports", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "routes",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("origin", sa.String(120), nullable=False),
        sa.Column("destination", sa.String(120), nullable=False),
        sa.Column("geometry", sa.Text(), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=False),
        sa.Column("distance_km", sa.Float(), nullable=False),
        sa.Column("alternate_of", sa.String(64), sa.ForeignKey("routes.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "route_segments",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("route_id", sa.String(64), sa.ForeignKey("routes.id"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
    )
    op.create_table(
        "reports",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("user_id", sa.String(64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("incident_type", sa.String(64), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("location_name", sa.String(120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("severity", sa.String(32), nullable=False),
        sa.Column("evidence_quality", sa.Float(), nullable=False),
        sa.Column("is_official", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("raw_text", sa.Text(), nullable=True),
    )
    op.create_table(
        "report_relationships",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("report_id", sa.String(64), sa.ForeignKey("reports.id"), nullable=False),
        sa.Column("related_report_id", sa.String(64), sa.ForeignKey("reports.id"), nullable=False),
        sa.Column("relationship_type", sa.String(32), nullable=False),
        sa.Column("similarity_score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "route_assessments",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("route_id", sa.String(64), sa.ForeignKey("routes.id"), nullable=False),
        sa.Column("state", sa.String(32), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("route_assessments")
    op.drop_table("report_relationships")
    op.drop_table("reports")
    op.drop_table("route_segments")
    op.drop_table("routes")
    op.drop_table("users")
