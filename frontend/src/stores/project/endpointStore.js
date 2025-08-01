import { defineStore } from "pinia";
import { endpointService } from "@/services/project/endpointService";

export const useEndpointStore = defineStore("endpoint", {
  state: () => ({
    // 接口分类数据
    categories: {},

    // 所有接口列表
    endpoints: [],

    // 当前选中的接口
    currentEndpoint: null,

    // 当前接口的参数列表
    endpointParameters: [],

    // 测试结果
    testResult: null,

    // 分页信息
    pagination: {
      currentPage: 1,
      pageSize: 20,
      total: 0,
      totalPages: 1,
    },

    // 加载状态
    loading: false,

    // 错误信息
    error: null,

    // 搜索关键词
    searchKeyword: "",

    // 统计信息
    stats: null,
  }),

  getters: {
    /**
     * 获取树形结构数据
     */
    treeData: (state) => {
      const tree = [];

      // 确保 categories 是对象且包含有效数据
      if (!state.categories || typeof state.categories !== "object") {
        return tree;
      }

      Object.entries(state.categories).forEach(([category, endpoints]) => {
        // 确保 endpoints 是数组
        const endpointList = Array.isArray(endpoints) ? endpoints : [];

        tree.push({
          id: `category-${category}`,
          label: category,
          type: "category",
          children: endpointList.map((endpoint) => ({
            id: endpoint.id,
            label: endpoint.path,
            path: endpoint.path,
            method: endpoint.method,
            summary: endpoint.summary || "",
            description: endpoint.description || "",
            parameters_count: endpoint.parameters_count || 0,
            type: "endpoint",
          })),
        });
      });

      return tree;
    },

    /**
     * 过滤后的树形数据（根据搜索关键词）
     */
    filteredTreeData: (state) => {
      const treeData = state.treeData;

      if (!state.searchKeyword.trim()) {
        return treeData;
      }

      const keyword = state.searchKeyword.toLowerCase().trim();
      const filteredData = [];

      // 在 store 中确保数据结构处理正确
      const processendpointServiceData = (data) => {
        // 假设 data 是 Gitee endpointService 返回的原始数据
        // 转换为前端需要的树形结构
        const categories = [];

        // 遍历 paths
        Object.entries(data.paths || {}).forEach(([path, methods]) => {
          Object.entries(methods).forEach(([method, operation]) => {
            // 根据 tags 分类
            const tag = operation.tags?.[0] || "默认分类";
            // ... 构建树形数据
          });
        });

        return categories;
      };

      treeData.forEach((category) => {
        // 确保 category.children 是数组
        const children = Array.isArray(category.children)
          ? category.children
          : [];
        const filteredChildren = children.filter((endpoint) => {
          if (!endpoint) return false;

          return (
            (endpoint.path && endpoint.path.toLowerCase().includes(keyword)) ||
            (endpoint.summary &&
              endpoint.summary.toLowerCase().includes(keyword)) ||
            (endpoint.description &&
              endpoint.description.toLowerCase().includes(keyword)) ||
            (endpoint.method && endpoint.method.toLowerCase().includes(keyword))
          );
        });

        if (filteredChildren.length > 0) {
          filteredData.push({
            ...category,
            children: filteredChildren,
          });
        }
      });

      return filteredData;
    },

    /**
     * 当前选中的接口详情（包含参数）
     */
    selectedEndpointDetail: (state) => {
      if (!state.currentEndpoint) {
        return null;
      }

      return {
        ...state.currentEndpoint,
        parameters: state.endpointParameters,
      };
    },

    /**
     * 按参数类型分组的参数
     */
    groupedParameters: (state) => {
      const groups = {};

      // 确保 endpointParameters 是数组
      const parameters = Array.isArray(state.endpointParameters)
        ? state.endpointParameters
        : [];

      parameters.forEach((param) => {
        if (param && param.param_type) {
          if (!groups[param.param_type]) {
            groups[param.param_type] = [];
          }
          groups[param.param_type].push(param);
        }
      });

      return groups;
    },
  },

  actions: {
    /**
     * 刷新endpointService文档（从Gitee获取最新文档）
     */
    async refreshApiDocs() {
      this.loading = true;
      this.error = null;
      try {
        const response = await endpointService.refreshApiDocs();

        // 刷新后重新加载数据
        await this.fetchEndpointsByCategories();

        return response;
      } catch (error) {
        this.error = error.message || "刷新endpointService文档失败";
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * 获取接口分类数据
     */
    async fetchEndpointsByCategories() {
      this.loading = true;
      this.error = null;
      try {
        const response = await endpointService.getEndpointsByCategories();

        if (response && response.data.code === 0) {
          this.categories = response.data.data || {};
          console.log("✅ 接口分类数据:", this.categories);
          return this.categories;
        } else {
          throw new Error(response?.message || "获取接口分类数据失败");
        }
      } catch (error) {
        console.error("❌ 获取接口分类数据失败:", error);
        this.error = error.message || "获取接口分类数据失败";
        this.categories = {};
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * 分页获取接口列表
     */
    async fetchEndpoints(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const response = await endpointService.getEndpoints(params);

        if (response && response.code === 0) {
          this.endpoints = Array.isArray(response.data) ? response.data : [];

          this.pagination = {
            currentPage: params.page || this.pagination.currentPage,
            pageSize: params.pageSize || this.pagination.pageSize,
            total: response.total || this.endpoints.length,
            totalPages: response.totalPages || 1,
          };

          return this.endpoints;
        } else {
          throw new Error(response?.message || "获取接口列表失败");
        }
      } catch (error) {
        this.error = error.message || "获取接口列表失败";
        this.endpoints = [];
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * 获取接口详情
     */
    async fetchEndpointDetail(id) {
      this.loading = true;
      this.error = null;
      try {
        const response = await endpointService.getEndpointDetail(id);

        // 后端返回的数据结构: { code: 0, message: 'success', data: { endpoint: {...}, parameters: [...] } }
        if (response && response.data.code === 0 && response.data.data) {
          console.log("✅ 接口详情:", response.data.data);
          this.currentEndpoint = response.data.data.endpoint || null;
          this.endpointParameters = Array.isArray(response.data.data.parameters)
            ? response.data.data.parameters
            : [];
          console.log("✅ 接口详情:", this.currentEndpoint);
          return response.data;
        } else {
          throw new Error(response?.message || "接口详情数据格式错误");
        }
      } catch (error) {
        this.error = error.message || "获取接口详情失败";
        this.currentEndpoint = null;
        this.endpointParameters = [];
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * 选择接口（如果已选中则直接返回，否则获取详情）
     */
    async selectEndpoint(id) {
      console.log(id);
      if (
        this.currentEndpoint?.id === id &&
        this.endpointParameters.length > 0
      ) {
        return this.selectedEndpointDetail;
      }

      return await this.fetchEndpointDetail(id);
    },

    /**
     * 创建新接口
     */
    async createEndpoint(endpointData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await endpointService.createEndpoint(endpointData);

        if (response && response.code === 0) {
          // 创建成功后重新加载数据
          await this.fetchEndpointsByCategories();
          return response.data;
        } else {
          throw new Error(response?.message || "创建接口失败");
        }
      } catch (error) {
        this.error = error.message || "创建接口失败";
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * 更新接口
     */
    async updateEndpoint(id, endpointData) {
      this.loading = true;
      this.error = null;
      try {
        const response = await endpointService.updateEndpoint(id, endpointData);

        if (response && response.code === 0) {
          this.currentEndpoint = response.data;
          // 更新成功后重新加载数据
          await this.fetchEndpointsByCategories();
          return response.data;
        } else {
          throw new Error(response?.message || "更新接口失败");
        }
      } catch (error) {
        this.error = error.message || "更新接口失败";
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * 删除接口
     */
    async deleteEndpoint(id) {
      this.loading = true;
      this.error = null;
      try {
        const response = await endpointService.deleteEndpoint(id);

        if (response && response.code === 0) {
          // 如果删除的是当前选中的接口，清空选中状态
          if (this.currentEndpoint?.id === id) {
            this.currentEndpoint = null;
            this.endpointParameters = [];
          }

          // 删除成功后重新加载数据
          await this.fetchEndpointsByCategories();
        } else {
          throw new Error(response?.message || "删除接口失败");
        }
      } catch (error) {
        this.error = error.message || "删除接口失败";
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * 获取接口参数列表
     */
    // 在 endpointServiceStore.js 中修改 fetchEndpointParameters 方法
    async fetchEndpointParameters(endpointId) {
      this.loading = true;
      this.error = null;
      try {
        console.log("🟡 Store: 获取参数，接口ID:", endpointId);

        // 先清空之前的参数
        this.endpointParameters = [];

        const response = await endpointService.getEndpointParameters(
          endpointId
        );
        console.log("🔵 Store: 原始响应:", response);

        if (response && response.data.code === 0) {
          this.endpointParameters = Array.isArray(response.data.data)
            ? response.data.data
            : [];
          console.log(
            "🟢 Store: 参数获取成功，数量:",
            this.endpointParameters.length
          );
          return this.endpointParameters;
        } else {
          throw new Error(response?.message || "获取接口参数失败");
        }
      } catch (error) {
        console.error("❌ Store: 获取参数失败:", error);
        this.error = error.message || "获取接口参数失败";
        this.endpointParameters = [];
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * 测试接口
     */
    async testEndpoint(endpointId, testData = {}) {
      this.loading = true;
      this.error = null;
      try {
        const response = await endpointService.testEndpoint(
          endpointId,
          testData
        );

        if (response && response.code === 0) {
          this.testResult = response.data;
          return response.data;
        } else {
          throw new Error(response?.message || "测试接口失败");
        }
      } catch (error) {
        this.error = error.message || "测试接口失败";
        throw error;
      } finally {
        this.loading = false;
      }
    },

    /**
     * 设置搜索关键词
     */
    setSearchKeyword(keyword) {
      this.searchKeyword = keyword;
    },

    /**
     * 清空测试结果
     */
    clearTestResult() {
      this.testResult = null;
    },

    /**
     * 重置当前选中的接口
     */
    resetCurrentEndpoint() {
      this.currentEndpoint = null;
      this.endpointParameters = [];
      this.testResult = null;
    },

    /**
     * 清除错误信息
     */
    clearError() {
      this.error = null;
    },
  },
});
