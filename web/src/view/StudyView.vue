<!-- src/views/StudyView.vue -->
<template>
  <div class="study-app">
    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      <div>加载中...</div>
    </div>

    <div v-else-if="error" class="error-container">
      <el-alert :title="error" type="error" :closable="false" show-icon></el-alert>
      <el-button @click="fetchBookData" type="primary" style="margin-top: 20px">重新加载</el-button>
    </div>

    <div v-else class="study-section">
      <!-- 学习进度 -->
      <div class="progress-section">
        <div class="progress-header">
          <h2 class="progress-title">学习进度</h2>
          <span class="progress-text">{{ progressPercentage }}% 已完成</span>
        </div>
        <div class="progress-bar-container">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: `${progressPercentage}%` }"></div>
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

      <!-- 单词卡片容器 -->
      <div class="card-container" v-if="currentWord">
        <div class="word-card" :class="{ flipped: isFlipped }">
          <WordCardFront
            :current-word="currentWord"
            :current-list-type="currentListType"
            :word-options="wordOptions"
            :selected-option="selectedOption"
            @select-option="handleOptionSelect"
            @flip="handleButton"
          />
          <WordCardBack
            :current-word="currentWord"
            :current-list-type="currentListType"
            :is-flipped="isFlipped"
            @remember="handleRemember"
            @mistake="handleMistake"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute,useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Loading } from "@element-plus/icons-vue";
import WordCardFront from "@/components/WordCardFront.vue";
import WordCardBack from "@/components/WordCardBack.vue";
// ===== 状态 =====
const api = "http://localhost:8000";
const loading = ref(false);
const error = ref("");
const wordList = ref([]);
const memoryList = ref([]);
const finalList = ref([]);
const allWords = ref([]);
const currentListType = ref("");
const currentWord = ref(null);
const isFlipped = ref(false);
const selectedOption = ref(null);
const wordOptions = ref([]);

const route = useRoute();
const router = useRouter();
// ===== 计算属性 =====
const totalWords = computed(() => allWords.value.length);
const remainingWords = computed(() => wordList.value.length + memoryList.value.length + finalList.value.length);
const progressPercentage = computed(() => {
  if (totalWords.value === 0) return 0;
  return Math.round(((totalWords.value - remainingWords.value) / totalWords.value) * 100);
});

// ===== 数据获取 =====
const fetchBookData = async () => {
  loading.value = true;
  error.value = "";
  try {
    const bookId = route.params.bookId;
    const response = await fetch(`${api}/api/books/${bookId}/study`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    wordList.value = data.word_list || [];
    memoryList.value = data.memory_list || [];
    finalList.value = data.final_list || [];
    allWords.value = [...wordList.value, ...memoryList.value, ...finalList.value];
    selectNextWord();
  } catch (err) {
    console.error("获取学习数据失败:", err);
    error.value = "获取学习数据失败";
    ElMessage.error("获取学习数据失败: " + err.message);
  } finally {
    loading.value = false;
  }
};

// ===== 单词选择逻辑 =====
const selectNextWord = () => {
  // 检查是否全部完成
  if (!wordList.value.length && !memoryList.value.length && !finalList.value.length) {
    // 跳转到学习完成页面
    router.push({ name: 'StudyComplete' });
    return;
  }

  isFlipped.value = false;
  selectedOption.value = null;
  wordOptions.value = [];

  const available = [];
  if (wordList.value.length) available.push("wordList");
  if (memoryList.value.length) available.push("memoryList");
  if (finalList.value.length) available.push("finalList");

  const type = available[Math.floor(Math.random() * available.length)];
  currentListType.value = type;

  switch (type) {
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

const prepareWordOptions = () => {
  if (!currentWord.value) return;
  const options = [currentWord.value.translation];
  const others = allWords.value.filter(w => w.word !== currentWord.value.word);
  const shuffled = [...others].sort(() => 0.5 - Math.random()).slice(0, 3);
  options.push(...shuffled.map(w => w.translation));
  wordOptions.value = options.sort(() => Math.random() - 0.5);
};

// ===== 事件处理 =====
const handleButton = () => {
  isFlipped.value = true;
};

const handleOptionSelect = (value) => {
  selectedOption.value = value;
  const correct = wordOptions.value[value] === currentWord.value.translation;
  if (correct) {
    ElMessage.success("选择正确！");
    setTimeout(() => handleButton(), 500);
  } else {
    ElMessage.error("选择错误");
    handleButton();
  }
};

const handleRemember = () => {
  if (currentListType.value === "wordList") {
    memoryList.value.push(wordList.value.shift());
  } else if (currentListType.value === "memoryList") {
    finalList.value.push(memoryList.value.shift());
  } else if (currentListType.value === "finalList") {
    finalList.value.shift();
    handleFinalRemember();
  }
  selectNextWord();
};

const handleMistake = () => {
  if (currentListType.value === "memoryList") {
    wordList.value.push(memoryList.value.shift());
  } else if (currentListType.value === "finalList") {
    memoryList.value.push(finalList.value.shift());
  }
  selectNextWord();
};

const handleFinalRemember = async () => {
  try {
    await fetch(`${api}/api/words/remember`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        books_id: route.params.bookId,
        word: currentWord.value.word,
        remember: true,
      }),
    });
  } catch (err) {
    console.error("标记记忆状态失败:", err);
    ElMessage.error("标记记忆状态失败");
  }
};

// ===== 副作用 =====
watch([wordList, memoryList, finalList], () => {
  if (!currentWord.value) selectNextWord();
});

onMounted(() => fetchBookData());
</script>

<style scoped>
/* 只保留布局和进度相关样式，移除卡片内部样式 */
.study-app {
  min-height: 94vh;
  max-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2vh;
  font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

.study-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

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

.card-container {
  perspective: 1200px;
  width: 100%;
  height: 100%;
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

.loading-container,
.error-container {
  text-align: center;
  padding: 50px 0;
}

@media (max-width: 768px) {
  .word-card {
    height: 350px;
  }
}
</style>