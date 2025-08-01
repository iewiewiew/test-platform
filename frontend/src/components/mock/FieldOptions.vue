<template>
    <div class="field-options">
      <div v-if="fieldType === 'number'" class="options-group">
        <el-input-number
          v-model="localOptions.min_value"
          placeholder="最小值"
          size="small"
          style="width: 100px; margin-right: 10px;"
        />
        <el-input-number
          v-model="localOptions.max_value"
          placeholder="最大值"
          size="small"
          style="width: 100px; margin-right: 10px;"
        />
        <el-input-number
          v-model="localOptions.decimals"
          :min="0"
          :max="6"
          placeholder="小数位"
          size="small"
          style="width: 100px;"
        />
      </div>
  
      <div v-else-if="fieldType === 'text'" class="options-group">
        <el-input-number
          v-model="localOptions.min_length"
          :min="1"
          placeholder="最小长度"
          size="small"
          style="width: 100px; margin-right: 10px;"
        />
        <el-input-number
          v-model="localOptions.max_length"
          :min="localOptions.min_length || 1"
          placeholder="最大长度"
          size="small"
          style="width: 100px;"
        />
      </div>
  
      <div v-else-if="fieldType === 'date' || fieldType === 'datetime'" class="options-group">
        <el-date-picker
          v-model="localOptions.start_date"
          type="date"
          placeholder="开始日期"
          size="small"
          style="width: 140px; margin-right: 10px;"
          value-format="YYYY-MM-DD"
        />
        <el-date-picker
          v-model="localOptions.end_date"
          type="date"
          placeholder="结束日期"
          size="small"
          style="width: 140px;"
          value-format="YYYY-MM-DD"
        />
      </div>
  
      <div v-else-if="fieldType === 'age'" class="options-group">
        <el-input-number
          v-model="localOptions.min_age"
          :min="0"
          placeholder="最小年龄"
          size="small"
          style="width: 100px; margin-right: 10px;"
        />
        <el-input-number
          v-model="localOptions.max_age"
          :min="localOptions.min_age || 0"
          placeholder="最大年龄"
          size="small"
          style="width: 100px;"
        />
      </div>
  
      <div v-else class="options-placeholder">
        <span class="placeholder-text">无额外选项</span>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, watch } from 'vue'
  
  const props = defineProps({
    fieldType: {
      type: String,
      default: ''
    },
    options: {
      type: Object,
      default: () => ({})
    }
  })
  
  const emit = defineEmits(['update'])
  
  const localOptions = ref({ ...props.options })
  
  watch(
    localOptions,
    (newOptions) => {
      emit('update', newOptions)
    },
    { deep: true }
  )
  
  watch(
    () => props.options,
    (newOptions) => {
      localOptions.value = { ...newOptions }
    }
  )
  </script>
  
  <style scoped>
  .field-options {
    padding: 5px 0;
  }
  
  .options-group {
    display: flex;
    align-items: center;
  }
  
  .options-placeholder {
    display: flex;
    align-items: center;
    height: 32px;
  }
  
  .placeholder-text {
    color: #999;
    font-size: 12px;
  }
  </style>