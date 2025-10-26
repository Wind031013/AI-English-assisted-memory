<!-- src/components/WordCardFront.vue -->
<template>
  <div class="card-front">
    <!-- 单词列表 -->
    <div class="wordList-content" v-if="currentListType === 'wordList'">
      <h2 class="word">{{ currentWord.word }}</h2>
      <div class="word-options">
        <el-radio-group
          v-model="localSelectedOption"
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
    <div class="final-content" v-else-if="currentListType === 'memoryList'">
      <div class="examples">
        <div
          v-for="(text, index) in currentWord.example?.text"
          :key="index"
          class="example-card"
        >
          <div class="example-original">{{ text }}</div>
        </div>
      </div>
    </div>

    <!-- 最终列表 -->
    <div class="word-content" v-else>
      <h2 class="word">{{ currentWord.word }}</h2>
    </div>

    <!-- 操作按钮（非 wordList 时显示） -->
    <div class="actions" v-if="currentListType !== 'wordList'">
      <el-button
        type="success"
        size="large"
        @click="emit('flip')"
        class="action-btn"
      >
        认识
      </el-button>
      <el-button
        type="danger"
        size="large"
        @click="emit('flip')"
        class="action-btn"
      >
        不认识
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({
  currentWord: Object,
  currentListType: String,
  wordOptions: Array,
  selectedOption: [String, Number, null],
});

const emit = defineEmits(["selectOption", "flip"]);

// 本地响应式副本，避免直接修改父级 prop
const localSelectedOption = ref(props.selectedOption);

// 同步父级变化
watch(
  () => props.selectedOption,
  (val) => {
    localSelectedOption.value = val;
  }
);

const handleOptionSelect = (value) => {
  emit("selectOption", value);
};
</script>

<style scoped>
/* 保留你原有的 front 相关样式（可从主组件复制） */
.card-front {
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.word {
  font-size: 3rem;
}

.wordList-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.word-content {
  display: flex;
  height: 100%;
  justify-content: center;
  align-items: center;
}

.example {
  margin-top: 30px;
  font-size: 1.5rem;
  padding: 15px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
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

.final-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 20px;
  box-sizing: border-box;
}

.examples {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  max-width: 600px;
}

.example-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(6px);
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
  width: 100%;
  text-align: center;
}

.example-card:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.example-original {
  font-size: 1.4rem;
  line-height: 1.6;
  color: white;
  font-weight: 400;
  word-break: break-word;
}

:deep(.option-item .el-radio__label) {
  color: white;
  font-size: 1.1em;
}

:deep(.option-item .el-radio__input.is-checked + .el-radio__label) {
  color: white;
}
</style>
