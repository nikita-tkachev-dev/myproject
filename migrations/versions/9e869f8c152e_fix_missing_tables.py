"""fix missing tables

Revision ID: 9e869f8c152e
Revises: d35a6a4c8646
Create Date: 2025-11-19 09:16:27.886760

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9e869f8c152e"
down_revision = "d35a6a4c8646"
branch_labels = None
depends_on = None


def upgrade():
    from sqlalchemy.dialects import postgresql

    # ===== FIX ENUM TYPES (create only if missing) =====
    conn = op.get_bind()

    # muscle_groups
    mg_enum = postgresql.ENUM(
        "chest",
        "back",
        "shoulders",
        "arms",
        "legs",
        "core",
        "cardio",
        name="muscle_groups",
    )
    mg_enum.create(conn, checkfirst=True)

    # equipment_types
    eq_enum = postgresql.ENUM(
        "bodyweight",
        "dumbbell",
        "barbell",
        "machine",
        "resistance_band",
        "kettlebell",
        name="equipment_types",
    )
    eq_enum.create(conn, checkfirst=True)

    # difficulty_levels
    diff_enum = postgresql.ENUM(
        "beginner", "intermediate", "advanced", name="difficulty_levels"
    )
    diff_enum.create(conn, checkfirst=True)

    # template_levels
    lvl_enum = postgresql.ENUM(
        "beginner", "intermediate", "advanced", name="template_levels"
    )
    lvl_enum.create(conn, checkfirst=True)

    # template_muscle_groups
    tmpl_mg_enum = postgresql.ENUM(
        "legs",
        "back",
        "chest",
        "core",
        "calves",
        "arms",
        "shoulders",
        name="template_muscle_groups",
    )
    tmpl_mg_enum.create(conn, checkfirst=True)

    op.execute("DROP TYPE IF EXISTS muscle_groups CASCADE;")
    op.execute("DROP TYPE IF EXISTS template_muscle_groups CASCADE;")
    op.execute("DROP TYPE IF EXISTS equipment_types CASCADE;")
    op.execute("DROP TYPE IF EXISTS difficulty_levels CASCADE;")

    # ===== TABLE CREATION =====
    op.create_table(
        "exercises",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("muscle_group", mg_enum, nullable=False),
        sa.Column("equipment", eq_enum, nullable=True),
        sa.Column("difficulty", diff_enum, nullable=False),
        sa.Column("video_url", sa.String(length=500), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("exercises", schema=None) as batch_op:
        batch_op.create_index("ix_exercises_name", ["name"], unique=True)

    op.create_table(
        "workout_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("level", lvl_enum, nullable=False),
        sa.Column("day_number", sa.Integer(), nullable=False),
        sa.Column("is_optional", sa.Boolean(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "template_exercises",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("template_id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("muscle_group", tmpl_mg_enum, nullable=False),
        sa.Column("exercise_number", sa.Integer(), nullable=False),
        sa.Column("order_in_workout", sa.Integer(), nullable=False),
        sa.Column("target_sets", sa.Integer(), nullable=False),
        sa.Column("target_reps_min", sa.Integer(), nullable=False),
        sa.Column("target_reps_max", sa.Integer(), nullable=False),
        sa.Column("warmup_sets", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"]),
        sa.ForeignKeyConstraint(["template_id"], ["workout_templates.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "workout_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("workout_plan_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=True),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["workout_plan_id"], ["workout_plans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("workout_sessions", schema=None) as batch_op:
        batch_op.create_index("idx_workout_session_user_date", ["user_id", "date"])

    op.create_table(
        "workout_exercises",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workout_session_id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("order_in_workout", sa.Integer(), nullable=False),
        sa.Column("target_sets", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"]),
        sa.ForeignKeyConstraint(["workout_session_id"], ["workout_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("workout_exercises", schema=None) as batch_op:
        batch_op.create_index("idx_workout_exercise_session", ["workout_session_id"])

    op.create_table(
        "exercise_sets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workout_exercise_id", sa.Integer(), nullable=False),
        sa.Column("set_number", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("reps", sa.Integer(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("distance_meters", sa.Float(), nullable=True),
        sa.Column("rest_seconds", sa.Integer(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False),
        sa.Column("rpe", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_warmup", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["workout_exercise_id"], ["workout_exercises.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("exercise_sets", schema=None) as batch_op:
        batch_op.create_index(
            "idx_exercise_set_workout_exercise", ["workout_exercise_id"]
        )

    # Add missing foreign keys
    with op.batch_alter_table("exercise_logs", schema=None) as batch_op:
        batch_op.create_foreign_key(None, "exercises", ["exercise_id"], ["id"])

    with op.batch_alter_table("exercise_statistics", schema=None) as batch_op:
        batch_op.create_foreign_key(None, "exercises", ["exercise_id"], ["id"])

    with op.batch_alter_table("workout_plan_exercises", schema=None) as batch_op:
        batch_op.create_foreign_key(None, "exercises", ["exercise_id"], ["id"])


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("workout_plan_exercises", schema=None) as batch_op:
        batch_op.drop_constraint(None, type_="foreignkey")

    with op.batch_alter_table("exercise_statistics", schema=None) as batch_op:
        batch_op.drop_constraint(None, type_="foreignkey")

    with op.batch_alter_table("exercise_logs", schema=None) as batch_op:
        batch_op.drop_constraint(None, type_="foreignkey")

    with op.batch_alter_table("exercise_sets", schema=None) as batch_op:
        batch_op.drop_index("idx_exercise_set_workout_exercise")

    op.drop_table("exercise_sets")
    with op.batch_alter_table("workout_exercises", schema=None) as batch_op:
        batch_op.drop_index("idx_workout_exercise_session")

    op.drop_table("workout_exercises")
    with op.batch_alter_table("workout_sessions", schema=None) as batch_op:
        batch_op.drop_index("idx_workout_session_user_date")

    op.drop_table("workout_sessions")
    op.drop_table("template_exercises")
    op.drop_table("workout_templates")
    with op.batch_alter_table("exercises", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_exercises_name"))

    op.drop_table("exercises")
    # ### end Alembic commands ###
