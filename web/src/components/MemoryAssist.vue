<template>
  <div class="study-app">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <div>加载中...</div>
    </div>

    <div v-else-if="error" class="error-container">
      <el-alert :title="error" type="error" :closable="false" show-icon>
      </el-alert>
      <el-button @click="fetchBookData" type="primary" style="margin-top: 20px">
        重新加载
      </el-button>
    </div>
    <!-- 学习区域 -->
    <div v-else class="study-section">
      <!-- 学习进度 -->
      <div class="progress-section">
        <div class="progress-header">
          <h2 class="progress-title">学习进度</h2>
          <span class="progress-text">{{ progressPercentage }}% 已完成</span>
        </div>
        <div class="progress-bar-container">
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: `${progressPercentage}%` }"
            ></div>
          </div>
        </div>
        <div class="progress-stats">
          <span class="stat-item">
            <span class="stat-number">{{ remainingWords }}</span>
            <span class="stat-label">剩余单词</span>
          </span>
          <span class="stat-divider">|</span>
          <span class="stat-item">
            <span class="stat-number">{{ totalWords }}</span>
            <span class="stat-label">总单词数</span>
          </span>
        </div>
      </div>

      <!-- 单词卡片 -->
      <div class="card-container" v-if="currentWord">
        <div class="word-card" :class="{ flipped: isFlipped }">
          <!-- 卡片正面 -->
          <div class="card-front">
            <!-- 单词列表 -->
            <div class="wordList-content" v-if="currentListType == 'wordList'">
              <h2 class="word">{{ currentWord.word }}</h2>
              <div class="word-options">
                <el-radio-group
                  v-model="selectedOption"
                  @change="handleOptionSelect"
                  class="options-group"
                >
                  <el-radio
                    v-for="(option, index) in wordOptions"
                    :key="index"
                    :value="index"
                    class="option-item"
                  >
                    <div class="option-content">
                      <div
                        v-for="(value, key) in option"
                        :key="key"
                        class="meaning-line"
                      >
                        <span class="part-of-speech">{{ key }}</span>
                        <span class="meaning">{{ value }}</span>
                      </div>
                    </div>
                  </el-radio>
                </el-radio-group>
              </div>
            </div>
            <!-- 记忆列表 -->
            <div
              class="final-content"
              v-else-if="currentListType == 'memoryList'"
            >
              <h2 class="word">{{ currentWord.word }}</h2>
              <div class="example">
                {{ currentWord.example.text }}
              </div>
            </div>
            <!-- 最终列表 -->
            <div class="word-content" v-else>
              <h2 class="word">{{ currentWord.word }}</h2>
            </div>
            <!-- 操作按钮 -->
            <div class="actions" v-if="currentListType != 'wordList'">
              <el-button
                type="success"
                size="large"
                @click.stop="handleButton"
                class="action-btn"
              >
                认识
              </el-button>
              <el-button
                type="danger"
                size="large"
                @click.stop="handleButton"
                class="action-btn"
              >
                不认识
              </el-button>
            </div>
          </div>
          <!-- 卡片背面 -->
          <div class="card-back" v-show="isFlipped">
            <div class="back-translation-content">
              <!-- 单词以及发音 -->
              <h2 class="back-word">{{ currentWord.word }}</h2>
              <h2 class="pronunciation">{{ currentWord.pronunciation }}</h2>
              <div class="translations">
                <!-- 单词含义 -->
                <div
                  class="translation"
                  v-for="(meaning, partOfSpeech) in currentWord.translation"
                >
                  <h3 class="part-of-speech">{{ partOfSpeech }}:</h3>
                  <p class="meaning">{{ meaning }}</p>
                </div>
                <!-- 单词例句 -->
                <div class="example">
                  {{ currentWord.example.text }}
                  {{ currentWord.example.translation }}
                </div>
              </div>
            </div>
            <!-- 操作按钮 -->
            <div class="back-actions">
              <div>
                <el-button
                  type="primary"
                  size="large"
                  @click.stop="handleRemember"
                  class="action-btn"
                >
                  下一个
                </el-button>
                <el-button
                  v-if="currentListType != 'wordList'"
                  type="warning"
                  size="large"
                  @click.stop="handleMistake"
                  class="action-btn"
                >
                  记错了
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { Loading } from "@element-plus/icons-vue";

const api = "http://localhost:8000";
const loading = ref(false);
const error = ref("");

// 学习数据
const wordList = ref([]);
const memoryList = ref([]);
const finalList = ref([]);

// 当前学习状态
const currentListType = ref(""); // 'wordList', 'memoryList', 'finalList'
const currentWord = ref(null);
const isFlipped = ref(false);
const selectedOption = ref("");
const optionCorrect = ref(false);
const wordOptions = ref([]);
let allWords = [];

const route = useRoute();

// 计算属性
const totalWords = computed(() => {
  return 10;
});

const remainingWords = computed(() => {
  return (
    wordList.value.length + memoryList.value.length + finalList.value.length
  );
});

// 进度条
const progressPercentage = computed(() => {
  if (totalWords.value === 0) return 0;
  const learned = totalWords.value - remainingWords.value;
  return Math.round((learned / totalWords.value) * 100);
});

// 获取学习数据
const fetchBookData = async () => {
  loading.value = true;
  error.value = "";

  try {
    const bookId = route.params.bookId;
    const response = await fetch(`${api}/api/books/${bookId}/study`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    wordList.value = data.word_list || [];
    memoryList.value = data.memory_list || [];
    finalList.value = data.final_list || [];
    allWords = [...wordList.value, ...memoryList.value, ...finalList.value];
    // 初始化学习状态
    selectNextWord();
  } catch (err) {
    console.error("获取学习数据失败:", err);
    error.value = "获取学习数据失败";
    ElMessage.error("获取学习数据失败: " + err.message);
  } finally {
    loading.value = false;
  }
};

// 随机选择下一个单词
const selectNextWord = () => {
  // 重置状态
  isFlipped.value = false;
  selectedOption.value = "";
  optionCorrect.value = false;
  wordOptions.value = [];

  // 检查是否有单词需要学习
  if (
    wordList.value.length === 0 &&
    memoryList.value.length === 0 &&
    finalList.value.length === 0
  ) {
    currentWord.value = null;
    currentListType.value = "";
    return;
  }

  // 随机选择列表类型
  const availableLists = [];
  if (wordList.value.length > 0) availableLists.push("wordList");
  if (memoryList.value.length > 0) availableLists.push("memoryList");
  if (finalList.value.length > 0) availableLists.push("finalList");

  if (availableLists.length === 0) {
    currentWord.value = null;
    currentListType.value = "";
    return;
  }

  const randomListType =
    availableLists[Math.floor(Math.random() * availableLists.length)];
  currentListType.value = randomListType;

  switch (randomListType) {
    case "wordList":
      currentWord.value = wordList.value[0];
      prepareWordOptions();
      break;
    case "memoryList":
      currentWord.value = memoryList.value[0];
      break;
    case "finalList":
      currentWord.value = finalList.value[0];
      break;
  }
};

// 准备单词列表的选项
const prepareWordOptions = () => {
  if (!currentWord.value) return;

  // 创建选项数组
  const options = [currentWord.value.translation];

  // 过滤掉当前单词
  const otherWords = allWords.filter(
    (word) => word.word !== currentWord.value.word
  );

  // 随机选择3个干扰项
  const shuffled = [...otherWords].sort(() => 0.5 - Math.random());
  const selected = shuffled.slice(0, 3);

  // 将干扰项添加到选项中
  selected.forEach((word) => {
    options.push(word.translation);
  });

  // 随机排序选项
  wordOptions.value = options.sort(() => Math.random() - 0.5);
};

const handleButton = () => {
  isFlipped.value = true;
};
const handleRemember = () => {
  // 从记忆列表移动到最终列表
  if (currentListType.value === "wordList" && currentWord.value) {
    const word = wordList.value.shift();
    memoryList.value.push(word);
  }
  if (currentListType.value === "memoryList" && currentWord.value) {
    const word = memoryList.value.shift();
    finalList.value.push(word);
  }
  if (currentListType.value === "finalList" && currentWord.value) {
    finalList.value.shift();
    handleFinalRemember()
  }
  selectNextWord();
};

const handleMistake = () => {
  if (currentListType.value === "memoryList") {
    const word = memoryList.value.shift();
    wordList.value.push(word);
  } else if (currentListType.value === "finalList") {
    // 从最终列表移动到记忆列表
    const word = finalList.value.shift();
    memoryList.value.push(word);
  }
  selectNextWord();
};

const handleFinalRemember = async () => {
  try {
    const data = {
      books_id: route.params.bookId,
      word: currentWord.value['word'],
      remember: true,
    }
    const response = await fetch(`${api}/api/words/remember`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error("标记记忆状态失败");
    }
  } catch (err) {
    console.error("标记记忆状态失败:", err);
    ElMessage.error("标记记忆状态失败");
  }
};

const handleOptionSelect = (value) => {
  if (!currentWord.value) return;
  optionCorrect.value =
    wordOptions.value[value] === currentWord.value.translation;
  if (optionCorrect.value) {
    ElMessage.success("选择正确！");
    // 延迟显示下一个单词
    setTimeout(() => {
      handleButton();
    }, 500);
  } else {
    // 选择错误，显示背面
    handleButton();
    ElMessage.error("选择错误");
  }
};

const resetStudy = () => {
  // 重新加载数据
  fetchBookData();
};

// 监听数据变化
watch([wordList, memoryList, finalList], () => {
  if (!currentWord.value) {
    selectNextWord();
  }
});

onMounted(() => {
  fetchBookData();
});
</script>

<style scoped>
/* 页面总体布局 */
.study-app {
  min-height: 94vh;
  max-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2vh;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    sans-serif;
}
/* 卡片部分 */
/* 总体布局 */
.study-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
/* 进度部分 */
.progress-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.progress-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
}
.progress-text {
  font-size: 0.875rem;
  color: #7f8c8d;
  font-weight: 500;
}
.progress-bar-container {
  margin-bottom: 16px;
}
.progress-bar {
  height: 8px;
  background: #ecf0f1;
  border-radius: 4px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  border-radius: 4px;
  transition: width 0.5s ease;
}
.progress-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
}

.stat-label {
  font-size: 0.75rem;
  color: #7f8c8d;
  margin-top: 4px;
}

.stat-divider {
  color: #bdc3c7;
  font-weight: 300;
}

.pronunciation {
  font-size: 1.5rem;
  margin-top: 0px;
  margin-bottom: 10px;
  color: #666;
  font-weight: bold;
  line-height: 1.5;
  word-wrap: break-word;
}

.word-content {
  display: flex;
  height: 100%;
  justify-content: center;
  align-items: center;
}
.wordList-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.word {
  font-size: 3rem;
}

.study-container {
  max-width: 800px;
  max-height: 800px;
  margin: 0 auto;
  padding: 20px;
}

.loading-container {
  text-align: center;
  padding: 50px 0;
}

.error-container {
  text-align: center;
  padding: 50px 0;
}

.progress-info {
  margin-bottom: 30px;
}

.card-container {
  perspective: 1200px;
  width: 100%;
  height: 100%;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.word-card {
  position: relative;
  width: 100%;
  height: 60vh;
  transition: transform 0.6s;
  transform-style: preserve-3d;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.word-card.flipped {
  transform: rotateY(180deg);
}

.card-front,
.card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 12px;
  padding: 30px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-sizing: border-box;
}

.card-front {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.card-back {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  transform: rotateY(180deg);
}

.translation-content {
  display: flex;
  flex-direction: column;
}
.back-translation-content {
  margin-left: 20px;
}
.word {
  font-size: 2.5em;
  margin-bottom: 20px;
  font-weight: bold;
}
.back-word {
  font-size: 2.5em;
  margin-bottom: 0px;
}
.word-type {
  font-size: 1.2em;
  opacity: 0.8;
  margin-bottom: 20px;
}
.translations {
  margin-top: 50px;
}
.translation {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.8em;
}

.part-of-speech {
  margin: 0; /* 移除默认外边距 */
}

.meaning {
  margin: 0; /* 移除默认外边距 */
}

.example {
  margin-top: 30px;
  font-size: 1.5rem;
  padding: 15px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
}

.example-original {
  font-style: italic;
  margin-bottom: 8px;
}

.example-translation {
  opacity: 0.9;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.action-btn {
  min-width: 120px;
}

.back-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.word-options {
  margin-top: 80px;
}

.options-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%;
}

.option-item {
  background: rgba(255, 255, 255, 0.2);
  padding: 15px;
  border-radius: 8px;
  margin: 0;
  transition: background-color 0.3s;
  width: 40vh;
}

/* 在CSS中添加了新的样式 */
.option-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.meaning-line {
  display: flex;
  align-items: center;
  gap: 5px;
}

.option-item:hover {
  background: rgba(255, 255, 255, 0.3);
}

:deep(.option-item .el-radio__label) {
  color: white;
  font-size: 1.1em;
}

:deep(.option-item .el-radio__input.is-checked + .el-radio__label) {
  color: white;
}

.completion-message {
  text-align: center;
  padding: 50px 0;
}

@media (max-width: 768px) {
  .study-container {
    padding: 10px;
  }

  .word-card {
    height: 350px;
  }

  .word {
    font-size: 2em;
  }

  .actions,
  .back-actions {
    flex-direction: column;
    align-items: center;
  }

  .action-btn {
    width: 100%;
    max-width: 200px;
  }
}
</style>
