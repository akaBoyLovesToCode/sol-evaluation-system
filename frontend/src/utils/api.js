import axios from "axios";
import { ElMessage } from "element-plus";

// Determine API base URL
const getApiBaseUrl = () => {
  // Try build-time environment variable first
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // Fallback: construct from current location for production
  if (window.location.hostname.includes('railway.app')) {
    return 'https://sol-evaluation-system.up.railway.app/api';
  }
  
  // Default for local development
  return '/api';
};

const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const { response, config } = error;

    if (response) {
      switch (response.status) {
        case 401:
          // 如果是login端点失败，让组件处理错误
          if (config.url === "/auth/login") {
            break;
          }

          // 如果是refresh端点失败，直接登出
          if (config.url === "/auth/refresh") {
            localStorage.removeItem("token");
            localStorage.removeItem("refreshToken");
            window.location.href = "/login";
            break;
          }

          // 尝试刷新token
          const refreshToken = localStorage.getItem("refreshToken");
          if (refreshToken && !config._retry) {
            config._retry = true;

            try {
              const refreshResponse = await axios.post(
                `${getApiBaseUrl()}/auth/refresh`,
                {},
                {
                  headers: {
                    Authorization: `Bearer ${refreshToken}`,
                  },
                },
              );

              const { access_token } = refreshResponse.data;
              localStorage.setItem("token", access_token);

              // 重新发送原始请求
              config.headers.Authorization = `Bearer ${access_token}`;
              return api(config);
            } catch (refreshError) {
              // 刷新token失败，清除tokens并跳转到登录页
              localStorage.removeItem("token");
              localStorage.removeItem("refreshToken");
              window.location.href = "/login";
              break;
            }
          } else {
            // 没有refresh token或重试失败，清除token并跳转到登录页
            localStorage.removeItem("token");
            localStorage.removeItem("refreshToken");
            window.location.href = "/login";
          }
          break;
        case 403:
          ElMessage.error("权限不足");
          break;
        case 404:
          ElMessage.error("请求的资源不存在");
          break;
        case 500:
          ElMessage.error("服务器内部错误");
          break;
        default:
          ElMessage.error(response.data?.message || "请求失败");
      }
    } else {
      ElMessage.error("网络连接失败");
    }

    return Promise.reject(error);
  },
);

export default api;
