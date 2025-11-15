from pydantic import BaseModel


class LoadTestDataResponse(BaseModel):
    students: list["StudentData"]
    instructors: list["InstructorData"]
    projects: list["ProjectData"]


class StudentData(BaseModel):
    id: int
    email: str
    private_key: str
    project_ids: list[int]


class InstructorData(BaseModel):
    id: int
    email: str
    private_key: str
    project_ids: list[int]


class ProjectData(BaseModel):
    id: int
    title: str
    instructor_id: int
