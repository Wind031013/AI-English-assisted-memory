from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
import random
import glob
import create_vocabulary

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
    id: str
    name: str
    description: str
    word_num: int
    remember_num: int

class WordRememberInfo(BaseModel):
    books_id: str
    word: str
    remember: Optional[bool]
    
class CreateBookInfo(BaseModel):
    name: str
    identity: str
    essay: str
    description: str
    
class DeleteRequest(BaseModel):
    ids: List[str]

# 模拟数据库
DATA_PATH = r"E:\English_study\AI-English-assisted-memory\backend\data"
BOOK_MAPPING_FILE_PATH = r"E:\English_study\AI-English-assisted-memory\backend\book_mapping.json"
api_key="2bdaa31b12a949ed8ff51cb875146002.4mqQT6TIDgVAnd1Y"
model = "GLM-4-Flash"
def load_json(file_name):
    try:
        print(f"尝试加载文件: {file_name}")
        if os.path.exists(file_name):
            with open(file_name, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"文件不存在: {file_name}")
            return {}
    except Exception as e:
        print(f"加载JSON文件时出错: {e}")
        raise

def load_book_names():
    id_to_fileName = {}
    json_files= glob.glob(rf"{DATA_PATH}\*.json")
    result = []
    for file_path in json_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            id_to_fileName[data[0]['id']] = file_path
            result.append(data[0])
    save_book_mapping(id_to_fileName)
    return result
            
def save_book_mapping(id_to_fileName):
    with open(BOOK_MAPPING_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(id_to_fileName, f, ensure_ascii=False, indent=4)
def book_names():
    books = load_json()
    print(books)
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
    return load_book_names()

@app.get("/api/books/{book_id}/study")
async def get_study_session(book_id: str):
    mapping = load_json(BOOK_MAPPING_FILE_PATH)
    file_name = mapping.get(book_id)
    if not file_name:
        raise HTTPException(status_code=404, detail="单词书不存在")
    book = load_json(file_name)[1:]
    unremembered_words = [word for word in book if not word["memory"].get("remember", False)]
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
    
@app.post("/api/createBook")
async def create_book(bookInfo: CreateBookInfo):
    generator = create_vocabulary.VocabularyGenerator(api_key,model)
    word_num = generator.create_vocabulary_from_essay(bookInfo.name,bookInfo.description,bookInfo.identity,bookInfo.essay)
    return {"word_num": word_num}

@app.post("/api/words/remember")
async def remember_words(wordInfo: WordRememberInfo):
    """标记单词为已记住"""
    mapping = load_json(BOOK_MAPPING_FILE_PATH)
    file_name = mapping.get(wordInfo.books_id)
    if not file_name:
        raise HTTPException(status_code=404, detail="单词书不存在")
    
    # 加载单词书数据
    book_data = load_json(file_name)
    if not book_data:
        raise HTTPException(status_code=404, detail="单词书数据为空")
    
    # 更新单词的remember状态
    updated = False
    for word_item in book_data[1:]:
        if word_item.get("word") == wordInfo.word:
            # 确保memory字段存在
            if "memory" not in word_item:
                word_item["memory"] = {}
            word_item["memory"]["remember"] = True
            updated = True
            break
        
    if not updated:
        raise HTTPException(status_code=404, detail="单词不存在")
    
    book_data[0]["remember_num"] += 1
    
    # 保存更新后的数据回文件
    try:
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(book_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存文件失败: {str(e)}")
    
    return {"message": "单词记忆状态更新成功", "word": wordInfo.word, "remember": True}
    
@app.post("/api/delete")
def delete_book(request:DeleteRequest):
    """删除单词书"""
    mapping = load_json(BOOK_MAPPING_FILE_PATH)
    for id in request.ids:
        file_name = mapping.get(id)
        if file_name:
            os.remove(file_name)
            del mapping[id]
            save_book_mapping(mapping)
            return {"message": "单词书删除成功"}
        
    
if __name__ == "__main__":
    import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(
        'main:app',
        host="0.0.0.0", 
        port=8000,
        reload=True
    )