<template>
  <div class="book-selection">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>Michella 辅助记忆平台</h1>
          <div class="header-actions">
            <el-dropdown @command="handleDropdownCommand">
              <el-button type="primary" size="large">
                新建 <el-icon><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="newBook">
                    <el-icon><document-add /></el-icon>
                    新建单词表
                  </el-dropdown-item>
                  <el-dropdown-item command="addWords">
                    <el-icon><plus /></el-icon>
                    在现有单词表内插入单词
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button @click="handleDeleteBook" size="large"
              >删除单词表</el-button
            >
          </div>
        </div>
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
                {{ book.word_num }}
                以记忆单词数量：
                {{ book.remember_num }}
              </p>
            </div>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </div>

  <!-- 新建单词表对话框 -->
  <el-dialog
    v-model="newBookDialogVisible"
    title="新建单词表"
    :close-on-click-modal="false"
  >
    <el-form :model="newBookForm" :rules="newBookRules" ref="newBookFormRef">
      <el-form-item label="单词表名称" prop="name">
        <el-input v-model="newBookForm.name" placeholder="请输入单词表名称">
        </el-input>
      </el-form-item>
      <el-form-item label="学习者身份" prop="identity">
        <el-input
          v-model="newBookForm.identity"
          placeholder="请输入身份如：高中生,四级考生..."
        >
        </el-input>
      </el-form-item>
      <el-form-item label="文章" prop="essay">
        <el-input
          v-model="newBookForm.essay"
          placeholder="请输入需要解析的文章"
          type="textarea"
          :row="3"
        ></el-input>
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input
          v-model="newBookForm.description"
          placeholder="请输入单词表描述（可选）"
          type="textarea"
          :rows="2"
        ></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="newBookDialogVisible = false" :disabled="isCreating"
          >取消</el-button
        >
        <el-button type="primary" @click="createNewBook" :loading="isCreating">
          {{ isCreating ? "创建中..." : "创建" }}
        </el-button>
      </span>
    </template>
  </el-dialog>

  <!-- 创建中加载遮罩 -->
  <el-dialog
    v-model="creatingDialogVisible"
    title="正在创建单词表"
    width="500px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
  >
    <div class="creating-container">
      <el-progress
        :percentage="progressPercentage"
        :status="progressStatus"
        :indeterminate="true"
        :show-text="false"
      />
      <div class="creating-content">
        <el-icon class="is-loading" size="24"><loading /></el-icon>
        <span class="creating-text"
          >正在处理文章并提取单词，这可能需要几分钟时间...</span
        >
      </div>
      <div class="creating-tip">
        <p>请耐心等待，不要关闭页面</p>
      </div>
    </div>
  </el-dialog>

  <!-- 创建结果对话框 -->
  <el-dialog v-model="resultDialogVisible" title="创建完成" width="400px">
    <div class="result-container">
      <el-result icon="success" title="创建成功" :sub-title="resultMessage">
        <template #extra>
          <el-button type="primary" @click="handleResultConfirm"
            >确定</el-button
          >
        </template>
      </el-result>
    </div>
  </el-dialog>

  <!-- 批量删除单词表对话框 -->
  <el-dialog
    v-model="deleteDialogVisible"
    title="选择要删除的单词表"
    width="500px"
    :close-on-click-modal="false"
  >
    <el-checkbox-group v-model="selectedBookIds">
      <el-checkbox
        v-for="book in bookNames"
        :key="book.id"
        :label="book.id"
        class="delete-checkbox-item"
      >
        {{ book.name }}（{{ book.word_num }} 词）
      </el-checkbox>
    </el-checkbox-group>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmDeleteBooks"
          >删除选中</el-button
        >
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { ArrowDown, DocumentAdd, Plus, Loading } from "@element-plus/icons-vue";

const router = useRouter();
// 正确声明响应式数据
const bookNames = ref([]);
const api = "http://localhost:8000";

// 新增的状态变量
const isCreating = ref(false);
const creatingDialogVisible = ref(false);
const resultDialogVisible = ref(false);
const resultMessage = ref("");
const progressPercentage = ref(0);
const progressStatus = ref("");
// 删除相关
const deleteDialogVisible = ref(false);
const selectedBookIds = ref([]);
const fetchBooksName = async () => {
  try {
    const response = await fetch(`${api}/api/bookNames`);
    const data = await response.json();
    bookNames.value = data;
  } catch (error) {
    console.error("获取书籍列表失败:", error);
  }
};

const handleDeleteBook = () => {
  if (bookNames.value.length === 0) {
    ElMessage.warning("暂无单词表可删除");
    return;
  }
  selectedBookIds.value = []; // 重置选择
  deleteDialogVisible.value = true;
};

const selectBook = (book) => {
  router.push(`/memory/${book.id}`);
};

// 新建单词表相关
const newBookDialogVisible = ref(false);
const newBookFormRef = ref(null);
const newBookForm = ref({
  name: "",
  identity: "",
  essay: "",
  description: "",
});
const newBookRules = {
  name: [
    { required: true, message: "请输入单词表名称", trigger: "blur" },
    { min: 1, max: 50, message: "长度在 1 到 50 个字符", trigger: "blur" },
  ],
  identity: [
    { required: true, message: "请输入身份", trigger: "blur" },
    { min: 1, max: 50, message: "长度在 1 到 50 个字符", trigger: "blur" },
  ],
  essay: [
    { required: true, message: "请输入文章内容", trigger: "blur" },
    { min: 1, message: "文章内容不能为空", trigger: "blur" },
  ],
  description: [
    { max: 200, message: "描述长度不能超过200个字符", trigger: "blur" },
  ],
};

const handleDropdownCommand = (command) => {
  if (command === "newBook") {
    newBookDialogVisible.value = true;
    // 重置表单
    newBookForm.value = {
      name: "",
      identity: "",
      essay: "",
      description: "",
    };
    // 重置表单验证
    if (newBookFormRef.value) {
      newBookFormRef.value.clearValidate();
    }
  }
};

const createNewBook = async () => {
  // 表单验证
  if (!newBookFormRef.value) return;

  try {
    const valid = await newBookFormRef.value.validate();
    if (!valid) return;
  } catch (error) {
    // 验证失败
    return;
  }

  isCreating.value = true;
  creatingDialogVisible.value = true;
  newBookDialogVisible.value = false;

  // 模拟进度更新（实际项目中可以根据后端进度反馈来更新）
  const progressInterval = setInterval(() => {
    if (progressPercentage.value < 90) {
      progressPercentage.value += 10;
    }
  }, 3000);

  const data = newBookForm.value;
  try {
    const response = await fetch(`${api}/api/createBook`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    clearInterval(progressInterval);
    progressPercentage.value = 100;

    if (response.ok) {
      const result = await response.json();

      // 显示创建结果
      resultMessage.value = `成功从文章中提取了 ${result.word_num || 0} 个单词`;
      creatingDialogVisible.value = false;
      resultDialogVisible.value = true;

      // 重新获取书籍列表
      await fetchBooksName();
    } else {
      const error = await response.json();
      throw new Error(error.message || "创建失败");
    }
  } catch (error) {
    console.error("创建单词表失败:", error);
    creatingDialogVisible.value = false;
    ElMessage.error(error.message || "创建单词表失败");
  } finally {
    isCreating.value = false;
    progressPercentage.value = 0;
  }
};

const handleResultConfirm = () => {
  resultDialogVisible.value = false;
  // 重置表单
  newBookForm.value = {
    name: "",
    identity: "",
    essay: "",
    description: "",
  };
};

const confirmDeleteBooks = async () => {
  if (selectedBookIds.value.length === 0) {
    ElMessage.warning("请至少选择一个单词表");
    return;
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedBookIds.value.length} 个单词表吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    // 发送删除请求
    const response = await fetch(`${api}/api/delete`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ids: selectedBookIds.value }),
    });

    if (response.ok) {
      ElMessage.success('删除成功');
      deleteDialogVisible.value = false;
      await fetchBooksName(); // 刷新列表
    } else {
      const errorData = await response.json();
      throw new Error(errorData.message || '删除失败');
    }
  } catch (error) {
    if (error.name !== 'Cancel') {
      console.error('删除失败:', error);
      ElMessage.error(error.message || '删除失败，请重试');
    }
  }
};


// 在组件挂载时获取数据
onMounted(() => {
  fetchBooksName();
});
</script>

<style scoped>
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

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
  color: #409eff;
}

.word-count {
  color: #909399;
  font-size: 14px;
}

.creating-container {
  text-align: center;
  padding: 20px 0;
}

.creating-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin: 20px 0;
}

.creating-text {
  font-size: 16px;
  color: #606266;
}

.creating-tip {
  margin-top: 15px;
}

.creating-tip p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.result-container {
  padding: 10px 0;
}

:deep(.el-progress-bar) {
  padding-right: 0;
}

:deep(.el-progress-bar__inner) {
  transition: all 0.3s ease;
}
</style>
