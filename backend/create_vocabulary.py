EXTRACT_SYSTEM_PROMPT = """
你是一个专业的英语词汇分析助手,我会提供一篇英语短文,请以{identity}学习者的角度提取重点单词,
根据{identity}，从中筛选出属于该阶段/考试大纲范围内的单词。
返回格式为answer后一个列表,样例如下
{{
  "answer": [
    "read",
    "write",
    "play",
    "work",
    ...
  ]
}}
"""

VOCABULARY_SYSTEM_PROMPT = """
你是一个专业的英语词典助手。请根据用户输入的英语单词，提供以下信息：
1. 单词的读音:使用国际音标标注
2. 单词的词性以及其每个词性下的不同含义
3. 用单词的每种词性都生成一个例句以及例句翻译,例句需要简短易懂
输出样例：
输入:read
输出:
{
  "word": "read",
  "pronunciation": "/riːd/",
  "translation": {
    "v.": "阅读",
    "n.": "读物"
  },
  "example": {
    "text": ["I read every day.", "This book is a good read."],
    "translation": ["我每天都会阅读。","这本书是个很好的读物。"] 
  },
}
"""
SAVE_PATH = r'E:\English_study\AI-English-assisted-memory\backend\data'
import json
import uuid
from zhipuai import ZhipuAI

class VocabularyGenerator:
    def __init__(self, api_key, model):
        self.api_key = api_key
        self.zhipuai = ZhipuAI(api_key=api_key)
        self.model = model
    
    def send_request(self, prompt, content):
        response = self.zhipuai.chat.completions.create(
            model = self.model,
            messages=[
                {"role": "system", 
                "content": prompt },
                {"role": "user", "content": content},
            ],
            response_format= {
                'type': 'json_object'
            }
        )
        return response.choices[0].message.content
    
    def build_word(self, word):
        try:
            result = json.loads(word)
            # 将其余几项信息添加到字典中
            memory = {
                'remember': False,
                'last_review': None,
                'wrong_count':0
            }
            word_list = True
            memory_list = False
            final_list = False
            result['memory'] = memory
            result['word_list'] = word_list
            result['memory_list'] = memory_list
            result['final_list'] = final_list
            return result
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return None
    
    def init_vocabulary(self, name, description, word_num):
        vocabulary = []
        information =  {
            "id" : str(uuid.uuid4()),
            "name":name,
            "description": description,
            "word_num": word_num,
            "remember_num":0
        }
        vocabulary.append(information)
        return vocabulary
    
    def save_vocabulary(self, vocabulary, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(vocabulary, f, indent=4, ensure_ascii=False)
    
    def extract_words_from_essay(self, prompt, essay):
        try:
            result = self.send_request(prompt, essay)
            words = json.loads(result)
            return  words.get("answer", [])
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return []
        
    def building_vocabulary(self, name, prompt, words, description,word_num):
        print("开始构建词汇表...")
        vocabulary = self.init_vocabulary(name,description,word_num)
        processed = 0
        for word in words:
            vocabulary.append(self.build_word(self.send_request(prompt, word)))
            processed += 1
            print(f"正在处理单词 ({processed}/{word_num})...")
        print("保存词汇表...")
        return vocabulary
        
    def create_vocabulary_from_essay(
        self, 
        name, 
        description,
        identity, 
        essay,
        system_prompt=[EXTRACT_SYSTEM_PROMPT, VOCABULARY_SYSTEM_PROMPT]):
        #  提示词填充
        prompt = system_prompt[0].format(identity=identity)
        print("开始提取单词")
        words = self.extract_words_from_essay(prompt, essay)
        word_num = len(words)
        print(f"提取到{word_num}个单词")
        file_name = f"{SAVE_PATH}\{name}.json"
        self.save_vocabulary(self.building_vocabulary(name, system_prompt[1], words, description, word_num), file_name)
        print("词汇表创建完成")
        return word_num