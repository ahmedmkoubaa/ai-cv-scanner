from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    full_name: str
    email: str
    phone: str
    location: str
    linkedin: str | None = None


class WorkExperience(BaseModel):
    title: str
    company: str
    location: str
    start_date: str
    end_date: str | None = None
    description: list[str] = Field(min_length=1)


class Education(BaseModel):
    degree: str
    institution: str
    location: str
    graduation_year: str


class CVProfile(BaseModel):
    contact: ContactInfo
    summary: str
    work_experience: list[WorkExperience] = Field(min_length=1)
    education: list[Education] = Field(min_length=1)
    skills: list[str] = Field(min_length=3)
