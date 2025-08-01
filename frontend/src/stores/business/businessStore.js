import { defineStore } from "pinia";
import { ref } from "vue";
import businessService from "@/services/business/businessService";
import { ElMessage } from "element-plus";

export const useBusinessStore = defineStore("business", () => {
  const loading = ref(false);
  const error = ref(null);
  const executionResult = ref(null);

  /**
   * 新建仓库
   */
  const createRepository = async ({ environment_id, project_data }) => {
    try {
      loading.value = true;
      error.value = null;
      const result = await businessService.createRepository({
        environment_id,
        project_data,
      });
      
      if (result.data.code === 0) {
        executionResult.value = result.data.data;
        return result.data.data;
      } else {
        throw new Error(result.data.message || "执行失败");
      }
    } catch (err) {
      error.value = err.response?.data?.message || err.message || "执行失败";
      ElMessage.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 新建工作项
   */
  const createIssue = async ({ environment_id, issue_data }) => {
    try {
      loading.value = true;
      error.value = null;
      const result = await businessService.createIssue({
        environment_id,
        issue_data,
      });
      
      if (result.data.code === 0) {
        executionResult.value = result.data.data;
        return result.data.data;
      } else {
        throw new Error(result.data.message || "执行失败");
      }
    } catch (err) {
      error.value = err.response?.data?.message || err.message || "执行失败";
      ElMessage.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 清空执行结果
   */
  const clearExecutionResult = () => {
    executionResult.value = null;
  };

  return {
    loading,
    error,
    executionResult,
    createRepository,
    createIssue,
    clearExecutionResult,
  };
});

