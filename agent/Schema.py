from pydantic import BaseModel, Field
from typing import Literal

class Files(BaseModel):
    filename: str = Field(
        description="The name of the file that is to be planned"
    )
    purpose: str = Field(
        description="The purpose of the file that is to be planned"
    )

class AppPlanner(BaseModel):
    appname: str = Field(
        description="The name of the app to be designed",
    )
    description: str = Field(
        description="The description of the app to be designed",
    )
    tech_stack: list[str] = Field(
        description="The technical stack of the app to be designed like html, css, js, py, etc",
    )
    features: list[str] = Field(
        description="The features of the app to be designed",
    )
    files: list[Files] = Field(
        description="The list of files that are to be planned",
    )

class ArchitectureInstruction(BaseModel):
    filename: str = Field(
        description="The name of the file for which architecture instructions should be generated",
    )
    filepath: str = Field(
        description="The path of the file that should be generated",
    )
    instructions: list[str] = Field(
        description="The list of architecture instructions to be executed while coding",
    )

class AppArchitecture(BaseModel):
    architecture_files: list[ArchitectureInstruction] = Field(
        description="The architecture instruction of the app to be followed",
    )

class CodeFile(BaseModel):
    filename: str = Field(
        description="The name of the file to be coded",
    )
    filepath: str = Field(
        description="The path of the file that should be coded",
    )
    content: str = Field(
        description="The actual code lies inside this file",
    )
    extension: str = Field(
        description="The extension of the file to be coded, ex: py, html, js, css, etc",
    )

class AppCoder(BaseModel):
    code_files: list[CodeFile] = Field(
        description="The list of code files that need to be generated for this app",
    )

class AppState(dict):
    user_input: str
    plan: AppPlanner
    architecture: AppArchitecture
    code: AppCoder
    status: Literal["STARTED", "PLANNED", "PLAN_APPROVED","PLAN_REJECTED","ARCHITECTED", "CODING", "REVIEWING", "FIXING", "DONE"]
    coding_iteration: int
    hitl_feedback: str
