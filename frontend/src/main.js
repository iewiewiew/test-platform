import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import "./styles/main.css"; // 导入全局样式
import './styles/common.css' // 导入全局样式
import { permissionDirective } from '@/directives/permission'
import { useThemeStore } from '@/stores/theme/themeStore'

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(ElementPlus);

// 全局注册权限指令
app.directive('permission', permissionDirective)

// 初始化主题（需要在 pinia 创建后）
const themeStore = useThemeStore();
themeStore.initTheme();

app.mount("#app");
