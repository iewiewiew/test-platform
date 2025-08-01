<template>
  <div class="common-list-container">
    <div class="common-header-bar">
      <div class="common-search-bar">
        <el-form :inline="true" :model="searchForm" class="demo-form-inline">
          <el-form-item label="报告名称">
            <el-input v-model="searchForm.search" placeholder="请输入报告名称" clearable @input="handleInputSearch"/>
          </el-form-item>
          <el-form-item>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

    </div>

    <el-table 
      :data="tableData" 
      style="width: 100%" 
      v-loading="store.loading"
      empty-text="暂无数据"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="execution_component" label="执行组件" width="100" show-overflow-tooltip />
      <el-table-column prop="execution_module" label="执行模块" width="100" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.execution_module || '所有模块' }}
        </template>
      </el-table-column>
      <el-table-column prop="execution_environment" label="执行环境" width="120" show-overflow-tooltip />
      <el-table-column prop="report_name" label="报告名称" width="150" show-overflow-tooltip />
      <el-table-column prop="test_file_name" label="测试文件名称" width="150" show-overflow-tooltip></el-table-column>
      <el-table-column prop="success_rate" label="成功率" width="100">
        <template #default="{ row }">
          <el-tag :type="row.success_rate >= 100 ? 'success' : row.success_rate >= 80 ? 'warning' : 'danger'">
            {{ row.success_rate ? row.success_rate.toFixed(2) + '%' : '0.00%' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="total_tests" label="总测试数" width="80" />
      <el-table-column prop="passed_tests" label="通过" width="80">
        <template #default="{ row }">
          <el-tag type="success">{{ row.passed_tests }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="failed_tests" label="失败" width="80">
        <template #default="{ row }">
          <el-tag type="danger">{{ row.failed_tests }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="skipped_tests" label="跳过" width="80">
        <template #default="{ row }">
          <el-tag type="warning">{{ row.skipped_tests }}</el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="duration" label="执行时长(秒)" width="120">
        <template #default="{ row }">
          {{ row.duration ? row.duration.toFixed(2) : '0.00' }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag 
            :type="row.status === 'success' ? 'success' : row.status === 'pending' ? 'info' : 'danger'"
          >
            {{ row.status === 'success' ? '成功' : row.status === 'pending' ? '待解析' : '失败' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="creator_name" label="创建人" width="120" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.creator_name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160" :formatter="formatDate"/>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="scope">
          <el-button 
            size="small" 
            type="primary" 
            @click="handleParseReport(scope.row)"
            :loading="parsingReportId === scope.row.id"
          >
            {{ scope.row.status === 'pending' ? '解析' : '重新解析' }}
          </el-button>
          <el-button 
            size="small" 
            type="success" 
            @click="viewAllureReport(scope.row)"
          >
            查看Allure报告
          </el-button>
          <el-button size="small" type="danger" @click="confirmDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="store.pagination.currentPage"
        v-model:page-size="store.pagination.pageSize"
        :total="store.pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        :background="true"
        layout="total, sizes, prev, pager, next, jumper"
        @update:current-page="handlePageChange"
        @update:page-size="handleSizeChange"
      />
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useTestReportStore } from '@/stores/test/testReportStore'
import { testReportService } from '@/services/test/testReportService'
import { formatDateTime } from '@/utils/date'
import apiClient from '@/utils/request'

const store = useTestReportStore()

const searchForm = ref({
  search: ''
})

const parsingReportId = ref(null)

const tableData = computed(() => {
  return Array.isArray(store.testReports) ? store.testReports : []
})

const formatDate = (row, column, cellValue) => {
  return cellValue ? formatDateTime(cellValue) : '-'
}

let searchTimer = null

const handleInputSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    handleSearch()
  }, 500)
}

const handleSearch = async () => {
  try {
    await store.fetchTestReports({
      page: 1,
      search: searchForm.value.search.trim()
    })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  }
}

const resetSearch = async () => {
  searchForm.value = { search: '' }
  try {
    await store.fetchTestReports({ page: 1 })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  }
}


// 解析测试报告
const handleParseReport = async (row) => {
  try {
    parsingReportId.value = row.id
    await store.parseTestReport(row.id)
    ElMessage.success('解析成功')
    // 刷新列表以显示更新后的数据
    await store.fetchTestReports({
      page: store.pagination.currentPage,
      pageSize: store.pagination.pageSize,
      search: searchForm.value.search.trim()
    })
  } catch (error) {
    ElMessage.error(store.error || '解析失败')
  } finally {
    parsingReportId.value = null
  }
}

// 查看Allure测试报告：在新窗口打开Allure原生HTML页面
const viewAllureReport = async (row) => {
  try {
    const response = await testReportService.getAllureReportUrl(row.id)
    if (response.data && response.data.url) {
      // 构建完整的URL
      // 后端返回的URL格式：/api/test-reports/{report_id}/allure/index.html
      const apiBaseUrl = apiClient.defaults.baseURL || '/api'
      
      // 从baseURL中提取origin（协议+主机+端口）
      let origin = window.location.origin
      if (apiBaseUrl.startsWith('http')) {
        // 开发环境：http://localhost:5001/api -> http://localhost:5001
        origin = apiBaseUrl.replace(/\/api\/?$/, '')
      }
      // 生产环境：/api -> 使用 window.location.origin
      
      const allureUrl = `${origin}${response.data.url}`
      
      console.log('打开Allure报告URL:', allureUrl)
      // 在新窗口打开Allure报告
      window.open(allureUrl, '_blank')
    } else {
      ElMessage.warning('Allure报告不存在')
    }
  } catch (error) {
    ElMessage.error('获取Allure报告失败')
    console.error('获取Allure报告失败:', error)
  }
}


const confirmDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除测试报告 "${row.report_name}" 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      await store.deleteTestReport(row.id)
      ElMessage.success('删除成功')
    })
    .catch(() => {})
}

const handlePageChange = async (newPage) => {
  try {
    await store.fetchTestReports({
      page: newPage,
      search: searchForm.value.search.trim()
    })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  }
}

const handleSizeChange = async (newSize) => {
  try {
    await store.fetchTestReports({
      page: 1,
      pageSize: newSize,
      search: searchForm.value.search.trim()
    })
  } catch (error) {
    if (store.error) {
      ElMessage.error(store.error)
    }
  }
}

onMounted(async () => {
  await store.fetchTestReports()
})
</script>

<style scoped>
/* 使用公共样式，移除重复定义 */
/* 页面特定样式 */

</style>

