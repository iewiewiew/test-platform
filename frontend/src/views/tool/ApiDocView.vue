<template>
  <div class="common-list-container">
    <div class="layout-container">
      <!-- 左侧目录树 -->
      <div class="tree-panel">
        <ApiTree @endpoint-selected="handleEndpointSelected" />
      </div>

      <!-- 右侧接口详情 -->
      <div class="detail-panel">
        <ApiDetail :endpoint="selectedEndpoint" :loading="detailLoading" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useEndpointStore } from '@/stores/project/endpointStore'
import ApiTree from '@/components/api/ApiTree.vue'
import ApiDetail from '@/components/api/ApiDetail.vue'

const endpointStore = useEndpointStore()
const selectedEndpoint = ref(null)
const detailLoading = ref(false)

const handleEndpointSelected = async (endpointData) => {
  detailLoading.value = true
  try {
    // 直接从点击的数据中获取接口信息，不需要额外请求
    selectedEndpoint.value = endpointData
  } catch (error) {
    console.error('加载接口详情失败:', error)
  } finally {
    detailLoading.value = false
  }
}

// 初始化加载分类数据
onMounted(() => {
  endpointStore.fetchEndpointsByCategories()
})

</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100%;
  max-height: 100%;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden; /* 确保布局容器本身不滚动 */
  min-height: 0; /* 确保flex容器可以正确收缩 */
  align-items: stretch; /* 确保左右面板等高 */
}

.tree-panel {
  width: 280px;
  min-width: 250px;
  max-width: 280px;
  border-right: 1px solid #e4e7ed;
  background: #fff;
  height: 100%;
  /* 限制目录树高度为视口内高度（扣除顶部导航60px与内容内边距约32px）*/
  max-height: calc(100vh - 60px - 32px);
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 让内部的树容器负责滚动 */
  min-height: 0; /* 确保flex子元素可以正确收缩 */
}

.detail-panel {
  flex: 1;
  min-width: 0;
  min-height: 0; /* 确保flex子元素可以正确收缩 */
  background: #fff;
  height: 100%;
  /* 固定右侧请求面板在内容区域内的高度，与左侧保持一致 */
  max-height: calc(100vh - 60px - 32px);
  overflow: hidden; /* 防止面板本身滚动，让内部组件负责滚动 */
  display: flex;
  flex-direction: column;
  position: relative; /* 确保定位上下文 */
}

@media (max-width: 768px) {
  .common-list-container {
    padding: 8px;
  }

  .layout-container {
    flex-direction: column;
    align-items: stretch; /* 确保移动端也等高 */
  }

  .tree-panel {
    width: 100%;
    height: 40%;
    max-height: 40%; /* 限制最大高度 */
    border-right: none;
    border-bottom: 1px solid #e4e7ed;
    flex-shrink: 0; /* 防止被压缩 */
  }

  .detail-panel {
    height: 60%;
    max-height: 60%; /* 限制最大高度 */
    flex-shrink: 0; /* 防止被压缩 */
  }
}
</style>