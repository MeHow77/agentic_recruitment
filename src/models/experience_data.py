from pydantic import BaseModel


class ExperienceEntry(BaseModel):
    title: str
    company: str
    date: str
    bullets: list[str]


class EducationEntry(BaseModel):
    degree: str
    date: str
    school: str
    location: str


class Skills(BaseModel):
    languages: list[str]
    tools: list[str]
    spoken: list[str]


class AwardEntry(BaseModel):
    title: str
    award: str
    year: str | int


class PublicationEntry(BaseModel):
    id: str
    title: str
    authors: str
    conference: str


class ExperienceData(BaseModel):
    summary: str
    experience: list[ExperienceEntry]
    education: list[EducationEntry]
    skills: Skills
    awards: list[AwardEntry] = []
    publications: list[PublicationEntry] = []
