<template>
  <div class="redis-view">
    <!-- 顶部：Redis 连接选择 -->
    <div class="header-bar">
      <el-select v-model="selectedConnectionId" placeholder="请选择 Redis 连接" filterable @change="handleConnectionChange" style="width: 300px" clearable>
        <el-option v-for="conn in redisConnectionOptions" :key="conn.value" :label="`${conn.label} (${conn.host}:${conn.port})`" :value="conn.value" />
      </el-select>
      <el-button v-if="selectedConnectionId" @click="loadKeys" :loading="store.loading">刷新</el-button>
      <el-button v-if="selectedConnectionId" type="primary" @click="showAddKeyDialog">
        <el-icon><Plus /></el-icon>
        新增 Key
      </el-button>
    </div>

    <!-- 主体：分为左右两部分 -->
    <div class="main-content" v-if="selectedConnectionId">
      <!-- 左侧：Redis Keys 列表 -->
      <div class="left-panel">
        <div style="display: flex; gap: 8px; margin-bottom: 12px">
          <el-input v-model="keyPattern" placeholder="搜索 key（支持 * 通配符）" size="small" clearable @keyup.enter="loadKeys" @clear="loadKeys" />
          <el-button size="small" type="primary" @click="loadKeys">搜索</el-button>
        </div>
        <div style="margin-bottom: 12px; color: #606266; font-size: 12px">共 {{ keyCount }} 个 key</div>
        <div class="keys-list" v-loading="store.loading">
          <div v-if="store.keys.length === 0 && !store.loading" class="empty-keys">
            <el-empty description="暂无 keys" :image-size="80" />
          </div>
          <div v-else class="keys-container">
            <div v-for="key in store.keys" :key="key" class="key-item" :class="{ active: store.currentKey === key }" @click="handleKeyClick(key)">
              <el-icon class="key-icon"><Key /></el-icon>
              <span class="key-name" :title="key">{{ key }}</span>
              <el-dropdown trigger="click" @command="(cmd) => handleKeyCommand(cmd, key)">
                <el-icon class="key-menu-icon"><MoreFilled /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="edit">编辑</el-dropdown-item>
                    <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
            <div v-if="store.pagination.hasMore" class="load-more" @click="loadMoreKeys">
              <el-button text type="primary" :loading="store.loading">加载更多...</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：Key 详情展示区和控制台 -->
      <div class="right-panel">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Key 详情 -->
          <el-tab-pane label="Key 详情" name="detail">
            <div v-if="store.currentKey && store.keyInfo" class="key-detail-panel">
              <div class="key-detail-header">
                <div class="key-info">
                  <span class="key-title">{{ store.currentKey }}</span>
                  <el-tag :type="getTypeTagType(store.keyInfo.type)" size="small">{{ store.keyInfo.type }}</el-tag>
                  <span v-if="store.keyInfo.ttl > 0" class="ttl-info">TTL: {{ formatTTL(store.keyInfo.ttl) }}</span>
                  <span v-else-if="store.keyInfo.ttl === -1" class="ttl-info">永不过期</span>
                </div>
                <div class="key-actions">
                  <el-button size="small" @click="showEditKeyDialog">编辑</el-button>
                  <el-button size="small" type="danger" @click="handleDeleteKey">删除</el-button>
                </div>
              </div>

              <div class="key-detail-content" v-loading="store.dataLoading">
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="Key">
                    <span style="word-break: break-all">{{ store.currentKey }}</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="类型">{{ store.keyInfo.type }}</el-descriptions-item>
                  <el-descriptions-item label="大小">{{ store.keyInfo.size }}</el-descriptions-item>
                  <el-descriptions-item label="TTL">
                    <span v-if="store.keyInfo.ttl > 0">{{ formatTTL(store.keyInfo.ttl) }}</span>
                    <span v-else-if="store.keyInfo.ttl === -1">永不过期</span>
                    <span v-else>已过期</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="值">
                    <div class="value-display">
                      <pre v-if="isJsonValue(store.keyInfo.value)" class="json-value">{{ formatJsonValue(store.keyInfo.value) }}</pre>
                      <div v-else-if="store.keyInfo.type === 'hash'" class="hash-value">
                        <el-table :data="formatHashValue(store.keyInfo.value)" border size="small" max-height="300">
                          <el-table-column prop="field" label="Field" min-width="150" />
                          <el-table-column prop="value" label="Value" min-width="200" show-overflow-tooltip />
                        </el-table>
                      </div>
                      <div v-else-if="store.keyInfo.type === 'list'" class="list-value">
                        <el-table :data="formatListValue(store.keyInfo.value)" border size="small" max-height="300">
                          <el-table-column type="index" label="#" width="60" />
                          <el-table-column prop="value" label="Value" show-overflow-tooltip />
                        </el-table>
                      </div>
                      <div v-else-if="store.keyInfo.type === 'set'" class="set-value">
                        <el-table :data="formatSetValue(store.keyInfo.value)" border size="small" max-height="300">
                          <el-table-column type="index" label="#" width="60" />
                          <el-table-column prop="value" label="Value" show-overflow-tooltip />
                        </el-table>
                      </div>
                      <div v-else-if="store.keyInfo.type === 'zset'" class="zset-value">
                        <el-table :data="formatZSetValue(store.keyInfo.value)" border size="small" max-height="300">
                          <el-table-column type="index" label="#" width="60" />
                          <el-table-column prop="value" label="Value" min-width="150" show-overflow-tooltip />
                          <el-table-column prop="score" label="Score" width="100" />
                        </el-table>
                      </div>
                      <div v-else class="string-value">
                        <pre>{{ store.keyInfo.value }}</pre>
                      </div>
                    </div>
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
            <el-empty v-else description="请先选择一个 key" />
          </el-tab-pane>

          <!-- Redis 控制台 -->
          <el-tab-pane label="Redis 控制台" name="console">
            <div class="console-container">
              <div class="console-toolbar">
                <el-button size="small" type="primary" @click="executeCommand" :loading="commandLoading">执行命令</el-button>
                <el-button size="small" @click="clearConsole">清空</el-button>
              </div>
              <div class="editor-area">
                <el-input v-model="redisCommand" type="textarea" :rows="8" placeholder="请输入 Redis 命令，例如：GET key_name" />
              </div>

              <!-- 常用命令 -->
              <div class="common-commands">
                <div class="commands-title">常用命令：</div>
                <div class="commands-list">
                  <el-button size="small" text type="primary" @click="insertCommand('INFO')">INFO</el-button>
                  <el-button size="small" text type="primary" @click="insertCommand('DBSIZE')">DBSIZE</el-button>
                  <el-button size="small" text type="primary" @click="insertCommand('KEYS *')">KEYS *</el-button>
                  <el-button size="small" text type="primary" @click="insertCommand('SCAN 0')">SCAN 0</el-button>
                  <el-button size="small" text type="primary" @click="insertCommand('PING')">PING</el-button>
                  <el-button size="small" text type="primary" @click="insertCommand('TTL key_name')">TTL key</el-button>
                  <el-button size="small" text type="primary" @click="insertCommand('TYPE key_name')">TYPE key</el-button>
                  <el-button size="small" text type="primary" @click="insertCommand('GET key_name')">GET key</el-button>
                  <el-button size="small" text type="primary" @click="insertCommand('HGETALL key_name')">HGETALL key</el-button>
                  <el-button size="small" text type="primary" @click="insertCommand('LRANGE key_name 0 -1')">LRANGE key</el-button>
                </div>
              </div>

              <!-- 命令执行结果 -->
              <div v-if="commandResult" class="result-area">
                <el-divider>
                  <span>执行结果</span>
                </el-divider>
                <div class="result-content">
                  <pre v-if="typeof commandResult === 'string'" class="result-text">{{ commandResult }}</pre>
                  <div v-else-if="Array.isArray(commandResult)" class="result-list">
                    <div v-for="(item, index) in commandResult" :key="index" class="result-item">{{ formatResultItem(item) }}</div>
                  </div>
                  <div v-else-if="typeof commandResult === 'object'" class="result-object">
                    <el-descriptions :column="1" border>
                      <el-descriptions-item v-for="(value, key) in commandResult" :key="key" :label="key">
                        {{ formatResultItem(value) }}
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>
                  <div v-else class="result-text">{{ formatResultItem(commandResult) }}</div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- Redis 示例 -->
          <el-tab-pane label="Redis 示例" name="examples">
            <div class="examples-container">
              <div class="examples-content">
                <!-- 字符串操作 -->
                <el-collapse v-model="activeExamples" accordion>
                  <el-collapse-item title="字符串操作 (String)" name="string">
                    <div class="example-section">
                      <div class="example-item" v-for="example in stringExamples" :key="example.command">
                        <div class="example-header">
                          <span class="example-desc">{{ example.description }}</span>
                          <el-button size="small" text type="primary" @click="copyToConsole(example.command)">复制到控制台</el-button>
                        </div>
                        <div class="example-command">
                          <code>{{ example.command }}</code>
                        </div>
                      </div>
                    </div>
                  </el-collapse-item>

                  <!-- 哈希操作 -->
                  <el-collapse-item title="哈希操作 (Hash)" name="hash">
                    <div class="example-section">
                      <div class="example-item" v-for="example in hashExamples" :key="example.command">
                        <div class="example-header">
                          <span class="example-desc">{{ example.description }}</span>
                          <el-button size="small" text type="primary" @click="copyToConsole(example.command)">复制到控制台</el-button>
                        </div>
                        <div class="example-command">
                          <code>{{ example.command }}</code>
                        </div>
                      </div>
                    </div>
                  </el-collapse-item>

                  <!-- 列表操作 -->
                  <el-collapse-item title="列表操作 (List)" name="list">
                    <div class="example-section">
                      <div class="example-item" v-for="example in listExamples" :key="example.command">
                        <div class="example-header">
                          <span class="example-desc">{{ example.description }}</span>
                          <el-button size="small" text type="primary" @click="copyToConsole(example.command)">复制到控制台</el-button>
                        </div>
                        <div class="example-command">
                          <code>{{ example.command }}</code>
                        </div>
                      </div>
                    </div>
                  </el-collapse-item>

                  <!-- 集合操作 -->
                  <el-collapse-item title="集合操作 (Set)" name="set">
                    <div class="example-section">
                      <div class="example-item" v-for="example in setExamples" :key="example.command">
                        <div class="example-header">
                          <span class="example-desc">{{ example.description }}</span>
                          <el-button size="small" text type="primary" @click="copyToConsole(example.command)">复制到控制台</el-button>
                        </div>
                        <div class="example-command">
                          <code>{{ example.command }}</code>
                        </div>
                      </div>
                    </div>
                  </el-collapse-item>

                  <!-- 有序集合操作 -->
                  <el-collapse-item title="有序集合操作 (Sorted Set)" name="zset">
                    <div class="example-section">
                      <div class="example-item" v-for="example in zsetExamples" :key="example.command">
                        <div class="example-header">
                          <span class="example-desc">{{ example.description }}</span>
                          <el-button size="small" text type="primary" @click="copyToConsole(example.command)">复制到控制台</el-button>
                        </div>
                        <div class="example-command">
                          <code>{{ example.command }}</code>
                        </div>
                      </div>
                    </div>
                  </el-collapse-item>

                  <!-- 键操作 -->
                  <el-collapse-item title="键操作 (Key)" name="key">
                    <div class="example-section">
                      <div class="example-item" v-for="example in keyExamples" :key="example.command">
                        <div class="example-header">
                          <span class="example-desc">{{ example.description }}</span>
                          <el-button size="small" text type="primary" @click="copyToConsole(example.command)">复制到控制台</el-button>
                        </div>
                        <div class="example-command">
                          <code>{{ example.command }}</code>
                        </div>
                      </div>
                    </div>
                  </el-collapse-item>

                  <!-- 服务器信息 -->
                  <el-collapse-item title="服务器信息 (Server)" name="server">
                    <div class="example-section">
                      <div class="example-item" v-for="example in serverExamples" :key="example.command">
                        <div class="example-header">
                          <span class="example-desc">{{ example.description }}</span>
                          <el-button size="small" text type="primary" @click="copyToConsole(example.command)">复制到控制台</el-button>
                        </div>
                        <div class="example-command">
                          <code>{{ example.command }}</code>
                        </div>
                      </div>
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <!-- 未选择连接时的提示 -->
    <el-empty v-else description="请先选择 Redis 连接" />

    <!-- 新增/编辑 Key 对话框 -->
    <el-dialog v-model="keyDialog.visible" :title="keyDialog.isEdit ? '编辑 Key' : '新增 Key'" width="600px">
      <el-form ref="keyFormRef" :model="keyDialog.form" :rules="keyDialog.rules" label-width="100px">
        <el-form-item label="Key" prop="key">
          <el-input v-model="keyDialog.form.key" :disabled="keyDialog.isEdit" placeholder="请输入 key" />
        </el-form-item>
        <el-form-item label="类型" prop="type">
          <el-select v-model="keyDialog.form.type" :disabled="keyDialog.isEdit" style="width: 100%">
            <el-option label="String" value="string" />
            <el-option label="Hash" value="hash" />
            <el-option label="List" value="list" />
            <el-option label="Set" value="set" />
            <el-option label="ZSet" value="zset" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="keyDialog.form.type === 'hash'" label="Field" prop="field">
          <el-input v-model="keyDialog.form.field" placeholder="请输入 field" />
        </el-form-item>
        <el-form-item v-if="keyDialog.form.type === 'zset'" label="Score" prop="score">
          <el-input-number v-model="keyDialog.form.score" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="值" prop="value">
          <el-input v-model="keyDialog.form.value" type="textarea" :rows="6" placeholder="请输入值" />
        </el-form-item>
        <el-form-item label="TTL（秒）">
          <el-input-number v-model="keyDialog.form.ttl" :min="-1" placeholder="-1 表示永不过期，0 表示使用默认" style="width: 100%" />
          <div style="color: #909399; font-size: 12px; margin-top: 4px">-1: 永不过期, 0: 使用默认, 其他: 过期秒数</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="keyDialog.visible = false">取消</el-button>
          <el-button type="primary" @click="handleSaveKey" :loading="saveLoading">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Key, MoreFilled } from '@element-plus/icons-vue'
import { useRedisStore } from '@/stores/database/redisStore'
import { useDatabaseConnStore } from '@/stores/database/databaseConnStore'
import { redisService } from '@/services/database/redisService'

const redisStore = useRedisStore()
const databaseConnStore = useDatabaseConnStore()
const store = redisStore

// 连接选择
const selectedConnectionId = ref(null)
const redisConnectionOptions = ref([])

// Key 搜索
const keyPattern = ref('*')
const keyCount = ref(0)

// Tab
const activeTab = ref('detail')

// Redis 控制台
const redisCommand = ref('')
const commandResult = ref(null)
const commandLoading = ref(false)

// Redis 示例
const activeExamples = ref(['string'])

// 字符串操作示例
const stringExamples = ref([
  { command: 'SET key_name "value"', description: '设置键值' },
  { command: 'GET key_name', description: '获取键值' },
  { command: 'SETEX key_name 3600 "value"', description: '设置键值并指定过期时间（秒）' },
  { command: 'SETNX key_name "value"', description: '仅当键不存在时设置' },
  { command: 'MSET key1 "value1" key2 "value2"', description: '批量设置多个键值' },
  { command: 'MGET key1 key2', description: '批量获取多个键值' },
  { command: 'INCR key_name', description: '将键值加1' },
  { command: 'INCRBY key_name 10', description: '将键值增加指定数值' },
  { command: 'DECR key_name', description: '将键值减1' },
  { command: 'APPEND key_name "suffix"', description: '追加字符串到键值' },
  { command: 'STRLEN key_name', description: '获取字符串长度' }
])

// 哈希操作示例
const hashExamples = ref([
  { command: 'HSET hash_key field1 "value1"', description: '设置哈希字段值' },
  { command: 'HGET hash_key field1', description: '获取哈希字段值' },
  { command: 'HMSET hash_key field1 "value1" field2 "value2"', description: '批量设置哈希字段' },
  { command: 'HMGET hash_key field1 field2', description: '批量获取哈希字段' },
  { command: 'HGETALL hash_key', description: '获取所有哈希字段和值' },
  { command: 'HKEYS hash_key', description: '获取所有哈希字段名' },
  { command: 'HVALS hash_key', description: '获取所有哈希字段值' },
  { command: 'HDEL hash_key field1', description: '删除哈希字段' },
  { command: 'HEXISTS hash_key field1', description: '检查哈希字段是否存在' },
  { command: 'HLEN hash_key', description: '获取哈希字段数量' }
])

// 列表操作示例
const listExamples = ref([
  { command: 'LPUSH list_key "value1"', description: '从左侧推入元素' },
  { command: 'RPUSH list_key "value1"', description: '从右侧推入元素' },
  { command: 'LPOP list_key', description: '从左侧弹出元素' },
  { command: 'RPOP list_key', description: '从右侧弹出元素' },
  { command: 'LRANGE list_key 0 -1', description: '获取列表指定范围元素' },
  { command: 'LLEN list_key', description: '获取列表长度' },
  { command: 'LINDEX list_key 0', description: '获取列表指定索引的元素' },
  { command: 'LSET list_key 0 "new_value"', description: '设置列表指定索引的值' },
  { command: 'LREM list_key 1 "value"', description: '删除列表中指定值的元素' },
  { command: 'LTRIM list_key 0 9', description: '修剪列表，只保留指定范围' }
])

// 集合操作示例
const setExamples = ref([
  { command: 'SADD set_key "member1"', description: '添加集合成员' },
  { command: 'SMEMBERS set_key', description: '获取所有集合成员' },
  { command: 'SISMEMBER set_key "member1"', description: '检查成员是否在集合中' },
  { command: 'SCARD set_key', description: '获取集合成员数量' },
  { command: 'SREM set_key "member1"', description: '删除集合成员' },
  { command: 'SPOP set_key', description: '随机弹出集合成员' },
  { command: 'SRANDMEMBER set_key', description: '随机获取集合成员' },
  { command: 'SUNION set_key1 set_key2', description: '获取多个集合的并集' },
  { command: 'SINTER set_key1 set_key2', description: '获取多个集合的交集' },
  { command: 'SDIFF set_key1 set_key2', description: '获取多个集合的差集' }
])

// 有序集合操作示例
const zsetExamples = ref([
  { command: 'ZADD zset_key 100 "member1"', description: '添加有序集合成员（带分数）' },
  { command: 'ZRANGE zset_key 0 -1', description: '获取有序集合成员（按索引）' },
  { command: 'ZRANGE zset_key 0 -1 WITHSCORES', description: '获取有序集合成员和分数' },
  { command: 'ZREVRANGE zset_key 0 -1', description: '反向获取有序集合成员' },
  { command: 'ZSCORE zset_key "member1"', description: '获取成员分数' },
  { command: 'ZCARD zset_key', description: '获取有序集合成员数量' },
  { command: 'ZRANK zset_key "member1"', description: '获取成员排名（从小到大）' },
  { command: 'ZREVRANK zset_key "member1"', description: '获取成员排名（从大到小）' },
  { command: 'ZREM zset_key "member1"', description: '删除有序集合成员' },
  { command: 'ZRANGEBYSCORE zset_key 0 100', description: '按分数范围获取成员' }
])

// 键操作示例
const keyExamples = ref([
  { command: 'KEYS *', description: '获取所有键（生产环境慎用）' },
  { command: 'SCAN 0', description: '扫描键（推荐使用）' },
  { command: 'EXISTS key_name', description: '检查键是否存在' },
  { command: 'TYPE key_name', description: '获取键的类型' },
  { command: 'TTL key_name', description: '获取键的剩余过期时间（秒）' },
  { command: 'PTTL key_name', description: '获取键的剩余过期时间（毫秒）' },
  { command: 'EXPIRE key_name 3600', description: '设置键的过期时间（秒）' },
  { command: 'PEXPIRE key_name 3600000', description: '设置键的过期时间（毫秒）' },
  { command: 'DEL key_name', description: '删除键' },
  { command: 'RENAME old_key new_key', description: '重命名键' },
  { command: 'RANDOMKEY', description: '随机获取一个键' }
])

// 服务器信息示例
const serverExamples = ref([
  { command: 'INFO', description: '获取服务器信息' },
  { command: 'INFO server', description: '获取服务器相关信息' },
  { command: 'INFO clients', description: '获取客户端相关信息' },
  { command: 'INFO memory', description: '获取内存使用信息' },
  { command: 'INFO stats', description: '获取统计信息' },
  { command: 'DBSIZE', description: '获取当前数据库键的数量' },
  { command: 'PING', description: '测试连接' },
  { command: 'TIME', description: '获取服务器时间' },
  { command: 'CLIENT LIST', description: '获取客户端连接列表' },
  { command: 'CONFIG GET "*"', description: '获取所有配置（部分命令可能被禁用）' }
])

// Key 对话框
const keyDialog = reactive({
  visible: false,
  isEdit: false,
  form: {
    key: '',
    type: 'string',
    value: '',
    field: '',
    score: 0,
    ttl: 0
  },
  rules: {
    key: [{ required: true, message: '请输入 key', trigger: 'blur' }],
    type: [{ required: true, message: '请选择类型', trigger: 'change' }],
    value: [{ required: true, message: '请输入值', trigger: 'blur' }],
    field: [
      {
        validator: (rule, value, callback) => {
          if (keyDialog.form.type === 'hash' && !value) {
            callback(new Error('Hash 类型需要提供 field'))
          } else {
            callback()
          }
        },
        trigger: 'blur'
      }
    ]
  }
})
const keyFormRef = ref()
const saveLoading = ref(false)

// 方法
const loadConnectionOptions = async () => {
  try {
    await databaseConnStore.fetchConnectionsForSelect()
    // 只显示 Redis 类型的连接
    redisConnectionOptions.value = databaseConnStore.connectionOptions
      .filter((opt) => {
        const conn = databaseConnStore.connections.find((c) => c.id === opt.value)
        return conn && conn.driver && conn.driver.toLowerCase() === 'redis'
      })
      .map((opt) => {
        const conn = databaseConnStore.connections.find((c) => c.id === opt.value)
        return {
          ...opt,
          host: conn.host,
          port: conn.port
        }
      })

    // 默认选择 host 为 127.0.0.1 的连接
    if (redisConnectionOptions.value.length > 0 && !selectedConnectionId.value) {
      const defaultConnection = redisConnectionOptions.value.find((opt) => opt.host === '127.0.0.1')
      if (defaultConnection) {
        selectedConnectionId.value = defaultConnection.value
        await handleConnectionChange(defaultConnection.value)
      }
    }
  } catch (error) {
    ElMessage.error('加载连接列表失败')
  }
}

const handleConnectionChange = async (connectionId) => {
  if (!connectionId) {
    store.reset()
    return
  }

  const connection = databaseConnStore.connections.find((c) => c.id === connectionId)
  if (connection && connection.driver && connection.driver.toLowerCase() === 'redis') {
    store.setCurrentConnection(connection)
    await loadKeys()
    await loadKeyCount()
  }
}

const loadKeys = async () => {
  if (!selectedConnectionId.value) return

  try {
    await store.fetchKeys(keyPattern.value, 0, 100)
    await loadKeyCount()
  } catch (error) {
    ElMessage.error(store.error || '加载 keys 失败')
  }
}

const loadMoreKeys = async () => {
  if (!selectedConnectionId.value || !store.pagination.hasMore) return

  try {
    await store.fetchKeys(keyPattern.value, store.pagination.cursor, 100)
  } catch (error) {
    ElMessage.error(store.error || '加载更多 keys 失败')
  }
}

const loadKeyCount = async () => {
  if (!selectedConnectionId.value) return

  try {
    keyCount.value = await store.fetchKeyCount(keyPattern.value)
  } catch (error) {
    console.error('获取 key 数量失败:', error)
  }
}

const handleKeyClick = async (key) => {
  try {
    await store.fetchKeyInfo(key)
  } catch (error) {
    ElMessage.error(store.error || '加载 key 信息失败')
  }
}

const handleKeyCommand = (command, key) => {
  if (command === 'edit') {
    handleKeyClick(key).then(() => {
      showEditKeyDialog()
    })
  } else if (command === 'delete') {
    handleDeleteKeyConfirm(key)
  }
}

const showAddKeyDialog = () => {
  keyDialog.isEdit = false
  keyDialog.form = {
    key: '',
    type: 'string',
    value: '',
    field: '',
    score: 0,
    ttl: 0
  }
  keyDialog.visible = true
}

const showEditKeyDialog = () => {
  if (!store.currentKey || !store.keyInfo) {
    ElMessage.warning('请先选择一个 key')
    return
  }

  keyDialog.isEdit = true
  keyDialog.form = {
    key: store.currentKey,
    type: store.keyInfo.type,
    value: formatValueForEdit(store.keyInfo.value, store.keyInfo.type),
    field: '',
    score: 0,
    ttl: store.keyInfo.ttl > 0 ? store.keyInfo.ttl : store.keyInfo.ttl === -1 ? -1 : 0
  }
  keyDialog.visible = true
}

const formatValueForEdit = (value, type) => {
  if (!value) return ''

  if (type === 'hash') {
    // Hash 类型在编辑时需要选择 field，这里返回空，让用户输入 field 和 value
    return ''
  } else if (type === 'list' || type === 'set') {
    return Array.isArray(value) ? value.join('\n') : String(value)
  } else if (type === 'zset') {
    // ZSet 类型需要 score，这里只显示值
    return Array.isArray(value) ? value.map((item) => item[0]).join('\n') : String(value)
  }

  return String(value)
}

const handleSaveKey = async () => {
  if (!keyFormRef.value) return

  await keyFormRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      saveLoading.value = true

      const formData = {
        value: keyDialog.form.value,
        type: keyDialog.form.type,
        ttl: keyDialog.form.ttl > 0 ? keyDialog.form.ttl : undefined
      }

      if (keyDialog.form.type === 'hash') {
        formData.field = keyDialog.form.field
      } else if (keyDialog.form.type === 'zset') {
        formData.score = keyDialog.form.score || 0
      }

      if (keyDialog.isEdit) {
        await store.updateKeyValue(keyDialog.form.key, formData)
        ElMessage.success('更新成功')
      } else {
        await store.setKeyValue(keyDialog.form.key, formData)
        ElMessage.success('创建成功')
        await loadKeys()
        await loadKeyCount()
      }

      keyDialog.visible = false

      // 如果编辑的是当前 key，刷新信息
      if (keyDialog.isEdit && store.currentKey === keyDialog.form.key) {
        await store.fetchKeyInfo(keyDialog.form.key)
      }
    } catch (error) {
      ElMessage.error(store.error || '操作失败')
    } finally {
      saveLoading.value = false
    }
  })
}

const handleDeleteKey = () => {
  if (!store.currentKey) {
    ElMessage.warning('请先选择一个 key')
    return
  }
  handleDeleteKeyConfirm(store.currentKey)
}

const handleDeleteKeyConfirm = async (key) => {
  try {
    await ElMessageBox.confirm(`确定要删除 key "${key}" 吗？`, '提示', { type: 'warning' })
    await store.deleteKey(key)
    ElMessage.success('删除成功')
    await loadKeyCount()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(store.error || '删除失败')
    }
  }
}

// 格式化方法
const formatTTL = (ttl) => {
  if (ttl <= 0) return '已过期'
  const days = Math.floor(ttl / 86400)
  const hours = Math.floor((ttl % 86400) / 3600)
  const minutes = Math.floor((ttl % 3600) / 60)
  const seconds = ttl % 60

  const parts = []
  if (days > 0) parts.push(`${days}天`)
  if (hours > 0) parts.push(`${hours}小时`)
  if (minutes > 0) parts.push(`${minutes}分钟`)
  if (seconds > 0 || parts.length === 0) parts.push(`${seconds}秒`)

  return parts.join(' ')
}

const getTypeTagType = (type) => {
  const typeMap = {
    string: 'success',
    hash: 'warning',
    list: 'info',
    set: '',
    zset: 'danger'
  }
  return typeMap[type] || ''
}

const isJsonValue = (value) => {
  if (typeof value !== 'string') return false
  try {
    JSON.parse(value)
    return true
  } catch {
    return false
  }
}

const formatJsonValue = (value) => {
  try {
    return JSON.stringify(JSON.parse(value), null, 2)
  } catch {
    return value
  }
}

const formatHashValue = (value) => {
  if (!value || typeof value !== 'object') return []
  return Object.entries(value).map(([field, val]) => ({
    field,
    value: String(val)
  }))
}

const formatListValue = (value) => {
  if (!Array.isArray(value)) return []
  return value.map((val, index) => ({
    index: index + 1,
    value: String(val)
  }))
}

const formatSetValue = (value) => {
  if (!Array.isArray(value)) return []
  return value.map((val, index) => ({
    index: index + 1,
    value: String(val)
  }))
}

const formatZSetValue = (value) => {
  if (!Array.isArray(value)) return []
  return value.map((item, index) => ({
    index: index + 1,
    value: String(item[0]),
    score: item[1]
  }))
}

// Redis 控制台相关方法
const executeCommand = async () => {
  if (!redisCommand.value.trim()) {
    ElMessage.warning('请输入 Redis 命令')
    return
  }

  if (!selectedConnectionId.value) {
    ElMessage.warning('请先选择 Redis 连接')
    return
  }

  try {
    commandLoading.value = true
    const response = await redisService.executeCommand(selectedConnectionId.value, redisCommand.value.trim())

    if (response.data.success) {
      commandResult.value = response.data.result
    } else {
      ElMessage.error('执行命令失败')
      commandResult.value = null
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '执行命令失败')
    commandResult.value = null
  } finally {
    commandLoading.value = false
  }
}

const clearConsole = () => {
  redisCommand.value = ''
  commandResult.value = null
}

const insertCommand = (command) => {
  redisCommand.value = command
}

const copyToConsole = (command) => {
  redisCommand.value = command
  // 切换到控制台标签页
  activeTab.value = 'console'
  ElMessage.success('已复制到控制台')
}

const formatResultItem = (item) => {
  if (item === null || item === undefined) {
    return '(nil)'
  }
  if (typeof item === 'object') {
    return JSON.stringify(item, null, 2)
  }
  return String(item)
}

// 生命周期
onMounted(() => {
  loadConnectionOptions()
})

onUnmounted(() => {
  store.closeConnection()
})
</script>

<style scoped>
.redis-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.header-bar {
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  gap: 12px;
  align-items: center;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.left-panel {
  width: 300px;
  background: white;
  border-right: 1px solid #ebeef5;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
}

.keys-list {
  flex: 1;
  overflow-y: auto;
}

.empty-keys {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
}

.keys-container {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.key-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
}

.key-item:hover {
  background-color: #f5f7fa;
}

.key-item.active {
  background-color: #e6f7ff;
  color: #409eff;
}

.key-icon {
  font-size: 16px;
  color: #909399;
  flex-shrink: 0;
}

.key-item.active .key-icon {
  color: #409eff;
}

.key-name {
  flex: 1;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.key-menu-icon {
  font-size: 16px;
  color: #909399;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
  flex-shrink: 0;
}

.key-item:hover .key-menu-icon {
  opacity: 1;
}

.load-more {
  text-align: center;
  padding: 12px;
}

.right-panel {
  flex: 1;
  background: white;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.right-panel :deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.right-panel :deep(.el-tab-pane) {
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.key-detail-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.key-detail-header {
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.key-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.key-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  word-break: break-all;
}

.ttl-info {
  font-size: 12px;
  color: #909399;
}

.key-actions {
  display: flex;
  gap: 8px;
}

.key-detail-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.value-display {
  max-width: 100%;
}

.json-value {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  overflow-x: auto;
  margin: 0;
}

.string-value pre {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  overflow-x: auto;
  margin: 0;
  word-break: break-all;
  white-space: pre-wrap;
}

.hash-value,
.list-value,
.set-value,
.zset-value {
  margin-top: 8px;
}

/* Redis 控制台样式 */
.console-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.console-toolbar {
  margin-bottom: 16px;
  display: flex;
  gap: 8px;
}

.editor-area {
  margin-bottom: 16px;
}

.common-commands {
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}

.commands-title {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
  font-weight: 500;
}

.commands-list {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}

.commands-list .el-button {
  width: 100%;
  text-align: center;
  padding: 8px 12px;
}

.result-area {
  flex: 1;
  overflow: auto;
}

.result-content {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  max-height: 400px;
  overflow: auto;
}

.result-text {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  white-space: pre-wrap;
  word-break: break-all;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.result-item {
  padding: 4px 8px;
  background: white;
  border-radius: 2px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.result-object {
  background: white;
  border-radius: 4px;
  padding: 8px;
}

/* Redis 示例样式 */
.examples-container {
  height: 100%;
  overflow: auto;
  padding: 16px;
}

.examples-content {
  max-width: 1200px;
  margin: 0 auto;
}

.example-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.example-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  border-left: 3px solid #409eff;
}

.example-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.example-desc {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.example-command {
  background: #fff;
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.example-command code {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #303133;
  word-break: break-all;
  white-space: pre-wrap;
}

:deep(.el-collapse-item__header) {
  font-weight: 500;
  font-size: 14px;
}

:deep(.el-collapse-item__content) {
  padding: 16px;
}
</style>
