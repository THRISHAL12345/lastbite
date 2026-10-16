"""Add LastBite listings and reservations; preserve the legacy ticket tables."""
from alembic import op
import sqlalchemy as sa

revision = "0002_lastbite"
down_revision = "0001_tickets"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("listings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(160), nullable=False),
        sa.Column("restaurant", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(20), nullable=False),
        sa.Column("dietary", sa.String(20), nullable=False),
        sa.Column("allergens", sa.String(300), nullable=False),
        sa.Column("address", sa.String(240), nullable=False),
        sa.Column("price_paise", sa.Integer(), nullable=False),
        sa.Column("original_price_paise", sa.Integer(), nullable=False),
        sa.Column("quantity_total", sa.Integer(), nullable=False),
        sa.Column("quantity_available", sa.Integer(), nullable=False),
        sa.Column("pickup_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("pickup_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("quantity_total > 0 AND quantity_available >= 0 AND quantity_available <= quantity_total", name="listing_inventory"),
        sa.CheckConstraint("price_paise > 0 AND original_price_paise >= price_paise", name="listing_prices"),
        sa.CheckConstraint("pickup_end > pickup_start", name="listing_pickup_window"),
        sa.CheckConstraint("status IN ('ACTIVE','PAUSED')", name="listing_status"),
    )
    op.create_index("ix_listings_pickup_end", "listings", ["pickup_end"])
    op.create_table("reservations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("listing_id", sa.Integer(), sa.ForeignKey("listings.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("customer", sa.String(120), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price_paise", sa.Integer(), nullable=False),
        sa.Column("original_unit_price_paise", sa.Integer(), nullable=False),
        sa.Column("pickup_code", sa.String(12), nullable=False, unique=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("picked_up_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("quantity > 0", name="reservation_quantity"),
        sa.CheckConstraint("status IN ('RESERVED','PICKED_UP','CANCELLED')", name="reservation_status"),
    )
    op.create_index("ix_reservations_listing_id", "reservations", ["listing_id"])
    op.create_index("ix_reservations_status", "reservations", ["status"])


def downgrade():
    op.drop_table("reservations")
    op.drop_table("listings")
