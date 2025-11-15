import random
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from app.shared.utils.db import SqlRunner
from app.auth.enums import AccessLevel
from app.auth.models import User
from app.auth import repository as auth_repo
from app.project.models import Project
from app.project import repository as project_repo

from .dto import LoadTestDataResponse, StudentData, InstructorData, ProjectData


def create_load_test_data(*, db: SqlRunner) -> LoadTestDataResponse:
    """
    Create 100 test users (80 students + 20 instructors) and 30 projects.
    Students have Controlled access levels, instructors have Restricted.
    Uses @hmp.test domain and $TEST$ prefix for easy cleanup.
    """
    students: list[StudentData] = []
    instructors: list[InstructorData] = []
    projects: list[ProjectData] = []

    expires_at = (datetime.now() + timedelta(days=365)).isoformat()

    # Create 80 students
    for i in range(80):
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )

        email = f"student{i:03d}@hmp.test"
        user = User(
            name=f"TestStudent{i:03d}",
            surname=f"Load{i:03d}",
            email=email,
            confidentiality_level=AccessLevel.CONTROLLED,
            integrity_levels=[AccessLevel.RESTRICTED],
            public_key=public_key_bytes,
            expires_at=expires_at,
        )

        user_id = auth_repo.create_user(user, db=db)

        students.append(
            StudentData(
                id=user_id,
                email=email,
                private_key=private_key_bytes.hex(),
                project_ids=[],
            )
        )

    # Create 20 instructors
    for i in range(20):
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )

        email = f"instructor{i:03d}@hmp.test"
        user = User(
            name=f"TestInstructor{i:03d}",
            surname=f"Load{i:03d}",
            email=email,
            confidentiality_level=AccessLevel.RESTRICTED,
            integrity_levels=[AccessLevel.RESTRICTED],
            public_key=public_key_bytes,
            expires_at=expires_at,
        )

        user_id = auth_repo.create_user(user, db=db)

        instructors.append(
            InstructorData(
                id=user_id,
                email=email,
                private_key=private_key_bytes.hex(),
                project_ids=[],
            )
        )

    # Create 30 projects with $TEST$ prefix
    project_deadline = (datetime.now() + timedelta(days=90)).isoformat()

    for i in range(30):
        instructor = instructors[i % len(instructors)]

        project = Project(
            title=f"$TEST$ Load Test Project {i:03d}",
            syllabus_summary=f"Test project {i:03d} for load testing",
            description=f"This is a load test project created for performance testing. Project number: {i:03d}",
            instructor_id=instructor.id,
            deadline=project_deadline,
        )

        project_id = project_repo.create_project(project, db=db)

        projects.append(
            ProjectData(id=project_id, title=project.title, instructor_id=instructor.id)
        )

        instructor.project_ids.append(project_id)

    # Assign students to projects (each student to 3-5 random projects)
    for student in students:
        num_projects = random.randint(3, 5)
        selected_projects = random.sample(projects, num_projects)

        student_project_ids = [p.id for p in selected_projects]

        # Assign student to each selected project
        for selected_project in selected_projects:
            project_repo.assign_students_to_project(
                selected_project.id, [student.id], db=db
            )

        student.project_ids = student_project_ids

    return LoadTestDataResponse(
        students=students, instructors=instructors, projects=projects
    )


def cleanup_load_test_data(*, db: SqlRunner) -> None:
    """
    Delete all test data created by create_load_test_data.
    Removes users with @hmp.test domain and projects with $TEST$ prefix.
    """
    # Delete submissions for test projects (must be first due to FK constraints)
    db.query("""
        DELETE FROM submissions
        WHERE project_student_id IN (
            SELECT ps.id FROM project_students ps
            WHERE ps.project_id IN (
                SELECT id FROM projects WHERE title LIKE '$TEST$%'
            )
        )
    """).execute()

    # Delete submissions from test users
    db.query("""
        DELETE FROM submissions
        WHERE project_student_id IN (
            SELECT ps.id FROM project_students ps
            JOIN users u ON ps.student_id = u.id
            WHERE u.email LIKE '%@hmp.test'
        )
    """).execute()

    # Delete project_students assignments for test projects
    db.query("""
        DELETE FROM project_students
        WHERE project_id IN (
            SELECT id FROM projects WHERE title LIKE '$TEST$%'
        )
    """).execute()

    # Delete test projects
    db.query("""
        DELETE FROM projects WHERE title LIKE '$TEST$%'
    """).execute()

    # Delete test users (FK will SET NULL on action_logs.user_id)
    db.query("""
        DELETE FROM users WHERE email LIKE '%@hmp.test'
    """).execute()
