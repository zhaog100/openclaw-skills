// MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
// AutoFlow Dashboard - Vue3 + Element Plus

const { createApp, ref, reactive, computed, onMounted, watch } = Vue;

// === 页面组件 ===

// 登录页
const LoginPage = {
  template: `
    <div style="display:flex;justify-content:center;align-items:center;height:100vh;background:#1a1a2e">
      <el-card style="width:400px" shadow="always">
        <template #header><h2 style="margin:0;text-align:center">🔐 AutoFlow 登录</h2></template>
        <el-input v-model="apiKey" placeholder="输入 API Key (af_xxxx)" @keyup.enter="login" />
        <el-button type="primary" style="width:100%;margin-top:16px" :loading="loading" @click="login">登录</el-button>
      </el-card>
    </div>`,
  setup() {
    const apiKey = ref(localStorage.getItem('af_token') || '');
    const loading = ref(false);
    const login = async () => {
      if (!apiKey.value.startsWith('af_')) return ElMessage.error('API Key格式错误');
      loading.value = true;
      try {
        const r = await api.get('/health');
        localStorage.setItem('af_token', apiKey.value);
        appCtx.loggedIn = true;
      } catch { ElMessage.error('连接失败'); }
      loading.value = false;
    };
    return { apiKey, loading, login };
  }
};

// Dashboard首页
const HomePage = {
  template: `
    <div>
      <el-row :gutter="20">
        <el-col :span="6"><el-card shadow="hover"><el-statistic title="今日对话" :value="stats.conversations" /></el-card></el-col>
        <el-col :span="6"><el-card shadow="hover"><el-statistic title="知识库条目" :value="stats.kb_entries" /></el-card></el-col>
        <el-col :span="6"><el-card shadow="hover"><el-statistic title="LLM成本(¥)" :value="stats.llm_cost" :precision="2" /></el-card></el-col>
        <el-col :span="6"><el-card shadow="hover"><el-statistic title="活跃工作流" :value="stats.workflows" /></el-card></el-col>
      </el-row>
      <el-card style="margin-top:20px"><template #header>📋 最近消息</template>
        <el-table :data="messages" stripe size="small">
          <el-table-column prop="channel" label="渠道" width="80" />
          <el-table-column prop="role" label="角色" width="70" />
          <el-table-column prop="content" label="内容" show-overflow-tooltip />
          <el-table-column prop="created_at" label="时间" width="160" />
        </el-table>
      </el-card>
    </div>`,
  setup() {
    const stats = reactive({ conversations: 0, kb_entries: 0, llm_cost: 0, workflows: 0 });
    const messages = ref([]);
    onMounted(async () => {
      try {
        const r = await api.get('/api/v1/clients/1/usage');
        if (r.data) Object.assign(stats, r.data);
      } catch {}
      try {
        const r = await api.get('/api/v1/conversations?page=1&limit=10');
        if (r.data) messages.value = r.data.items || [];
      } catch {}
    });
    return { stats, messages };
  }
};

// 知识库管理
const KBPage = {
  template: `
    <div>
      <el-button type="primary" @click="showAdd=true" style="margin-bottom:16px">+ 新建知识库</el-button>
      <el-table :data="kbs" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="file_count" label="文档数" width="80" />
        <el-table-column label="操作" width="150">
          <template #default="{row}">
            <el-button size="small" @click="openKB(row)">详情</el-button>
            <el-button size="small" @click="testSearch(row)">搜索</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-dialog v-model="showAdd" title="新建知识库" width="400px">
        <el-input v-model="newKB.name" placeholder="名称" /><br><br>
        <el-input v-model="newKB.desc" placeholder="描述" type="textarea" :rows="2" />
        <template #footer><el-button @click="showAdd=false">取消</el-button><el-button type="primary" @click="createKB">创建</el-button></template>
      </el-dialog>
      <el-dialog v-model="showEntries" title="知识条目" width="700px">
        <el-input v-model="searchQ" placeholder="搜索测试..." @keyup.enter="doSearch" style="margin-bottom:12px" />
        <el-table :data="entries" stripe size="small">
          <el-table-column prop="question" label="问题" show-overflow-tooltip />
          <el-table-column prop="answer" label="回答" show-overflow-tooltip />
        </el-table>
      </el-dialog>
    </div>`,
  setup() {
    const kbs = ref([]), entries = ref([]), showAdd = ref(false), showEntries = ref(false), searchQ = ref('');
    const newKB = reactive({ name: '', desc: '' });
    const load = async () => { try { const r = await api.get('/api/v1/kb'); kbs.value = r.data || []; } catch {} };
    const createKB = async () => { await api.post('/api/v1/kb', newKB); showAdd.value = false; load(); };
    const openKB = async (row) => {
      try { const r = await api.get(`/api/v1/kb/${row.id}/entries`); entries.value = r.data || []; showEntries.value = true; } catch {}
    };
    const testSearch = async (row) => {
      if (!searchQ.value) return;
      try { const r = await api.post(`/api/v1/kb/${row.id}/search`, { query: searchQ.value }); entries.value = r.data || []; showEntries.value = true; } catch {}
    };
    const doSearch = () => {};
    onMounted(load);
    return { kbs, entries, showAdd, showEntries, searchQ, newKB, createKB, openKB, testSearch, doSearch };
  }
};

// 报表中心
const ReportPage = {
  template: `
    <div>
      <el-button type="primary" @click="showCreate=true" style="margin-bottom:16px">+ 新建报表</el-button>
      <el-table :data="reports" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="schedule" label="定时" width="120" />
        <el-table-column label="操作" width="180">
          <template #default="{row}">
            <el-button size="small" type="primary" @click="generate(row)">生成</el-button>
            <el-button size="small" @click="viewSnapshots(row)">快照</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>`,
  setup() {
    const reports = ref([]), showCreate = ref(false);
    const load = async () => { try { const r = await api.get('/api/v1/reports'); reports.value = r.data || []; } catch {} };
    const generate = async (row) => { await api.post(`/api/v1/reports/${row.id}/generate`); ElMessage.success('报表生成中...'); };
    const viewSnapshots = async (row) => { ElMessage.info('快照功能开发中'); };
    onMounted(load);
    return { reports, showCreate, generate, viewSnapshots };
  }
};

// 成本追踪
const CostPage = {
  template: `
    <div>
      <el-row :gutter="20">
        <el-col :span="8"><el-card><el-statistic title="本月总成本" :value="monthly" :precision="2" prefix="¥" /></el-card></el-col>
        <el-col :span="8"><el-card><el-statistic title="本月请求数" :value="requests" /></el-card></el-col>
        <el-col :span="8"><el-card><el-statistic title="平均单次成本" :value="avg" :precision="4" prefix="¥" /></el-card></el-col>
      </el-row>
      <el-card style="margin-top:20px"><template #header>📊 按模型成本分布</template>
        <el-table :data="byModel" stripe>
          <el-table-column prop="model" label="模型" />
          <el-table-column prop="total_cost" label="成本(¥)" :precision="2" />
          <el-table-column prop="request_count" label="请求数" />
        </el-table>
      </el-card>
    </div>`,
  setup() {
    const monthly = ref(0), requests = ref(0), avg = ref(0), byModel = ref([]);
    onMounted(async () => {
      try {
        const r = await api.get('/api/v1/clients/1/costs');
        if (r.data) { monthly.value = r.data.monthly_cost || 0; requests.value = r.data.request_count || 0; avg.value = r.data.avg_cost || 0; byModel.value = r.data.by_model || []; }
      } catch {}
    });
    return { monthly, requests, avg, byModel };
  }
};

// === 主应用 ===
const appCtx = reactive({ loggedIn: !!localStorage.getItem('af_token'), currentPage: 'home' });

const app = createApp({
  template: `
    <el-container style="height:100vh;background:#1a1a2e">
      <el-aside width="200px" style="background:#16213e">
        <div style="padding:20px;color:#e94560;font-size:20px;font-weight:bold">⚡ AutoFlow</div>
        <el-menu :default-active="currentPage" @select="p=>currentPage=p" background-color="#16213e" text-color="#a8a8b3" active-text-color="#e94560">
          <el-menu-item index="home">📊 首页</el-menu-item>
          <el-menu-item index="kb">📚 知识库</el-menu-item>
          <el-menu-item index="reports">📈 报表</el-menu-item>
          <el-menu-item index="crawl">🔍 采集</el-menu-item>
          <el-menu-item index="cost">💰 成本</el-menu-item>
        </el-menu>
      </el-aside>
      <el-main style="padding:20px">
        <login-page v-if="!loggedIn" />
        <component :is="currentComponent" v-else />
      </el-main>
    </el-container>`,
  setup() {
    const currentPage = ref(appCtx.currentPage);
    watch(currentPage, v => appCtx.currentPage = v);
    const currentComponent = computed(() => ({
      home: HomePage, kb: KBPage, reports: ReportPage, crawl: ReportPage, cost: CostPage
    }[currentPage.value] || HomePage));
    return { loggedIn: computed(() => appCtx.loggedIn), currentPage, currentComponent };
  }
});

app.use(ElementPlus);
app.mount('#app');
