<template>
  <div class="api-detail">
    <div v-if="!endpoint" class="empty-detail">
      <el-empty description="请选择左侧接口查看详情" :image-size="120" />
    </div>

    <div v-else class="detail-content" v-loading="loading">

      <!-- 接口基本信息 -->
      <div class="api-basic-info">
        <h1 class="api-title">{{ getApiTitle() }}</h1>

        <div class="method-path">
          <el-tag :type="getMethodType(endpoint.method)" effect="dark" class="method-tag">
            {{ endpoint.method }}
          </el-tag>
          <span class="api-path">{{ currentBaseUrl + endpoint.path }}</span>
        </div>

        <!-- 环境选择 -->
        <div class="environment-selector">
          <el-select
            v-model="selectedEnvironmentId"
            placeholder="请选择环境"
            size="default"
            clearable
            @change="handleEnvironmentChange"
            style="width: 300px;"
          >
            <el-option
              v-for="env in environmentOptions"
              :key="env.value"
              :label="env.label"
              :value="env.value"
            >
            </el-option>
          </el-select>
          <el-button
            type="primary"
            :loading="testing"
            @click="handleTest"
            style="margin-left: 16px;"
            :disabled="!selectedEnvironmentId"
          >
            <el-icon><Promotion /></el-icon>
            测试接口
          </el-button>
        </div>
      </div>

      <!-- 请求参数（统一表单） -->
      <div class="parameters-section">
        <h2 class="section-title">
          请求参数
        </h2>

        <div class="parameter-group">
          <div class="body-parameters-table">
            <el-table :data="unifiedParameters" size="small" class="parameter-table" empty-text="无参数">
              <el-table-column prop="name" label="参数名" min-width="200">
                <template #default="{ row }">
                  <span class="param-name">{{ row.name }}</span>
                  <el-tag v-if="row.required" size="small" type="danger" class="required-tag">必填</el-tag>
                  <el-tag v-if="row._source === 'path'" size="small" type="danger" effect="plain" style="margin-left: 6px;">路径</el-tag>
                  <el-tag v-if="row._source === 'query'" size="small" type="primary" effect="plain" style="margin-left: 6px;">查询</el-tag>
                  <el-tag v-if="row._source === 'body'" size="small" type="warning" effect="plain" style="margin-left: 6px;">Body</el-tag>
                </template>
              </el-table-column>

              <el-table-column label="参数值" min-width="240">
                <template #default="{ row }">
                  <!-- 文本输入框 -->
                  <el-input
                    v-if="(row.type === 'string' || !row.type) && !row.enum && row.format !== 'boolean'"
                    v-model="unifiedFormData[row.name]"
                    :placeholder="getPlaceholder(row)"
                    size="small"
                    clearable
                    class="parameter-input"
                  />

                  <!-- 数字输入框 -->
                  <el-input-number
                    v-else-if="row.type === 'integer' || row.type === 'number'"
                    v-model="unifiedFormData[row.name]"
                    :placeholder="getPlaceholder(row)"
                    :min="row.minimum"
                    :max="row.maximum"
                    size="small"
                    controls-position="right"
                    style="width: 100%"
                    class="number-input-left parameter-input"
                  />

                  <!-- 下拉选择框 -->
                  <el-select
                    v-else-if="row.enum && row.enum.length > 0"
                    v-model="unifiedFormData[row.name]"
                    :placeholder="getPlaceholder(row)"
                    size="small"
                    style="width: 100%"
                    clearable
                    class="parameter-input"
                  >
                    <el-option
                      v-for="option in row.enum"
                      :key="option"
                      :label="option"
                      :value="option"
                    />
                  </el-select>

                  <!-- 布尔值选择 -->
                  <el-radio-group
                    v-else-if="row.type === 'boolean' || row.format === 'boolean'"
                    v-model="unifiedFormData[row.name]"
                    size="small"
                    class="parameter-input"
                  >
                    <el-radio :label="true">是</el-radio>
                    <el-radio :label="false">否</el-radio>
                  </el-radio-group>

                  <!-- 默认文本输入框 -->
                  <el-input
                    v-else
                    v-model="unifiedFormData[row.name]"
                    :placeholder="getPlaceholder(row)"
                    size="small"
                    clearable
                    class="parameter-input"
                  />
                </template>
              </el-table-column>

              <el-table-column prop="type" label="类型" width="90">
                <template #default="{ row }">
                  <el-tag size="small" effect="plain">{{ row.type || 'string' }}</el-tag>
                </template>
              </el-table-column>

              <el-table-column prop="description" label="说明" min-width="180">
                <template #default="{ row }">
                  <div class="param-description">
                    <template v-if="row.description">
                      <el-tooltip effect="dark" :content="row.description" placement="top">
                        <span class="desc-ellipsis">{{ row.description }}</span>
                      </el-tooltip>
                    </template>
                    <template v-else>
                      <span>无说明</span>
                    </template>
                    <div v-if="row.format && row.format !== 'boolean'" class="format-hint">格式: {{ row.format }}</div>
                    <div v-if="row.minimum !== undefined || row.maximum !== undefined" class="range-hint">
                      <span v-if="row.minimum !== undefined">最小值: {{ row.minimum }}</span>
                      <span v-if="row.maximum !== undefined">最大值: {{ row.maximum }}</span>
                    </div>
                  </div>
                </template>
              </el-table-column>
            </el-table>

            <div v-if="showJsonPreview && bodyParameterNames.length > 0" class="json-preview">
              <h4>JSON预览</h4>
              <pre class="json-code">{{ JSON.stringify(unifiedBodyJson, null, 2) }}</pre>
            </div>
          </div>
        </div>

        <div v-if="!hasUnifiedParameters" class="no-parameters">
          <el-empty description="此接口无需参数" :image-size="80" />
        </div>
      </div>

      <!-- 响应示例 -->
      <div v-if="hasResponses" class="response-section">
        <h2 class="section-title">
          <el-icon><CircleCheck /></el-icon>
          响应示例
        </h2>
        <div class="response-content">
          <div v-for="(response, code) in getResponses()" :key="code" class="response-item">
            <div class="response-code">
              <el-tag :type="getResponseType(code)" size="small">{{ code }}</el-tag>
              <span class="response-desc">{{ response.description }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 测试结果 -->
      <div v-if="testResult" class="test-result-section">

        <!-- CURL命令 -->
        <div class="test-result-item">
          <h2 class="section-title">
            CURL 命令
          </h2>
          <div class="code-block">
            <pre class="code-content">{{ testResult.request?.curl || '无' }}</pre>
            <el-button
              text
              type="primary"
              size="small"
              @click="copyToClipboard(testResult.request?.curl)"
              class="copy-btn"
            >
              <el-icon><CopyDocument /></el-icon>
              复制
            </el-button>
          </div>
        </div>

        <!-- 请求信息（默认折叠） -->
        <div class="test-result-item">
          <h2 class="section-title">
            请求信息
            <el-button
              text
              type="primary"
              size="small"
              @click="expandRequestInfo = !expandRequestInfo"
              class="toggle-btn"
            >
              {{ expandRequestInfo ? '收起' : '展开' }}
            </el-button>
          </h2>
          <div class="request-info" v-show="expandRequestInfo">
            <div class="info-row">
              <span class="info-label">请求URL:</span>
              <span class="info-value">{{ testResult.request?.url }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">请求方法:</span>
              <el-tag :type="getMethodType(testResult.request?.method)" size="small">
                {{ testResult.request?.method }}
              </el-tag>
            </div>
            <div v-if="testResult.request?.headers" class="info-row">
              <span class="info-label">请求头:</span>
              <div class="code-block">
                <pre class="code-content">{{ JSON.stringify(testResult.request.headers, null, 2) }}</pre>
              </div>
            </div>
            <div v-if="testResult.request?.body" class="info-row">
              <span class="info-label">请求体:</span>
              <div class="code-block">
                <pre class="code-content">{{ JSON.stringify(testResult.request.body, null, 2) }}</pre>
              </div>
            </div>
          </div>
        </div>

        <!-- 响应结果 -->
        <div class="test-result-item">
          <h2 class="section-title">
            响应结果
          </h2>
          <div class="response-info">
            <div class="info-row">
              <span class="info-label">状态码:</span>
              <el-tag
                :type="getResponseStatusType(testResult.response?.status_code)"
                size="small"
              >
                {{ testResult.response?.status_code }}
              </el-tag>
            </div>
            <div v-if="testResult.response?.headers" class="info-row headers-toggle-row">
              <span class="info-label">响应头:</span>
              <el-button
                text
                type="primary"
                size="small"
                @click="expandResponseHeaders = !expandResponseHeaders"
                class="toggle-btn"
              >
                {{ expandResponseHeaders ? '收起' : '展开' }}
              </el-button>
            </div>
            <div v-if="testResult.response?.headers" class="info-row headers-content-row" v-show="expandResponseHeaders">
              <span class="info-label"></span>
              <div class="code-block">
                <pre class="code-content">{{ JSON.stringify(testResult.response.headers, null, 2) }}</pre>
              </div>
            </div>
            <div class="info-row">
              <span class="info-label">响应体:</span>
              <div class="code-block">
                <pre class="code-content">{{ formatResponseData(testResult.response) }}</pre>
                <el-button
                  text
                  type="primary"
                  size="small"
                  @click="copyToClipboard(testResult.response)"
                  class="copy-btn"
                >
                  <el-icon><CopyDocument /></el-icon>
                  复制
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, nextTick } from 'vue'
import { Document, CircleCheck, Promotion, DocumentCopy, CopyDocument, Link } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useEndpointStore } from '@/stores/project/endpointStore'
import { useEnvironmentStore } from '@/stores/project/environmentStore'
import { endpointService } from '@/services/project/endpointService'
import { environmentService } from '@/services/project/environmentService'

const props = defineProps({
  endpoint: Object,
  loading: Boolean
})

const apiStore = useEndpointStore()
const environmentStore = useEnvironmentStore()
const showDebug = ref(false)
const localLoading = ref(false)
const showJsonPreview = ref(true)
const bodyFormData = ref({})
const unifiedFormData = ref({})
const selectedEnvironmentId = ref(null)
const testing = ref(false)
const testResult = ref(null)
const currentBaseUrl = ref('https://example.com')
// 折叠控制（默认折叠）
const expandRequestInfo = ref(false)
const expandResponseHeaders = ref(false)

// 清洗说明字段，去除 [EXTRA_INFO]...[/EXTRA_INFO]
const sanitizeText = (text) => {
  if (!text || typeof text !== 'string') return text || ''
  return text.replace(/\[EXTRA_INFO\][\s\S]*?\[\/EXTRA_INFO\]/g, '').trim()
}

// 参数计算属性 - 移到前面定义
const pathParameters = computed(() => {
  const params = currentParameters.value.filter(p => p.param_type === 'path')
  console.log('📍 路径参数数量:', params.length)
  return params
})

const queryParameters = computed(() => {
  const params = currentParameters.value.filter(p => p.param_type === 'query')
  console.log('📍 查询参数数量:', params.length)
  return params
})

const bodyParameters = computed(() => {
  // 过滤出 body 参数并转换为表单可用的格式
  const bodyParams = currentParameters.value.filter(p => 
    p.param_type === 'formData' || p.param_type === 'body'
  )
  
  // 转换参数格式
  const formattedParams = bodyParams.map(param => {
    // 如果参数有 schema，提取 schema 中的信息
    if (param.schema && typeof param.schema === 'object') {
      return {
        name: param.name,
        type: param.schema.type || 'string',
        required: param.required || false,
        description: param.description || param.schema.description,
        default: param.default || param.schema.default,
        enum: param.enum || param.schema.enum,
        format: param.format || param.schema.format,
        minimum: param.minimum || param.schema.minimum,
        maximum: param.maximum || param.schema.maximum,
        minLength: param.minLength || param.schema.minLength,
        maxLength: param.maxLength || param.schema.maxLength
      }
    }
    
    return {
      name: param.name,
      type: param.type || 'string',
      required: param.required || false,
      description: param.description,
      default: param.default,
      enum: param.enum,
      format: param.format,
      minimum: param.minimum,
      maximum: param.maximum,
      minLength: param.minLength,
      maxLength: param.maxLength
    }
  })
  
  console.log('📍 Body参数:', formattedParams)
  return formattedParams
})

// 统一的参数列表：access_token -> 查询参数 -> 路径参数 -> Body参数
const unifiedParameters = computed(() => {

  const mappedPath = pathParameters.value.map(p => ({
    name: p.name,
    type: p.data_type || p.type || (p.schema && p.schema.type) || 'string',
    required: !!p.required,
    description: sanitizeText(p.description || (p.schema && p.schema.description)),
    enum: p.enum || (p.schema && p.schema.enum),
    format: p.format || (p.schema && p.schema.format),
    minimum: p.minimum || (p.schema && p.schema.minimum),
    maximum: p.maximum || (p.schema && p.schema.maximum),
    default: p.example || p.default || (p.schema && p.schema.default),
    _source: 'path'
  }))

  const mappedQuery = queryParameters.value.map(p => ({
    name: p.name,
    type: p.data_type || p.type || (p.schema && p.schema.type) || 'string',
    required: !!p.required,
    description: sanitizeText(p.description || (p.schema && p.schema.description)),
    enum: p.enum || (p.schema && p.schema.enum),
    format: p.format || (p.schema && p.schema.format),
    minimum: p.minimum || (p.schema && p.schema.minimum),
    maximum: p.maximum || (p.schema && p.schema.maximum),
    default: p.example || p.default || (p.schema && p.schema.default),
    _source: 'query'
  }))

  const mappedBody = bodyParameters.value.map(p => ({
    ...p,
    description: sanitizeText(p.description),
    _source: 'body'
  }))

  const list = [...mappedPath, ...mappedQuery, ...mappedBody]
  return list
})

const bodyParameterNames = computed(() => unifiedParameters.value.filter(p => p._source === 'body').map(p => p.name))
const hasUnifiedParameters = computed(() => unifiedParameters.value.length > 0)

const unifiedBodyJson = computed(() => {
  const json = {}
  bodyParameterNames.value.forEach(name => {
    json[name] = unifiedFormData.value[name]
  })
  return json
})

const headerParameters = computed(() => {
  const params = currentParameters.value.filter(p => p.param_type === 'header')
  console.log('📍 头部参数数量:', params.length)
  return params
})

// 是否有参数的计算属性
const hasPathParameters = computed(() => pathParameters.value.length > 0)
const hasQueryParameters = computed(() => queryParameters.value.length > 0)
const hasBodyParameters = computed(() => bodyParameters.value.length > 0)
const hasHeaderParameters = computed(() => headerParameters.value.length > 0)
const hasParameters = computed(() =>
  hasPathParameters.value ||
  hasQueryParameters.value ||
  hasBodyParameters.value ||
  hasHeaderParameters.value
)

// 直接从 endpoint.id 获取当前接口ID
const currentEndpointId = computed(() => {
  return props.endpoint?.id || null
})

// 修复：简化参数逻辑，直接使用 store 中的参数
const currentParameters = computed(() => {
  console.log('🔍 currentParameters 计算:')
  console.log('  - 当前接口ID:', currentEndpointId.value)
  console.log('  - store 参数数量:', apiStore.endpointParameters.length)
  
  // 如果没有当前接口ID，返回空数组
  if (!currentEndpointId.value) {
    console.log('❌ 没有当前接口ID，返回空数组')
    return []
  }
  
  // 检查 store 中的参数是否属于当前接口
  if (apiStore.endpointParameters.length > 0) {
    const firstParam = apiStore.endpointParameters[0]
    console.log('  - 第一个参数的endpoint_id:', firstParam?.endpoint_id)
    
    if (firstParam && firstParam.endpoint_id === currentEndpointId.value) {
      console.log('✅ 参数匹配，返回参数数量:', apiStore.endpointParameters.length)
      return apiStore.endpointParameters
    } else {
      console.log('❌ 参数不匹配，返回空数组')
      return []
    }
  }
  
  console.log('❌ store中没有参数，返回空数组')
  return []
})

// 监听 endpoint 变化，获取参数
watch(() => props.endpoint, async (newEndpoint, oldEndpoint) => {
  console.log('🔄 endpoint 变化监听:', { 
    oldEndpointId: oldEndpoint?.id, 
    newEndpointId: newEndpoint?.id 
  })
  
  // 切换接口时清空上一个接口的响应内容
  if (oldEndpoint && newEndpoint && oldEndpoint.id !== newEndpoint?.id) {
    testResult.value = null
    expandRequestInfo.value = false
    expandResponseHeaders.value = false
    testing.value = false
  }
  
  if (newEndpoint && newEndpoint.id) {
    await fetchParameters(newEndpoint.id)
    // 重置表单数据
    resetBodyFormData()
    resetUnifiedFormData()
    // 如果已选择环境，切换接口后按环境参数默认填充（静默）
    if (selectedEnvironmentId.value) {
      await handleEnvironmentChange(selectedEnvironmentId.value, { silent: true })
    }
  } else {
    // 如果没有选中接口，也要清空测试结果
    testResult.value = null
    expandRequestInfo.value = false
    expandResponseHeaders.value = false
    testing.value = false
  }
}, { immediate: true })

// 监听 bodyParameters 变化，初始化表单数据
watch(bodyParameters, (newParams) => {
  if (newParams && newParams.length > 0) {
    resetBodyFormData()
    resetUnifiedFormData()
  }
}, { deep: true })

// 重置Body表单数据
const resetBodyFormData = () => {
  bodyFormData.value = {}
  if (bodyParameters.value && bodyParameters.value.length > 0) {
    bodyParameters.value.forEach(param => {
      // 设置默认值
      if (param.default !== undefined) {
        bodyFormData.value[param.name] = param.default
      } else if (param.type === 'boolean') {
        bodyFormData.value[param.name] = false
      } else if (param.type === 'integer' || param.type === 'number') {
        bodyFormData.value[param.name] = null
      } else {
        bodyFormData.value[param.name] = ''
      }
    })
  }
}

// 重置统一表单数据
const resetUnifiedFormData = () => {
  unifiedFormData.value = {}
  // access_token 默认空
  unifiedFormData.value['access_token'] = ''
  // 查询参数默认值（数值型使用 null，避免 InputNumber 告警）
  queryParameters.value.forEach(param => {
    const type = param.data_type || param.type || (param.schema && param.schema.type)
    if (type === 'integer' || type === 'number') {
      if (param.example !== undefined && param.example !== null && param.example !== '') {
        const n = Number(param.example)
        unifiedFormData.value[param.name] = isNaN(n) ? null : n
      } else {
        unifiedFormData.value[param.name] = null
      }
    } else if (type === 'boolean' || (param.format === 'boolean')) {
      unifiedFormData.value[param.name] = false
    } else {
      unifiedFormData.value[param.name] = param.example ?? ''
    }
  })
  // 路径参数默认值（数值型使用 null，避免 InputNumber 告警）
  pathParameters.value.forEach(param => {
    const type = param.data_type || param.type || (param.schema && param.schema.type)
    if (type === 'integer' || type === 'number') {
      if (param.example !== undefined && param.example !== null && param.example !== '') {
        const n = Number(param.example)
        unifiedFormData.value[param.name] = isNaN(n) ? null : n
      } else {
        unifiedFormData.value[param.name] = null
      }
    } else if (type === 'boolean' || (param.format === 'boolean')) {
      unifiedFormData.value[param.name] = false
    } else {
      unifiedFormData.value[param.name] = param.example ?? ''
    }
  })
  // Body参数默认使用与 bodyFormData 同样的逻辑
  if (bodyParameters.value && bodyParameters.value.length > 0) {
    bodyParameters.value.forEach(param => {
      if (param.default !== undefined) {
        unifiedFormData.value[param.name] = param.default
      } else if (param.type === 'boolean') {
        unifiedFormData.value[param.name] = false
      } else if (param.type === 'integer' || param.type === 'number') {
        unifiedFormData.value[param.name] = null
      } else {
        unifiedFormData.value[param.name] = ''
      }
    })
  }
}

// 获取参数的方法
const fetchParameters = async (endpointId) => {
  try {
    localLoading.value = true
    console.log('🟡 开始获取参数，接口ID:', endpointId)
    
    // 清空之前的参数
    if (apiStore.endpointParameters.length > 0) {
      apiStore.endpointParameters = []
      await nextTick()
    }
    
    // 调用 store 方法获取参数
    await apiStore.fetchEndpointParameters(endpointId)
    
    console.log('🟢 参数获取完成:')
    console.log('  - 参数数量:', apiStore.endpointParameters.length)
    console.log('  - 参数详情:', apiStore.endpointParameters)
    
  } catch (error) {
    console.error('❌ 获取参数失败:', error)
    apiStore.endpointParameters = []
  } finally {
    localLoading.value = false
  }
}

// 组合 loading 状态
const loading = computed(() => props.loading || localLoading.value)

// 获取占位符文本
const getPlaceholder = (param) => {
  let placeholder = `请输入${param.name}`
  
  if (param.type === 'integer' || param.type === 'number') {
    placeholder = `请输入数字`
    if (param.minimum !== undefined && param.maximum !== undefined) {
      placeholder += ` (${param.minimum}-${param.maximum})`
    } else if (param.minimum !== undefined) {
      placeholder += ` (最小${param.minimum})`
    } else if (param.maximum !== undefined) {
      placeholder += ` (最大${param.maximum})`
    }
  } else if (param.format) {
    placeholder += ` (${param.format})`
  }
  
  return placeholder
}

const getMethodType = (method) => {
  const types = {
    'GET': 'success',
    'POST': 'warning',
    'PUT': 'primary',
    'DELETE': 'danger',
    'PATCH': 'info'
  }
  return types[method?.toUpperCase()] || 'info'
}

const getResponseType = (code) => {
  if (code.startsWith('2')) return 'success'
  if (code.startsWith('4')) return 'warning'
  if (code.startsWith('5')) return 'danger'
  return 'info'
}

const getApiTitle = () => {
  if (!props.endpoint) return '未知接口'
  
  const data = props.endpoint
  
  if (data.operation) {
    if (data.operation.summary) return data.operation.summary
    if (data.operation.operationId) return data.operation.operationId
    if (data.operation.description) return data.operation.description
  }
  
  if (data.summary) return data.summary
  if (data.name) return data.name
  if (data.label) return data.label
  if (data.operationId) return data.operationId
  if (data.description) return data.description
  if (data.title) return data.title
  
  if (data.path) {
    const pathParts = data.path.split('/').filter(part => part && !part.includes('{'))
    return pathParts[pathParts.length - 1] || data.path
  }
  
  return '未命名接口'
}

const getApiDescription = () => {
  if (!props.endpoint) return ''
  
  const data = props.endpoint
  
  if (data.operation?.description) return data.operation.description
  if (data.description) return data.description
  if (data.operation?.summary) return data.operation.summary
  if (data.summary) return data.summary
  
  return ''
}

const getResponses = () => {
  if (!props.endpoint) return {}
  
  const data = props.endpoint
  
  if (data.operation?.responses) return data.operation.responses
  if (data.responses) return data.responses
  
  return {}
}

const hasResponses = computed(() => {
  const responses = getResponses()
  return Object.keys(responses).length > 0
})

// 环境选项
const environmentOptions = computed(() => environmentStore.environmentOptions)

// 监听环境变化，加载环境参数
const handleEnvironmentChange = async (environmentId, { silent = false } = {}) => {
  if (!environmentId) {
    currentBaseUrl.value = 'https://example.com'
    return
  }

  try {
    // 获取环境详情
    const envResponse = await environmentService.getEnvironment(environmentId)
    if (envResponse && envResponse.data) {
      currentBaseUrl.value = envResponse.data.base_url || 'https://example.com'
    }

    // 获取环境参数
    const paramsResponse = await environmentStore.fetchEnvironmentParameters(environmentId, {
      page: 1,
      pageSize: 1000
    })

    // 将环境参数回显到表单
    if (paramsResponse && paramsResponse.data) {
      const envParams = paramsResponse.data
      // 创建环境参数的映射，方便查找
      const envParamsMap = {}
      envParams.forEach(param => {
        envParamsMap[param.param_key] = param.param_value
      })
      
      // 遍历所有统一参数，使用环境参数值填充（如果存在）
      unifiedParameters.value.forEach(param => {
        const paramName = param.name
        // 如果环境参数中有这个参数，则使用环境参数的值（覆盖已有值）
        if (envParamsMap.hasOwnProperty(paramName)) {
          const envParamValue = envParamsMap[paramName]
          const meta = unifiedParameters.value.find(p => p.name === paramName)
          if (meta && (meta.type === 'integer' || meta.type === 'number')) {
            const n = Number(envParamValue)
            unifiedFormData.value[paramName] = isNaN(n) ? null : n
          } else if (meta && (meta.type === 'boolean' || meta.format === 'boolean')) {
            // 将字符串 'true'/'false' 转为布尔
            if (typeof envParamValue === 'string') {
              const lower = envParamValue.toLowerCase()
              unifiedFormData.value[paramName] = lower === 'true' ? true : lower === 'false' ? false : false
            } else {
              unifiedFormData.value[paramName] = Boolean(envParamValue)
            }
          } else {
            unifiedFormData.value[paramName] = envParamValue
          }
        } else {
          // 如果环境参数中没有这个参数，则恢复为默认值或空值
          const meta = unifiedParameters.value.find(p => p.name === paramName)
          if (meta && (meta.type === 'integer' || meta.type === 'number')) {
            if (meta.default !== undefined && meta.default !== null && meta.default !== '') {
              const n = Number(meta.default)
              unifiedFormData.value[paramName] = isNaN(n) ? null : n
            } else {
              unifiedFormData.value[paramName] = null
            }
          } else if (meta && (meta.type === 'boolean' || meta.format === 'boolean')) {
            unifiedFormData.value[paramName] = meta.default !== undefined ? Boolean(meta.default) : false
          } else {
            unifiedFormData.value[paramName] = meta?.default ?? ''
          }
        }
      })
    }

    if (!silent) {
      ElMessage.success('环境参数已自动填充')
    }
  } catch (error) {
    console.error('加载环境参数失败:', error)
    ElMessage.error('加载环境参数失败')
  }
}

// 处理测试
const handleTest = async () => {
  if (!selectedEnvironmentId.value || !props.endpoint?.id) {
    ElMessage.warning('请先选择环境')
    return
  }

  testing.value = true
  testResult.value = null

  try {
    // 准备测试数据
    const testData = {
      environment_id: selectedEnvironmentId.value,
      base_url: currentBaseUrl.value,
      ...unifiedFormData.value
    }

    // 调用测试接口
    const response = await endpointService.testEndpoint(props.endpoint.id, testData)

    // 处理响应数据
    const responseData = response?.data || response
    if (responseData && responseData.code === 0 && responseData.data) {
      testResult.value = responseData.data
      ElMessage.success('测试完成')
    } else {
      ElMessage.error(responseData?.message || responseData?.error || '测试失败')
    }
  } catch (error) {
    console.error('测试接口失败:', error)
    ElMessage.error(error.message || '测试接口失败')
  } finally {
    testing.value = false
  }
}

// 格式化响应数据
const formatResponseData = (response) => {
  if (!response) return '无响应数据'
  
  if (response.data !== undefined && response.data !== null) {
    if (typeof response.data === 'string') {
      return response.data
    }
    return JSON.stringify(response.data, null, 2)
  }
  
  if (response.text) {
    return response.text
  }
  
  return '无响应数据'
}

// 获取响应状态码类型
const getResponseStatusType = (statusCode) => {
  if (!statusCode) return 'info'
  if (statusCode >= 200 && statusCode < 300) return 'success'
  if (statusCode >= 400 && statusCode < 500) return 'warning'
  if (statusCode >= 500) return 'danger'
  return 'info'
}

// 复制到剪贴板
const copyToClipboard = async (text) => {
  if (!text) {
    ElMessage.warning('无内容可复制')
    return
  }

  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

// 初始化：加载环境列表
watch(() => props.endpoint, async () => {
  if (props.endpoint) {
    // 加载环境列表
    try {
      await environmentStore.fetchEnvironments({ page: 1, pageSize: 100 })
      
      // 如果环境列表已加载且当前未选中环境，则自动选中"Gitee公有云"
      if (!selectedEnvironmentId.value && environmentStore.environmentOptions.length > 0) {
        const giteeEnv = environmentStore.environmentOptions.find(env => 
          env.label === 'Gitee公有云线上'
        )
        
        if (giteeEnv) {
          selectedEnvironmentId.value = giteeEnv.value
          // 自动触发环境变化处理，加载环境参数
          await handleEnvironmentChange(giteeEnv.value)
        }
      }
    } catch (error) {
      console.error('加载环境列表失败:', error)
    }
  }
}, { immediate: true })
</script>

<style scoped>
.api-detail {
  height: 100%;
  max-height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0;
  position: relative; /* 确保定位上下文 */
  /* 平滑滚动 */
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch; /* iOS 平滑滚动 */
  /* Firefox 滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: #c1c8d1 #f8f9fa;
}

/* WebKit 滚动条样式 */
.api-detail::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.api-detail::-webkit-scrollbar-track {
  background: #f8f9fa;
  border-radius: 4px;
}

.api-detail::-webkit-scrollbar-thumb {
  background: #c1c8d1;
  border-radius: 4px;
  transition: background 0.3s ease;
}

.api-detail::-webkit-scrollbar-thumb:hover {
  background: #a8b2bd;
}

.empty-detail {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  background: #fafafa;
}

.detail-content {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.api-basic-info {
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 20px;
  margin-bottom: 24px;
}

.method-path {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.method-tag {
  min-width: 60px;
  text-align: center;
  font-weight: bold;
  font-size: 12px;
}

.api-path {
  font-family: 'Monaco', 'Consolas', 'Courier New', monospace;
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.api-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 32px 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.section-title .toggle-btn {
  margin-left: 0;
  flex-shrink: 0;
}

.parameter-group {
  margin-bottom: 16px; /* 减小底部间距 */
}

.parameter-group-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.param-desc {
  font-size: 12px;
  color: #909399;
  font-weight: normal;
}

/* Body参数表格样式 */
.body-parameters-table {
  background: transparent;
  border-radius: 0;
  padding: 0;
  border: none;
  height: auto;
  overflow-x: auto; /* 支持横向滚动 */
  overflow-y: visible;
}

.parameter-table {
  width: 100%;
  min-width: 800px; /* 确保表格有最小宽度，触发横向滚动 */
  border: 1px solid #e4e7ed;
  border-radius: 6px;
}

.param-name {
  font-family: 'Monaco', 'Consolas', 'Courier New', monospace;
  font-weight: 500;
  font-size: 13px; /* 调小字体 */
}

.required-tag {
  margin-left: 6px;
}

.param-description {
  line-height: 1.4; /* 减小行高 */
  font-size: 12px; /* 调小字体 */
}

.desc-ellipsis {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: bottom;
}

.format-hint {
  color: #909399;
  font-size: 11px; /* 调小字体 */
  margin-top: 2px; /* 减小间距 */
}

.range-hint {
  color: #e6a23c;
  font-size: 11px; /* 调小字体 */
  margin-top: 2px; /* 减小间距 */
}

.range-hint span {
  margin-right: 8px;
}

:deep(.parameter-table .el-table__header) {
  background: #f8f9fa;
}

:deep(.parameter-table th) {
  background: #f8f9fa;
  font-weight: 600;
  font-size: 13px; /* 调小表头字体 */
  padding: 10px 8px; /* 减小表头padding（上下10px，左右8px） */
}

:deep(.parameter-table .el-table__row) {
  background: white;
}

:deep(.parameter-table .el-table__cell) {
  padding: 4px 4px; /* 减小单元格padding（上下8px，左右8px） */
  font-size: 13px; /* 调小单元格字体 */
}

/* JSON预览样式 */
.json-preview {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px dashed #dcdfe6;
}

.json-preview h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.json-code {
  background: #f8f9fa;
  color: #495057;
  border: 1px solid #e9ecef;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
  overflow-x: auto;
  margin: 0;
}

.no-parameters {
  text-align: center;
  padding: 40px 0;
  color: #909399;
}

.response-section {
  margin-top: 32px;
}

.response-item {
  margin-bottom: 20px;
}

.response-code {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.response-desc {
  font-size: 14px;
  color: #606266;
}

@media (max-width: 768px) {
  .detail-content {
    padding: 16px;
  }

  .api-title {
    font-size: 20px;
  }

  .api-path {
    font-size: 14px;
  }

  .section-title {
    font-size: 18px;
  }

  .parameter-group-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .method-path {
    flex-wrap: wrap;
  }
  
  .body-parameters-table {
    padding: 12px;
  }
}

/* 环境选择器样式 */
.environment-selector {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  gap: 12px;
  margin-top: 16px;
}

/* 测试结果样式 */
.test-result-section {
  margin-top: 32px;
  padding: 0;
  background: transparent;
  border-radius: 0;
  border: none;
}

.test-result-item {
  margin-bottom: 24px;
  padding: 0;
  background: transparent;
  border-radius: 0;
  border: none;
}

.test-result-item:last-child {
  margin-bottom: 0;
}

.test-result-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.code-block {
  position: relative;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 12px;
  margin-top: 8px;
  width: 100%;
  max-width: 100%;
  min-width: 0; /* 允许收缩 */
  box-sizing: border-box;
}

.code-block .copy-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  color: #409eff;
}

.code-content {
  color: #495057;
  font-family: 'Monaco', 'Consolas', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-x: auto;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

/* 统一 info-row 内上下间距，不叠加 code-block 顶部间距 */
.info-row .code-block {
  margin-top: 0;
}

/* 统一展开/收起按钮样式，与状态码标签保持一致的大小和对齐 */
.toggle-btn {
  background-color: #f9fafb !important;
  border: 1px solid #e4e7ed !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  border-radius: 4px;
  padding: 2px 8px;
  height: 24px;
  min-height: 24px;
  line-height: 20px;
  font-size: 12px;
  vertical-align: middle;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

/* 确保按钮在 info-row 中与状态码标签对齐 */
.info-row .toggle-btn {
  margin-left: 0;
  align-self: center;
}

/* 确保状态码标签和按钮高度一致 */
.info-row :deep(.el-tag) {
  height: 24px;
  line-height: 22px;
  display: inline-flex;
  align-items: center;
}


.request-info,
.response-info {
  margin-top: 8px;
}

.info-row {
  margin-bottom: 12px;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  font-weight: 500;
  color: #606266;
  min-width: 80px;
  width: 80px;
  flex-shrink: 0;
}

.info-value {
  color: #303133;
  word-break: break-all;
  flex: 1;
  min-width: 0; /* 允许收缩 */
}

/* 请求头和响应体的代码块固定宽度 */
.info-row .code-block {
  flex: 1;
  min-width: 0;
  max-width: calc(100% - 88px); /* 减去 label 宽度(80px) 和 gap(8px) */
}

/* 参数输入框样式 - 调小尺寸 */
:deep(.parameter-input) {
  font-size: 13px; /* 调小输入框字体 */
}

:deep(.parameter-input .el-input__wrapper) {
  min-height: 32px; /* 减小输入框高度 */
  padding: 0 8px; /* 减小左右内边距 */
}

:deep(.parameter-input .el-input__inner) {
  font-size: 13px; /* 调小输入框内文字体 */
  height: 32px; /* 减小输入框高度 */
  line-height: 32px; /* 垂直居中 */
}

:deep(.parameter-input.el-select) {
  font-size: 13px;
}

:deep(.parameter-input.el-select .el-input__wrapper) {
  min-height: 32px;
}

:deep(.parameter-input.el-select .el-input__inner) {
  font-size: 13px;
  height: 32px;
  line-height: 32px;
}

:deep(.parameter-input.el-input-number) {
  font-size: 13px;
}

:deep(.parameter-input.el-input-number .el-input__wrapper) {
  min-height: 32px;
}

:deep(.parameter-input.el-input-number .el-input__inner) {
  font-size: 13px;
  height: 32px;
  line-height: 32px;
}

:deep(.parameter-input.el-radio-group) {
  font-size: 13px;
}

:deep(.parameter-input.el-radio-group .el-radio) {
  font-size: 13px;
  margin-right: 12px; /* 减小单选按钮间距 */
}

/* 数字输入框内容居左对齐 */
:deep(.number-input-left) {
  width: 100%;
}

:deep(.number-input-left .el-input),
:deep(.number-input-left .el-input__wrapper),
:deep(.number-input-left .el-input__inner),
:deep(.number-input-left input[type="text"]) {
  text-align: left !important;
}

:deep(.number-input-left .el-input__wrapper input) {
  text-align: left !important;
}
</style>