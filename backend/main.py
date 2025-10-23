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
class BookNameInfo(BaseModel):
    id: int
    name: str
    description: str
    rememberLength: int
    unknownLength: int

class WordRememberInfo(BaseModel):
    books_id: str
    word: str
    remember: Optional[bool]

# 模拟数据库
BOOKS_FILE = r"E:\English_study\backend\books.json"

def load_books():
    if os.path.exists(BOOKS_FILE):
        with open(BOOKS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def book_names():
    books = load_books()
    result = []
    for book in books:
        words = book.get("words", [])
        remember_count = sum(1 for word in words if word.get("remember") is True)
        unknown_count = sum(1 for word in words if word.get("remember") is False)
        result.append({
            "id": book["id"],
            "name": book["name"],
            "description": book["description"],
            "rememberLength": remember_count,
            "unknownLength": unknown_count
        })
    return result

# API路由
@app.get("/")
async def root():
    return {"message": "英语辅助记忆平台API"}

@app.get("/api/bookNames", response_model=List[BookNameInfo])
async def get_book_names():
    """获取所有单词书的名称"""
    return book_names()

@app.get("/api/books/{book_id}/study")
async def get_study_session(book_id: str):
    books = load_books()
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        raise HTTPException(status_code=404, detail="单词书不存在")
    unremembered_words = [word for word in book["words"] if not word.get("remember", False)]
    if len(unremembered_words) > 10:
        study_words = random.sample(unremembered_words, 10)
    else:
        study_words = unremembered_words

    word_list = [word for word in study_words if word.get("word_list") is True]
    memory_list = [word for word in study_words if word.get("memory_list") is True]
    final_list = [word for word in study_words if word.get("final_list") is True]
    
    session = {
        "word_list": word_list,
        "memory_list": memory_list,
        "final_list": final_list
    }
    return session
    
@app.post("/api/words/remember")
async def remember_words(word: WordRememberInfo):
    """标记单词为已记住"""
    books = load_books()
    book_id = word.books_id
    
    # 查找对应的书籍
    book_index = None
    for i, b in enumerate(books):
        if b["id"] == book_id:
            book_index = i
            break
    
    if book_index is None:
        raise HTTPException(status_code=404, detail="单词书不存在")
    
    # 查找并更新对应的单词
    word_found = False
    for w in books[book_index]["words"]:
        if w["word"] == word.word:
            w["remember"] = word.remember  # 设置为传入的remember值
            word_found = True
            break
    
    if not word_found:
        raise HTTPException(status_code=404, detail="单词不存在")
    
    # 保存更新后的数据
    with open(BOOKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=2)
    
    return {"message": "单词记忆状态更新成功"}
if __name__ == "__main__":
    import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(
        'main:app',
        host="0.0.0.0", 
        port=8000,
        reload=True
    )