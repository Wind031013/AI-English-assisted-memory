<!-- src/components/WordCardBack.vue -->
<template>
  <div class="card-back" v-show="isFlipped">
    <div class="back-content">
      <!-- 单词信息区域 -->
      <div class="word-info">
        <h2 class="back-word">{{ currentWord.word }}</h2>
        <h2 class="pronunciation">{{ currentWord.pronunciation }}</h2>
      </div>

      <!-- 可滚动的内容区域 -->
      <div class="scrollable-content">
        <!-- 含义 -->
        <div class="translations">
          <div
            class="translation"
            v-for="(meaning, partOfSpeech) in currentWord.translation"
            :key="partOfSpeech"
          >
            <h3 class="part-of-speech">{{ partOfSpeech }}:</h3>
            <p class="meaning">{{ meaning }}</p>
          </div>
        </div>

        <!-- 例句 -->
        <div
          class="examples"
          v-if="currentWord.example && Array.isArray(currentWord.example.text)"
        >
          <div
            v-for="(text, index) in currentWord.example.text"
            :key="index"
            class="example-pair"
          >
            <div class="example-original">{{ text }}</div>
            <div class="example-translation">
              {{ currentWord.example.translation?.[index] || "" }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="back-actions">
      <div>
        <el-button
          type="primary"
          size="large"
          @click="emit('remember')"
          class="action-btn"
        >
          下一个
        </el-button>
        <el-button
          v-if="currentListType !== 'wordList'"
          type="warning"
          size="large"
          @click="emit('mistake')"
          class="action-btn"
        >
          记错了
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  currentWord: Object,
  currentListType: String,
  isFlipped: Boolean,
});

const emit = defineEmits(['remember', 'mistake']);
</script>

<style scoped>
/* 保留你原有的 back 相关样式 */
.card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-sizing: border-box;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  transform: rotateY(180deg);
}

.back-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.word-info {
  flex-shrink: 0;
  margin: 15px 0 30px 15px;
}

.back-word {
  font-size: 2.2rem;
  margin: 0;
  font-weight: bold;
}

.pronunciation {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.9);
  margin-top: 5px;
}

.translations {
  margin-bottom: 30px;
}

.translation {
  display: flex;
  gap: 10px;
  font-size: 1.5rem;
}

.part-of-speech {
  margin: 0;
  font-weight: bold;
}

.meaning {
  margin: 0;
  opacity: 0.95;
}

.examples {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.example-pair {
  background: rgba(255, 255, 255, 0.2);
  padding: 14px;
  border-radius: 8px;
}

.example-original {
  font-style: italic;
  font-size: 1.3rem;
  margin-bottom: 6px;
  line-height: 1.5;
}

.example-translation {
  font-size: 1.2rem;
  opacity: 0.95;
  line-height: 1.5;
}

/* 滚动区域 */
.scrollable-content {
  flex: 1;
  overflow-y: auto;
  margin:0 0 0 15px;
  min-height: 0;
}

.scrollable-content::-webkit-scrollbar {
  width: 6px;
}
.scrollable-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}
.scrollable-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}
.scrollable-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

.back-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.action-btn {
  min-width: 120px;
}
</style>