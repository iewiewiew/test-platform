<template>
  <div class="common-list-container">
    <div class="common-header-bar">
      <div class="common-search-bar">
        <el-form :inline="true" :model="searchForm" class="demo-form-inline">
          <el-form-item label="文件名">
            <el-input v-model="searchForm.filename" placeholder="请输入文件名" clearable @input="handleInputSearch" />
          </el-form-item>
          <el-form-item>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="common-action-bar">
        <el-button type="danger" :disabled="selectedIds.size === 0" @click="handleBatchDelete" :loading="batchDeleteLoading">批量删除({{ selectedIds.size }})</el-button>
        <el-upload
          :action="uploadAction"
          :headers="uploadHeaders"
          :data="uploadData"
          :before-upload="beforeUpload"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :show-file-list="false"
          accept="image/*"
          multiple
        >
          <el-button type="primary">上传图片</el-button>
        </el-upload>
      </div>
    </div>

    <!-- 图片列表表格 -->
    <el-table v-loading="store.loading" :data="tableData" style="width: 100%" @selection-change="handleSelectionChange" row-key="id" empty-text="暂无图片">
      <el-table-column type="selection" width="55" />
      <el-table-column label="缩略图" width="120" align="center">
        <template #default="{ row }">
          <div class="thumbnail-wrapper">
            <img :src="getImageUrl(row.url)" :alt="row.original_filename" class="thumbnail-image" @error="handleImageError" @click="previewImage(row)" />
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="original_filename" label="文件名" min-width="200" show-overflow-tooltip>
        
      </el-table-column>
      <el-table-column label="尺寸" width="120" align="center">
        <template #default="{ row }">
          <span v-if="row.width && row.height">{{ row.width }} × {{ row.height }}</span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="大小" width="100" align="center">
        <template #default="{ row }">
          {{ formatFileSize(row.file_size) }}
        </template>
      </el-table-column>
      <el-table-column prop="url" label="访问地址" min-width="250">
        <template #default="{ row }">
          <div class="url-cell">
            <el-input :value="getImageUrl(row.url)" readonly size="small" class="url-input">
              <template #append>
                <el-button @click="copyImageUrl(row)" size="small">复制</el-button>
              </template>
            </el-input>
            <el-button text type="primary" size="small" @click="openImageInNewTab(row)" style="margin-left: 8px">打开</el-button>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="mime_type" label="类型" width="120" align="center" />
      <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.description">{{ row.description }}</span>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>

      <el-table-column prop="created_at" label="上传时间" width="180" align="center">
        <template #default="{ row }">
          {{ formatDateTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right" align="center">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="editImage(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="confirmDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
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

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑图片信息" width="500px">
      <el-form ref="editFormRef" :model="editForm" label-width="80px">
        <el-form-item label="更新图片">
          <el-upload :auto-upload="false" :show-file-list="true" :limit="1" accept="image/*" :on-change="handleFileChange" :on-remove="handleFileRemove" :before-upload="beforeUpload">
            <el-button type="primary">选择图片</el-button>
            <template #tip>
              <div class="el-upload__tip">选择新图片将替换当前图片，但保持 URL 不变</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" placeholder="请输入图片描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdate" :loading="updateLoading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 预览对话框 -->
    <el-dialog v-model="showPreviewDialog" title="图片预览" width="80%" :before-close="closePreview">
      <div v-if="previewImageData" class="preview-container">
        <img :src="getImageUrl(previewImageData.url)" :alt="previewImageData.original_filename" class="preview-image" />
        <div class="preview-info">
          <p>
            <strong>文件名：</strong>
            {{ previewImageData.original_filename }}
          </p>
          <p v-if="previewImageData.width && previewImageData.height">
            <strong>尺寸：</strong>
            {{ previewImageData.width }} × {{ previewImageData.height }} 像素
          </p>
          <p>
            <strong>大小：</strong>
            {{ formatFileSize(previewImageData.file_size) }}
          </p>
          <p>
            <strong>类型：</strong>
            {{ previewImageData.mime_type }}
          </p>
          <p v-if="previewImageData.description">
            <strong>描述：</strong>
            {{ previewImageData.description }}
          </p>
          <p>
            <strong>URL：</strong>
            <el-input :value="getImageUrl(previewImageData.url)" readonly style="margin-top: 8px">
              <template #append>
                <el-button @click="copyUrl">复制</el-button>
              </template>
            </el-input>
          </p>
          <p style="margin-top: 12px">
            <el-button type="primary" @click="openImageInNewTab(previewImageData)">在新标签页打开</el-button>
          </p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useImageStore } from '@/stores/tool/imageStore'
import { formatDateTime } from '@/utils/date'

const store = useImageStore()

// 搜索表单
const searchForm = ref({
  filename: ''
})

// 对话框状态
const showEditDialog = ref(false)
const showPreviewDialog = ref(false)
const editFormRef = ref(null)
const updateLoading = ref(false)
const batchDeleteLoading = ref(false)

// 编辑表单
const editForm = ref({
  id: null,
  description: '',
  file: null
})

// 预览图片数据
const previewImageData = ref(null)

// 选中状态
const selectedIds = ref(new Set())

// 防抖计时器
let searchTimer = null

// 计算属性
const tableData = computed(() => {
  return Array.isArray(store.images) ? store.images : []
})

// 上传配置
const uploadAction = computed(() => {
  const baseURL = process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:5001/api'
  return `${baseURL}/images`
})

const uploadHeaders = computed(() => {
  const token = localStorage.getItem('token')
  return {
    Authorization: token ? `Bearer ${token}` : ''
  }
})

const uploadData = computed(() => ({
  description: ''
}))

// 工具函数
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const getImageUrl = (url) => {
  if (!url) return ''
  // 如果已经是完整URL，直接返回
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  // 如果是相对路径，构建完整URL
  const baseURL = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:5001'
  // 确保URL以 / 开头
  const path = url.startsWith('/') ? url : `/${url}`
  return `${baseURL}${path}`
}

// 搜索处理
const handleInputSearch = () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    handleSearch()
  }, 500)
}

const handleSearch = async () => {
  try {
    await store.fetchImages({
      page: 1,
      filename: searchForm.value.filename || undefined
    })
  } catch (error) {
    ElMessage.error(error.message || '搜索失败')
  }
}

const resetSearch = async () => {
  searchForm.value = {
    filename: ''
  }
  await handleSearch()
}

// 分页处理
const handlePageChange = async (page) => {
  await store.fetchImages({
    page,
    filename: searchForm.value.filename || undefined
  })
}

const handleSizeChange = async (size) => {
  await store.fetchImages({
    page: 1,
    pageSize: size,
    filename: searchForm.value.filename || undefined
  })
}

// 表格选择处理
const handleSelectionChange = (selection) => {
  selectedIds.value = new Set(selection.map((item) => item.id))
}

// 上传处理
const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

const handleUploadSuccess = async (response) => {
  if (response.success) {
    ElMessage.success('图片上传成功')
    await store.fetchImages({
      page: store.pagination.currentPage,
      filename: searchForm.value.filename || undefined
    })
  } else {
    ElMessage.error(response.message || '上传失败')
  }
}

const handleUploadError = (error) => {
  ElMessage.error('图片上传失败')
  console.error('Upload error:', error)
}

// 编辑处理
const editImage = (image) => {
  editForm.value = {
    id: image.id,
    description: image.description || '',
    file: null
  }
  showEditDialog.value = true
}

const handleFileChange = (file) => {
  // 验证文件
  const isImage = file.raw.type.startsWith('image/')
  const isLt5M = file.raw.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return
  }

  editForm.value.file = file.raw
}

const handleFileRemove = () => {
  editForm.value.file = null
}

const handleUpdate = async () => {
  if (!editForm.value.id) return

  updateLoading.value = true
  try {
    const updateData = {
      description: editForm.value.description
    }

    // 如果选择了新文件，添加到更新数据中
    if (editForm.value.file) {
      updateData.file = editForm.value.file
    }

    await store.updateImage(editForm.value.id, updateData)
    ElMessage.success(editForm.value.file ? '图片文件和信息更新成功（UUID 保持不变）' : '更新成功')
    showEditDialog.value = false
    // 重置表单
    editForm.value.file = null
  } catch (error) {
    ElMessage.error(error.message || '更新失败')
  } finally {
    updateLoading.value = false
  }
}

// 删除处理
const confirmDelete = async (image) => {
  try {
    await ElMessageBox.confirm('确定要删除这张图片吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await store.deleteImage(image.id)
    ElMessage.success('删除成功')
    selectedIds.value.delete(image.id)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const handleBatchDelete = async () => {
  if (selectedIds.value.size === 0) return

  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedIds.value.size} 张图片吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    batchDeleteLoading.value = true
    await store.batchDeleteImages(Array.from(selectedIds.value))
    ElMessage.success('批量删除成功')
    selectedIds.value.clear()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '批量删除失败')
    }
  } finally {
    batchDeleteLoading.value = false
  }
}

// 预览处理
const previewImage = (image) => {
  previewImageData.value = image
  showPreviewDialog.value = true
}

const closePreview = () => {
  showPreviewDialog.value = false
  previewImageData.value = null
}

const copyUrl = () => {
  const url = getImageUrl(previewImageData.value.url)
  copyToClipboard(url)
}

const copyImageUrl = (image) => {
  const url = getImageUrl(image.url)
  copyToClipboard(url)
}

const copyToClipboard = (text) => {
  // 检查是否支持 Clipboard API
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard
      .writeText(text)
      .then(() => {
        ElMessage.success('URL已复制到剪贴板')
      })
      .catch(() => {
        // 降级方案
        fallbackCopyToClipboard(text)
      })
  } else {
    // 直接使用降级方案
    fallbackCopyToClipboard(text)
  }
}

const fallbackCopyToClipboard = (text) => {
  const textarea = document.createElement('textarea')
  textarea.value = text
  textarea.style.position = 'fixed'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  textarea.select()
  try {
    document.execCommand('copy')
    ElMessage.success('URL已复制到剪贴板')
  } catch (err) {
    ElMessage.error('复制失败，请手动复制')
  }
  document.body.removeChild(textarea)
}

const openImageInNewTab = (image) => {
  const url = getImageUrl(image.url)
  window.open(url, '_blank')
}

const handleImageError = (event) => {
  event.target.src =
    'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2VlZSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LXNpemU9IjE0IiBmaWxsPSIjOTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+5Zu+54mH5pyq5Yqg6L29PC90ZXh0Pjwvc3ZnPg=='
}

// 初始化
onMounted(async () => {
  await store.fetchImages()
})
</script>

<style scoped>
/* 使用公共样式类 common-list-container、common-header-bar、common-search-bar、common-action-bar */
/* 以下为图床管理页面特定的样式 */

/* 缩略图样式 */
.thumbnail-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100px;
  height: 100px;
  background: #f5f7fa;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
}

.thumbnail-wrapper:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.thumbnail-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

/* 文件名单元格 */
.filename-cell {
  display: flex;
  align-items: center;
}

.filename-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* URL单元格 */
.url-cell {
  display: flex;
  align-items: center;
}

.url-input {
  flex: 1;
}

.text-muted {
  color: #909399;
  font-style: italic;
}

/* 分页样式已在公共样式中定义 */

/* 预览对话框 */
.preview-container {
  display: flex;
  gap: 20px;
  max-height: 70vh;
}

.preview-image {
  max-width: 60%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.preview-info {
  flex: 1;
  font-size: 14px;
  line-height: 1.8;
}

.preview-info p {
  margin-bottom: 12px;
}

.preview-info strong {
  color: #303133;
  margin-right: 8px;
}

/* 表格样式优化 */
:deep(.el-table) {
  border-radius: 4px;
  overflow: hidden;
}

:deep(.el-table th) {
  background-color: #fafafa;
  font-weight: 600;
}

:deep(.el-table td) {
  padding: 12px 0;
}

:deep(.el-table .cell) {
  padding: 0 12px;
}
</style>
