"""add NAND evaluation extension tables

Revision ID: 6f2a9c8d1e7b
Revises: c8d9e0f1a2b3
Create Date: 2026-07-03 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6f2a9c8d1e7b"
down_revision = "c8d9e0f1a2b3"
branch_labels = None
depends_on = None


NAND_PRODUCTS = (
    ("V3", "DW"),
    ("V3", "DX"),
    ("V3", "DA"),
    ("V4", "FB"),
    ("V4", "FP"),
    ("V4", "FY"),
    ("V5", "IX"),
    ("V5", "IT"),
    ("V5", "IL"),
    ("V6", "BF"),
    ("V6", "BU"),
    ("V6P", "BH"),
    ("V7", "GQ"),
    ("V7", "GJ"),
    ("V8", "CR"),
    ("V8", "CU"),
)


NAND_TABLES = {
    "nand_products",
    "nand_applied_products",
    "nand_grades",
    "nand_evaluations",
    "nand_evaluation_applied_products",
    "nand_evaluation_grades",
    "nand_timeline_relations",
}


def _seed_nand_products() -> None:
    bind = op.get_bind()
    existing_rows = bind.execute(
        sa.text("SELECT dr_generation, product_code FROM nand_products")
    )
    existing_products = {(row.dr_generation, row.product_code) for row in existing_rows}

    missing_products = [
        {
            "dr_generation": dr_generation,
            "product_code": product_code,
            "display_order": index,
            "is_active": True,
        }
        for index, (dr_generation, product_code) in enumerate(NAND_PRODUCTS, start=1)
        if (dr_generation, product_code) not in existing_products
    ]
    if not missing_products:
        return

    nand_products_table = sa.table(
        "nand_products",
        sa.column("dr_generation", sa.String()),
        sa.column("product_code", sa.String()),
        sa.column("display_order", sa.Integer()),
        sa.column("is_active", sa.Boolean()),
    )
    op.bulk_insert(nand_products_table, missing_products)


def upgrade() -> None:
    existing_tables = set(sa.inspect(op.get_bind()).get_table_names())
    if NAND_TABLES.issubset(existing_tables):
        _seed_nand_products()
        return

    op.create_table(
        "nand_products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dr_generation", sa.String(length=20), nullable=False),
        sa.Column("product_code", sa.String(length=20), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "dr_generation",
            "product_code",
            name="uq_nand_product_dr_product",
        ),
    )
    op.create_index(
        "ix_nand_products_dr_generation", "nand_products", ["dr_generation"]
    )
    op.create_index("ix_nand_products_product_code", "nand_products", ["product_code"])

    _seed_nand_products()

    op.create_table(
        "nand_applied_products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("model_name"),
    )
    op.create_index(
        "ix_nand_applied_products_model_name",
        "nand_applied_products",
        ["model_name"],
    )

    op.create_table(
        "nand_grades",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("grade_code", sa.String(length=50), nullable=False),
        sa.Column("grade_family", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("grade_code"),
    )
    op.create_index("ix_nand_grades_grade_code", "nand_grades", ["grade_code"])

    op.create_table(
        "nand_evaluations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("evaluation_id", sa.Integer(), nullable=False),
        sa.Column("nand_product_id", sa.Integer(), nullable=False),
        sa.Column("milestone_date", sa.Date(), nullable=False),
        sa.Column(
            "milestone_status",
            sa.Enum(
                "approved",
                "current_month_plan",
                "follow_up_plan",
                name="nand_milestone_status",
            ),
            nullable=False,
        ),
        sa.Column("evaluation_item", sa.String(length=100), nullable=False),
        sa.Column("fab_line", sa.String(length=50), nullable=False),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("remark_top", sa.Text(), nullable=True),
        sa.Column("remark_bottom", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["evaluation_id"],
            ["evaluations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["nand_product_id"], ["nand_products.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("evaluation_id"),
    )
    op.create_index(
        "ix_nand_evaluations_evaluation_id", "nand_evaluations", ["evaluation_id"]
    )
    op.create_index(
        "ix_nand_evaluations_nand_product_id",
        "nand_evaluations",
        ["nand_product_id"],
    )
    op.create_index(
        "ix_nand_evaluations_milestone_date", "nand_evaluations", ["milestone_date"]
    )

    op.create_table(
        "nand_evaluation_applied_products",
        sa.Column("nand_evaluation_id", sa.Integer(), nullable=False),
        sa.Column("applied_product_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["nand_evaluation_id"],
            ["nand_evaluations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["applied_product_id"],
            ["nand_applied_products.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("nand_evaluation_id", "applied_product_id"),
    )

    op.create_table(
        "nand_evaluation_grades",
        sa.Column("nand_evaluation_id", sa.Integer(), nullable=False),
        sa.Column("grade_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["nand_evaluation_id"],
            ["nand_evaluations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["grade_id"], ["nand_grades.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("nand_evaluation_id", "grade_id"),
    )

    op.create_table(
        "nand_timeline_relations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("from_nand_evaluation_id", sa.Integer(), nullable=False),
        sa.Column("to_nand_evaluation_id", sa.Integer(), nullable=False),
        sa.Column("relation_type", sa.String(length=50), nullable=False),
        sa.Column("label", sa.String(length=100), nullable=True),
        sa.Column("color", sa.String(length=20), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["from_nand_evaluation_id"],
            ["nand_evaluations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["to_nand_evaluation_id"],
            ["nand_evaluations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_nand_timeline_relations_from",
        "nand_timeline_relations",
        ["from_nand_evaluation_id"],
    )
    op.create_index(
        "ix_nand_timeline_relations_to",
        "nand_timeline_relations",
        ["to_nand_evaluation_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_nand_timeline_relations_to", table_name="nand_timeline_relations")
    op.drop_index(
        "ix_nand_timeline_relations_from", table_name="nand_timeline_relations"
    )
    op.drop_table("nand_timeline_relations")
    op.drop_table("nand_evaluation_grades")
    op.drop_table("nand_evaluation_applied_products")
    op.drop_index("ix_nand_evaluations_milestone_date", table_name="nand_evaluations")
    op.drop_index("ix_nand_evaluations_nand_product_id", table_name="nand_evaluations")
    op.drop_index("ix_nand_evaluations_evaluation_id", table_name="nand_evaluations")
    op.drop_table("nand_evaluations")
    op.drop_index("ix_nand_grades_grade_code", table_name="nand_grades")
    op.drop_table("nand_grades")
    op.drop_index(
        "ix_nand_applied_products_model_name",
        table_name="nand_applied_products",
    )
    op.drop_table("nand_applied_products")
    op.drop_index("ix_nand_products_product_code", table_name="nand_products")
    op.drop_index("ix_nand_products_dr_generation", table_name="nand_products")
    op.drop_table("nand_products")
