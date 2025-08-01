<template>
  <div class="common-list-container">
    <div class="common-header-bar">
      <div class="common-action-bar">
        <el-button type="primary" @click="refresh" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <span v-if="loading && metrics.length === 0" class="loading-tip">正在请求接口，请耐心等待...</span>
      </div>
    </div>

    <div class="cards-grid">
      <!-- 首次进入时的局部骨架屏加载 -->
      <template v-if="loading && metrics.length === 0">
        <el-card v-for="n in 4" :key="`skeleton-${n}`" class="server-card">
          <el-skeleton :rows="5" animated />
        </el-card>
      </template>

      <!-- 加载完成后的服务器资源卡片 -->
      <el-card v-for="item in metrics" :key="item.server_id" class="server-card">
        <template #header>
          <div class="card-header">
            <div class="server-title">
              <span class="name">{{ item.server_name }}</span>
              <span class="host">{{ item.host }}</span>
            </div>
            <div class="header-right">
              <el-tag size="small" :type="statusTagType(item.status)">
                {{ statusText(item.status) }}
              </el-tag>
              <el-tag size="small" style="margin-left: 8px" type="info">ID: {{ item.server_id }}</el-tag>
            </div>
          </div>
        </template>

        <div class="metrics metrics-circle">
          <div class="metric-circle">
            <el-progress type="dashboard" :percentage="safePct(item.cpu_usage)" :status="circleStatus(item.cpu_usage)" :width="110" />
            <div class="metric-title">CPU</div>
            <div class="metric-value" :class="usageClass(item.cpu_usage)">{{ formatPercent(item.cpu_usage) }}</div>
          </div>
          <div class="metric-circle">
            <el-progress type="dashboard" :percentage="safePct(item.memory_usage)" :status="circleStatus(item.memory_usage)" :width="110" />
            <div class="metric-title">内存</div>
            <div class="metric-value" :class="usageClass(item.memory_usage)">{{ formatPercent(item.memory_usage) }}</div>
          </div>
          <div class="metric-circle">
            <el-progress type="dashboard" :percentage="safePct(item.disk_usage)" :status="circleStatus(item.disk_usage)" :width="110" />
            <div class="metric-title">磁盘</div>
            <div class="metric-value" :class="usageClass(item.disk_usage)">{{ formatPercent(item.disk_usage) }}</div>
          </div>
        </div>

        <div class="extras">
          <div class="extra-item" v-if="item.load_average">
            <span class="extra-label">负载</span>
            <span class="extra-value load-badges">
              <el-tag size="small" :type="loadTagType(item.load_average['1min'])">1m: {{ formatLoad(item.load_average['1min']) }}</el-tag>
              <el-tag size="small" :type="loadTagType(item.load_average['5min'])">5m: {{ formatLoad(item.load_average['5min']) }}</el-tag>
              <el-tag size="small" :type="loadTagType(item.load_average['15min'])">15m: {{ formatLoad(item.load_average['15min']) }}</el-tag>
            </span>
          </div>
          <div class="extra-item" v-if="item.uptime">
            <span class="extra-label">运行时长</span>
            <span class="extra-value">{{ item.uptime }}</span>
          </div>
        </div>
      </el-card>
    </div>

    <el-empty v-if="!loading && metrics.length === 0" description="暂无服务器数据" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { linuxInfoService } from '@/services/tool/linuxInfoService'

const loading = ref(false)
const metrics = ref([])

const refresh = async () => {
  loading.value = true
  try {
    const res = await linuxInfoService.getAllServerMetrics()
    if (res.data && res.data.success) {
      metrics.value = res.data.data || []
    } else {
      throw new Error(res.data?.error || '获取指标失败')
    }
  } catch (e) {
    ElMessage.error('获取服务器指标失败')
  } finally {
    loading.value = false
  }
}

const safePct = (v) => {
  if (typeof v !== 'number' || isNaN(v)) return 0
  return Math.max(0, Math.min(100, v))
}

const formatPercent = (v) => {
  return typeof v === 'number' && !isNaN(v) ? `${v}%` : '-'
}

const usageClass = (v) => {
  if (typeof v !== 'number') return 'usage-unknown'
  if (v >= 80) return 'usage-high'
  if (v >= 60) return 'usage-medium'
  return 'usage-low'
}

const circleStatus = (v) => {
  if (typeof v !== 'number' || isNaN(v)) return undefined
  if (v >= 80) return 'exception'
  if (v >= 60) return 'warning'
  return 'success'
}

// 负载徽标: <0.7 绿色, <1.0 黄色, >=1.0 红色
const loadTagType = (v) => {
  if (typeof v !== 'number' || isNaN(v)) return 'info'
  if (v >= 1.0) return 'danger'
  if (v >= 0.7) return 'warning'
  return 'success'
}

const formatLoad = (v) => {
  if (typeof v !== 'number' || isNaN(v)) return '-'
  return Number(v).toFixed(2)
}

const statusTagType = (status) => {
  switch (status) {
    case 'healthy':
      return 'success'
    case 'warning':
      return 'warning'
    case 'critical':
      return 'danger'
    default:
      return 'info'
  }
}

const statusText = (status) => {
  switch (status) {
    case 'healthy':
      return '健康'
    case 'warning':
      return '警告'
    case 'critical':
      return '告警'
    default:
      return '未知'
  }
}

onMounted(refresh)
</script>

<style scoped>
.page-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}
.loading-tip {
  margin-left: 12px;
  color: #909399;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}
.server-card {
  transition: all 0.3s;
}
.server-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-right {
  display: flex;
  align-items: center;
}
.server-title .name {
  font-weight: 600;
  margin-right: 8px;
}
.server-title .host {
  color: #909399;
}
.metrics {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}
.metrics-circle {
  grid-template-columns: repeat(3, 1fr);
  align-items: center;
}
.metric-circle {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.metric-title {
  margin-top: 6px;
  color: #6b7280;
  font-size: 13px;
}
.metric-value {
  font-weight: 600;
  margin-top: 2px;
}
.metric .label {
  color: #6b7280;
  font-size: 14px;
}
.metric .value {
  font-weight: 600;
  margin: 6px 0;
}
.usage-low {
  color: #52c41a;
}
.usage-medium {
  color: #faad14;
  font-weight: 600;
}
.usage-high {
  color: #ff4d4f;
  font-weight: 600;
}
.usage-unknown {
  color: #909399;
}
.extras {
  margin-top: 10px;
  font-size: 12px;
  color: #606266;
}
.extra-item {
  display: flex;
  justify-content: space-between;
}
.extra-label {
  color: #909399;
}
.load-badges > .el-tag {
  margin-right: 6px;
}
</style>
