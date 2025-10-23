from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
import random

app = FastAPI(title="英语辅助记忆平台API")

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class Translation(BaseModel):
    v: Optional[str] = None
    n: Optional[str] = None
    adj: Optional[str] = None
    adv: Optional[str] = None

class Example(BaseModel):
    text: str
    translation: str

class Word(BaseModel):
    word: str
    translation: Dict[str, str]
    example: Example
    remember: bool = False

class WordBook(BaseModel):
    id: int
    name: str
    description: str
    words: List[Word]

class StudySession(BaseModel):
    book_id: int
    word_list: List[Word]
    memory_list: List[Word]
    final_list: List[Word]

# 模拟数据库
BOOKS_FILE = "books.json"

def load_books():
    if os.path.exists(BOOKS_FILE):
        with open(BOOKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_books(books):
    with open(BOOKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

# 初始数据
initial_books = [
    {
        "id": 1,
        "name": "四级英语单词",
        "description": "四级相关单词书",
        "words": [
            {
                "word": "study",
                "translation": {"v.": "学习", "n.": "研究"},
                "example": {
                    "text": "I am studying English.",
                    "translation": "我正在学习英语。"
                },
                "remember": False
            },
            {
                "word": "memory",
                "translation": {"n.": "记忆"},
                "example": {
                    "text": "He has a good memory.",
                    "translation": "他记忆力很好。"
                },
                "remember": False
            },
            {
                "word": "practice",
                "translation": {"n.": "练习", "v.": "实践"},
                "example": {
                    "text": "Practice makes perfect.",
                    "translation": "熟能生巧。"
                },
                "remember": False
            }
        ]
    },
    {
        "id": 2,
        "name": "高考英语单词",
        "description": "高考必备单词",
        "words": [
            {
                "word": "achieve",
                "translation": {"v.": "达到，完成"},
                "example": {
                    "text": "He achieved his goal.",
                    "translation": "他达到了他的目标。"
                },
                "remember": False
            },
            {
                "word": "benefit",
                "translation": {"n.": "好处", "v.": "受益"},
                "example": {
                    "text": "Exercise benefits your health.",
                    "translation": "锻炼有益于你的健康。"
                },
                "remember": False
            }
        ]
    }
]

# 初始化数据
if not os.path.exists(BOOKS_FILE):
    save_books(initial_books)

# API路由
@app.get("/")
async def root():
    return {"message": "英语辅助记忆平台API"}

@app.get("/api/books", response_model=List[WordBook])
async def get_books():
    """获取所有单词书"""
    return load_books()

@app.get("/api/books/{book_id}", response_model=WordBook)
async def get_book(book_id: int):
    """获取特定单词书"""
    books = load_books()
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="单词书不存在")
    return book

@app.post("/api/books", response_model=WordBook)
async def create_book(book_data: dict):
    """创建新单词书"""
    books = load_books()
    
    # 生成新ID
    new_id = max([b["id"] for b in books], default=0) + 1
    
    new_book = {
        "id": new_id,
        "name": book_data["name"],
        "description": book_data["description"],
        "words": book_data["words"]
    }
    
    books.append(new_book)
    save_books(books)
    return new_book

@app.get("/api/books/{book_id}/study")
async def get_study_session(book_id: int):
    """获取学习会话数据"""
    books = load_books()
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="单词书不存在")
    
    # 随机选择10个未记忆的单词
    unremembered_words = [word for word in book["words"] if not word.get("remember", False)]
    
    if len(unremembered_words) > 10:
        study_words = random.sample(unremembered_words, 10)
    else:
        study_words = unremembered_words
    
    # 初始化学习会话
    session = {
        "book": book,
        "word_list": study_words,
        "memory_list": [],
        "final_list": []
    }
    
    return session

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)