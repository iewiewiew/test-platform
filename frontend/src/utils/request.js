import axios from 'axios'
import { ElMessage } from 'element-plus'

// 生产环境使用相对路径（通过 Nginx 代理），开发环境使用完整 URL
const baseURL = process.env.NODE_ENV === 'production'
    ? '/api'
    : 'http://localhost:5001/api';

const apiClient = axios.create({
    baseURL,
    withCredentials: false,
    headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    },
    maxRedirects: 0,
    timeout: 10000
})

// 不需要重定向到登录页的路由白名单
const publicRoutes = ['/login', '/register', '/forgot-password', '/reset-password']

// 请求拦截器
apiClient.interceptors.request.use(config => {
    console.log('🚀 请求拦截器 - 请求URL:', config.url)

    // 规范化URL，防止双斜杠
    config.url = config.url.replace(/([^:]\/)\/+/g, '$1')

    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')
    console.log('🔑 请求拦截器 - Token:', token ? '存在' : '不存在')

    // 如果存在 token，添加到请求头
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
        console.log('✅ 请求拦截器 - 已添加 Authorization 头')
    } else {
        console.log('❌ 请求拦截器 - 未添加 Authorization 头')
    }

    return config
}, error => {
    console.error('❌ 请求拦截器错误:', error)
    return Promise.reject(error)
})

// 响应拦截器
apiClient.interceptors.response.use(response => {
    console.log('✅ 响应拦截器 - 请求成功:', response.config.url, response.status)
    return response
}, error => {
    if (error.response) {
        const { status, data } = error.response
        const currentPath = window.location.pathname
        
        console.error('❌ API 错误响应:', {
            url: error.config?.url,
            status: status,
            data: data
        })

        if (status === 401) {
            console.log('🔐 检测到 401 错误，清除认证信息')
            localStorage.removeItem('token')
            localStorage.removeItem('user')

            // 检查当前路由是否在公共路由中
            const isPublicRoute = publicRoutes.some(route => 
                currentPath.includes(route)
            )
            
            // 只有不在公共路由且不是登录相关页面才跳转
            if (!isPublicRoute) {
                ElMessage.error('登录已过期，请重新登录')
                // 记录当前路径，登录后可以跳转回来
                const returnUrl = encodeURIComponent(currentPath + window.location.search)
                setTimeout(() => {
                    window.location.href = `/login?returnUrl=${returnUrl}`
                }, 1000)
            }
        } else {
            // 优先显示后端返回的错误消息
            if (data?.message) {
                ElMessage.error(data.message)
            } else if (status >= 500) {
                ElMessage.error('服务器错误，请稍后重试')
            } else {
                ElMessage.error('请求失败，请稍后重试')
            }
        }
    } else if (error.request) {
        console.error('❌ API 错误: 无响应 received', error.request)
        ElMessage.error('网络错误，请检查网络连接')
    } else {
        console.error('❌ API 错误:', error.message)
        ElMessage.error('请求配置错误')
    }

    return Promise.reject(error)
})

// 默认导出
export default apiClient