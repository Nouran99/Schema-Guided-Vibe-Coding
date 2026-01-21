from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
courses = {}
lessons = {}
quizzes = {}
enrollments = {}

# Models
class CourseCreate(BaseModel):
    instructor_id: int
    title: str
    description: str

class LessonCreate(BaseModel):
    title: str
    content_type: str
    content_url: str
    order: int

class QuizCreate(BaseModel):
    title: str
    questions: list
    passing_score: int

class EnrollmentCreate(BaseModel):
    learner_id: int

class ProgressUpdate(BaseModel):
    progress_percent: int

class QuizSubmission(BaseModel):
    answers: dict

# Core endpoints
@app.get("/api/courses")
def list_courses():
    return list(courses.values())

@app.post("/api/courses")
def create_course(course: CourseCreate):
    course_id = str(uuid.uuid4())
    courses[course_id] = {
        "id": course_id,
        "instructor_id": course.instructor_id,
        "title": course.title,
        "description": course.description,
        "created_at": datetime.now().isoformat()
    }
    return courses[course_id]

@app.post("/api/courses/{course_id}/lessons")
def add_lesson(course_id: str, lesson: LessonCreate):
    if course_id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    lesson_id = str(uuid.uuid4())
    lessons[lesson_id] = {
        "id": lesson_id,
        "course_id": course_id,
        "title": lesson.title,
        "content_type": lesson.content_type,
        "content_url": lesson.content_url,
        "order": lesson.order,
        "is_completed": False
    }
    return lessons[lesson_id]

@app.post("/api/lessons/{lesson_id}/quiz")
def create_quiz(lesson_id: str, quiz: QuizCreate):
    if lesson_id not in lessons:
        raise HTTPException(status_code=404, detail="Lesson not found")
    quiz_id = str(uuid.uuid4())
    quizzes[quiz_id] = {
        "id": quiz_id,
        "lesson_id": lesson_id,
        "title": quiz.title,
        "questions": quiz.questions,
        "passing_score": quiz.passing_score
    }
    return quizzes[quiz_id]

@app.post("/api/quizzes/{quiz_id}/submit")
def submit_quiz(quiz_id: str, submission: QuizSubmission):
    if quiz_id not in quizzes:
        raise HTTPException(status_code=404, detail="Quiz not found")
    quiz = quizzes[quiz_id]
    # Simple auto-grading
    correct = 0
    for q in quiz["questions"]:
        if q.get("correct_answer") == submission.answers.get(str(q.get("id"))):
            correct += 1
    score = int((correct / len(quiz["questions"])) * 100) if quiz["questions"] else 0
    passed = score >= quiz["passing_score"]
    return {"score": score, "passed": passed, "correct": correct, "total": len(quiz["questions"])}

@app.put("/api/lessons/{lesson_id}/complete")
def mark_lesson_complete(lesson_id: str):
    if lesson_id not in lessons:
        raise HTTPException(status_code=404, detail="Lesson not found")
    lessons[lesson_id]["is_completed"] = True
    return lessons[lesson_id]

@app.post("/api/courses/{course_id}/enroll")
def enroll_course(course_id: str, enrollment: EnrollmentCreate):
    if course_id not in courses:
        raise HTTPException(status_code=404, detail="Course not found")
    enrollment_id = str(uuid.uuid4())
    enrollments[enrollment_id] = {
        "id": enrollment_id,
        "learner_id": enrollment.learner_id,
        "course_id": course_id,
        "progress_percent": 0,
        "completed_at": None,
        "certificate_url": None
    }
    return enrollments[enrollment_id]

@app.get("/api/learners/{learner_id}/dashboard")
def get_dashboard(learner_id: int):
    learner_enrollments = [e for e in enrollments.values() if e["learner_id"] == learner_id]
    dashboard = []
    for e in learner_enrollments:
        course = courses.get(e["course_id"], {})
        dashboard.append({
            "course_id": e["course_id"],
            "course_title": course.get("title", "Unknown"),
            "progress_percent": e["progress_percent"],
            "completed_at": e["completed_at"],
            "certificate_url": e["certificate_url"]
        })
    return {"learner_id": learner_id, "enrollments": dashboard}