// 原始查询API函数
export async function queryAPI(query: string) {
    const response = await fetch("REPLACEWITHENDPOINT", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    })
  
    if (!response.ok) {
      throw new Error("Failed to fetch data.")
    }
  
    return response.json()
  }
  
// API基础URL - 在Docker环境中使用服务名称
const API_BASE_URL = 'http://backend:8000';

// 向后端API发送搜索请求
export async function vectorSearchAPI(text: string, topK: number = 10) {
  try {
    const response = await fetch('/api/search/vector', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: text,
        top_k: topK
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error during API call:', error);
    throw error;
  }
}

// 根据DOI搜索
export async function searchByDOI(doi: string, size: number = 10) {
  try {
    const response = await fetch(`/api/search/doi/${encodeURIComponent(doi)}?size=${size}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error during API call:', error);
    throw error;
  }
}

// 健康检查
export async function healthCheck() {
  try {
    const response = await fetch('/api/health', {
      method: 'GET'
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error during health check:', error);
    throw error;
  }
}
  