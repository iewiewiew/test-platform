<template>
  <div class="common-list-container" v-loading="store.loading">
    <div class="common-header-bar">
      <div class="common-search-bar">
        <el-form :inline="true" :model="searchForm" class="demo-form-inline search-form-inline">
          <el-form-item label="测试环境">
            <el-select
              v-model="selectedEnvironmentId"
              placeholder="请选择测试环境"
              style="width: 180px"
              @change="handleEnvironmentChange"
              clearable
            >
              <el-option
                v-for="env in environments"
                :key="env.id"
                :label="env.env_name"
                :value="env.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <div v-if="selectedEnvironmentId" class="business-buttons-wrapper">
      <div class="business-buttons-container">
        <el-button
          type="primary"
          @click="handleCreateRepository"
          class="business-button"
        >
          <el-icon><FolderAdd /></el-icon>
          <span>新建仓库</span>
        </el-button>

        <el-button
          type="success"
          @click="handleCreateIssue"
          class="business-button"
        >
          <el-icon><DocumentAdd /></el-icon>
          <span>新建工作项</span>
        </el-button>
      </div>
    </div>

    <div v-else class="empty-tip">
      <el-empty description="请先选择测试环境" :image-size="100" />
    </div>

    <!-- 新建仓库对话框 -->
    <el-dialog
      v-model="showRepositoryDialog"
      title="新建仓库"
      width="60%"
      :before-close="handleRepositoryDialogClose"
    >
      <el-form :model="repositoryForm" label-width="140px" :rules="repositoryRules" ref="repositoryFormRef">
        <el-form-item label="仓库名称" prop="name">
          <el-input v-model="repositoryForm.name" placeholder="请输入仓库名称" />
        </el-form-item>
        <el-form-item label="仓库路径" prop="path">
          <el-input v-model="repositoryForm.path" placeholder="请输入仓库路径，如：test_repo_001" />
        </el-form-item>
        <el-form-item label="命名空间路径" prop="namespace_path">
          <el-input v-model="repositoryForm.namespace_path" placeholder="请输入命名空间路径，如：testent004" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="repositoryForm.description" type="textarea" :rows="3" placeholder="请输入仓库描述" />
        </el-form-item>
        <el-form-item label="是否公开">
          <el-switch v-model="repositoryForm.public" :active-value="1" :inactive-value="0" />
        </el-form-item>
        <el-form-item label="创建README">
          <el-switch v-model="repositoryForm.readme" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRepositoryDialog = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmCreateRepository" :loading="executing">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 新建工作项对话框 -->
    <el-dialog
      v-model="showIssueDialog"
      title="新建工作项"
      width="60%"
      :before-close="handleIssueDialogClose"
    >
      <el-form :model="issueForm" label-width="140px" :rules="issueRules" ref="issueFormRef">
        <el-form-item label="标题" prop="title">
          <el-input v-model="issueForm.title" placeholder="请输入工作项标题" />
        </el-form-item>
        <el-form-item label="工作项类型ID" prop="issue_type_id">
          <el-input-number v-model="issueForm.issue_type_id" :min="1" placeholder="请输入工作项类型ID" style="width: 100%" />
        </el-form-item>
        <el-form-item label="项目ID" prop="project_id">
          <el-input-number v-model="issueForm.project_id" :min="1" placeholder="请输入项目ID" style="width: 100%" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-input-number v-model="issueForm.priority" :min="0" placeholder="优先级，默认0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="指派人ID">
          <el-input-number v-model="issueForm.assignee_id" :min="0" placeholder="指派人ID，0表示不指派" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showIssueDialog = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmCreateIssue" :loading="executing">
          创建
        </el-button>
      </template>
    </el-dialog>

    <!-- 执行结果对话框 -->
    <el-dialog
      v-model="showResultDialog"
      title="执行结果"
      width="80%"
    >
      <div v-if="executionResult">
        <el-tabs v-model="activeResultTab">
          <el-tab-pane label="响应结果" name="response">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="状态码">
                <el-tag :type="executionResult.response.status_code < 400 ? 'success' : 'danger'">
                  {{ executionResult.response.status_code }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="响应数据">
                <pre class="result-json">{{ formatJson(executionResult.response.data) }}</pre>
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
          <el-tab-pane label="请求信息" name="request">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="URL">
                <code>{{ executionResult.request.url }}</code>
              </el-descriptions-item>
              <el-descriptions-item label="方法">
                <el-tag :type="getMethodType(executionResult.request.method)">
                  {{ executionResult.request.method }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="请求体">
                <pre class="result-json">{{ formatJson(executionResult.request.body) }}</pre>
              </el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>
        </el-tabs>
      </div>
      <template #footer>
        <el-button type="primary" @click="showResultDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { FolderAdd, DocumentAdd } from "@element-plus/icons-vue";
import { useBusinessStore } from "@/stores/business/businessStore";
import { useTestEnvironmentStore } from "@/stores/test/testEnvironmentStore";

const store = useBusinessStore();
const testEnvironmentStore = useTestEnvironmentStore();

const selectedEnvironmentId = ref(null);
const environments = ref([]);
const showRepositoryDialog = ref(false);
const showIssueDialog = ref(false);
const showResultDialog = ref(false);
const executing = ref(false);
const executionResult = ref(null);
const activeResultTab = ref("response");

const searchForm = ref({});

const repositoryFormRef = ref(null);
const issueFormRef = ref(null);

const repositoryForm = ref({
  name: "",
  path: "",
  namespace_path: "",
  description: "",
  public: 0,
  readme: 1,
});

const issueForm = ref({
  title: "",
  issue_type_id: null,
  project_id: null,
  priority: 0,
  assignee_id: 0,
});

const repositoryRules = {
  name: [{ required: true, message: "请输入仓库名称", trigger: "blur" }],
  path: [{ required: true, message: "请输入仓库路径", trigger: "blur" }],
  namespace_path: [{ required: true, message: "请输入命名空间路径", trigger: "blur" }],
};

const issueRules = {
  title: [{ required: true, message: "请输入工作项标题", trigger: "blur" }],
  issue_type_id: [{ required: true, message: "请输入工作项类型ID", trigger: "blur" }],
  project_id: [{ required: true, message: "请输入项目ID", trigger: "blur" }],
};

const getMethodType = (method) => {
  const typeMap = {
    GET: "success",
    POST: "primary",
    PUT: "warning",
    DELETE: "danger",
    PATCH: "info",
  };
  return typeMap[method] || "";
};

const handleEnvironmentChange = () => {
  if (selectedEnvironmentId.value) {
    // 环境变更处理
  }
};

const handleCreateRepository = () => {
  if (!selectedEnvironmentId.value) {
    ElMessage.warning("请先选择测试环境");
    return;
  }
  showRepositoryDialog.value = true;
};

const handleCreateIssue = () => {
  if (!selectedEnvironmentId.value) {
    ElMessage.warning("请先选择测试环境");
    return;
  }
  showIssueDialog.value = true;
};

const handleRepositoryDialogClose = () => {
  repositoryFormRef.value?.resetFields();
  repositoryForm.value = {
    name: "",
    path: "",
    namespace_path: "",
    description: "",
    public: 0,
    readme: 1,
  };
  showRepositoryDialog.value = false;
};

const handleIssueDialogClose = () => {
  issueFormRef.value?.resetFields();
  issueForm.value = {
    title: "",
    issue_type_id: null,
    project_id: null,
    priority: 0,
    assignee_id: 0,
  };
  showIssueDialog.value = false;
};

const handleConfirmCreateRepository = async () => {
  if (!repositoryFormRef.value) return;

  try {
    await repositoryFormRef.value.validate();
  } catch (error) {
    return;
  }

  try {
    executing.value = true;

    // 构建请求数据
    const projectData = {
      project: {
        name: repositoryForm.value.name,
        description: repositoryForm.value.description || "",
        path: repositoryForm.value.path,
        namespace_path: repositoryForm.value.namespace_path,
        outsourced: 0,
        import_url: "",
        program_ids: "",
        member_ids: "",
        group_ids: "",
        public: repositoryForm.value.public,
        template_id: 0,
        quota_size: null,
        size_limit_enabled: false,
      },
      import_program_users: 0,
      readme: repositoryForm.value.readme,
      issue_template: 0,
      pull_request_template: 0,
      user_sync_code: "",
      password_sync_code: "",
      model: "1",
      custom_branches: {
        tag: "",
      },
      template_apply_scope: "default",
    };

    const result = await store.createRepository({
      environment_id: selectedEnvironmentId.value,
      project_data: projectData,
    });

    executionResult.value = result;
    showRepositoryDialog.value = false;
    showResultDialog.value = true;
    ElMessage.success("创建成功");
  } catch (error) {
    ElMessage.error(error.message || "创建失败");
  } finally {
    executing.value = false;
  }
};

const handleConfirmCreateIssue = async () => {
  if (!issueFormRef.value) return;

  try {
    await issueFormRef.value.validate();
  } catch (error) {
    return;
  }

  try {
    executing.value = true;

    // 构建请求数据
    const issueData = {
      title: issueForm.value.title,
      priority: issueForm.value.priority,
      description_type: "json",
      issue_type_id: issueForm.value.issue_type_id,
      project_id: issueForm.value.project_id,
      security_hole: 0,
      page_source: "企业",
      description_json: JSON.stringify({
        type: "doc",
        content: [
          {
            type: "paragraph",
            attrs: {
              indent: 0,
              textAlign: "left",
            },
          },
        ],
      }),
      assignee_id: issueForm.value.assignee_id,
      extra_fields: [],
    };

    const result = await store.createIssue({
      environment_id: selectedEnvironmentId.value,
      issue_data: issueData,
    });

    executionResult.value = result;
    showIssueDialog.value = false;
    showResultDialog.value = true;
    ElMessage.success("创建成功");
  } catch (error) {
    ElMessage.error(error.message || "创建失败");
  } finally {
    executing.value = false;
  }
};

const formatJson = (obj) => {
  if (!obj) return "-";
  try {
    return JSON.stringify(obj, null, 2);
  } catch (e) {
    return String(obj);
  }
};

onMounted(async () => {
  // 获取测试环境列表
  try {
    await testEnvironmentStore.fetchTestEnvironments({ page: 1, pageSize: 100 });
    environments.value = testEnvironmentStore.testEnvironments || [];

    // 默认选择 premium_k8s 环境
    const premiumK8sEnv = environments.value.find((env) => env.env_name === "premium_k8s");
    if (premiumK8sEnv) {
      selectedEnvironmentId.value = premiumK8sEnv.id;
      handleEnvironmentChange();
    }
  } catch (error) {
    ElMessage.error("获取测试环境列表失败");
  }
});
</script>

<style scoped>
.common-list-container {
  padding: 0 !important;
}

.common-header-bar {
  margin-top: 20px;
  padding: 0 20px;
}

.search-form-inline {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  overflow-x: auto;
  overflow-y: hidden;
  white-space: nowrap;
}

.search-form-inline :deep(.el-form-item) {
  flex-shrink: 0;
  margin-right: 16px;
  margin-bottom: 0;
  white-space: nowrap;
}

.search-form-inline :deep(.el-form-item__label) {
  white-space: nowrap;
  flex-shrink: 0;
}

.search-form-inline :deep(.el-form-item__content) {
  flex-shrink: 0;
}

.empty-tip {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60px 0;
  flex: 1;
}

.business-buttons-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
  flex: 1;
}

.business-buttons-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: center;
}

.business-button {
  width: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.result-json {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  max-height: 400px;
  font-size: 12px;
  line-height: 1.5;
}

code {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: "Courier New", monospace;
  color: #e6a23c;
}
</style>
