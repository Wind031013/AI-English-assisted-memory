<template>
  <div class="book-selection">
    <el-container>
      <el-header>
        <h1>Michella辅助记忆平台</h1>
        <p>选择单词书开始学习</p>
      </el-header>

      <el-main>
        <div class="book-list">
          <el-card
            v-for="book in bookNames"
            :key="book.id"
            class="book-card"
            shadow="hover"
            @click="selectBook(book)"
          >
            <div class="book-info">
              <h3>{{ book.name }}</h3>
              <p>{{ book.description }}</p>
              <p class="word-count">
                单词数量:
                {{ book.rememberLength + book.unknownLength }}
                以记忆单词数量：
                {{ book.rememberLength }}
              </p>
            </div>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
// 正确声明响应式数据
const bookNames = ref([]);
const api = "http://localhost:8000";

const fetchBooksName = async () => {
  try {
    const response = await fetch(`${api}/api/bookNames`);
    const data = await response.json();
    bookNames.value = data;
  } catch (error) {
    console.error("获取书籍列表失败:", error);
  }
};

const selectBook = (book) => {
  router.push(`/memory/${book.id}`)
};

// 在组件挂载时获取数据
onMounted(() => {
  fetchBooksName();
});
</script>

<style scoped>
.book-selection {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
.book-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}
.book-card {
  cursor: pointer;
  transition: transform 0.3s;
}
.book-card:hover {
  transform: translateY(-5px);
}
.book-info h3 {
  margin: 0 0 10px 0;
  color: #409EFF;
}

.word-count {
  color: #909399;
  font-size: 14px;
}
</style>
