<!-- src/views/StudyComplete.vue -->
<template>
  <div class="study-complete">
    <h1>🎉 学习完成！</h1>
    <p>你已经掌握了本词书的所有单词！</p>
    <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
  </div>
</template>

<style scoped>
.study-complete {
  text-align: center;
  padding: 100px 20px;
  font-family: "Inter", sans-serif;
}
</style>