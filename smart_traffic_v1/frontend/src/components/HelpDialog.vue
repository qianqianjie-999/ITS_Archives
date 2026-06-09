<template>
  <el-dialog
    v-model="visible"
    title="操作手册"
    width="960px"
    :close-on-click-modal="false"
    destroy-on-close
    class="help-dialog"
  >
    <div class="help-body">
      <aside class="help-nav">
        <a
          v-for="s in sections"
          :key="s.id"
          class="nav-item"
          :class="{ active: activeSection === s.id }"
          @click="scrollTo(s.id)"
        >{{ s.title }}</a>
      </aside>
      <main class="help-content" ref="contentRef">
        <!-- 1. 系统概述 -->
        <section :id="sections[0].id">
          <h2>1. 系统概述</h2>
          <p>智能交通建设档案系统是一套用于管理智能交通前端设备（信号灯、电子警察、违停球、卡口、结构化相机）、后端设备、项目信息、质保状态及电子档案的综合管理平台。</p>

          <h3>1.1 主要功能模块</h3>
          <table>
            <thead><tr><th>模块</th><th>说明</th></tr></thead>
            <tbody>
              <tr><td>首页仪表盘</td><td>设备统计概览、质保到期提醒</td></tr>
              <tr><td>项目管理</td><td>项目信息、验收日期、质保期限管理</td></tr>
              <tr><td>路口管理</td><td>信号灯、电子警察设备配置与质保管理</td></tr>
              <tr><td>点位管理</td><td>违停抓拍、卡口设备、结构化相机配置与质保管理</td></tr>
              <tr><td>后端设备</td><td>服务器、存储、交换机等后端设备管理</td></tr>
              <tr><td>数据统计</td><td>设备数量统计与 Excel 导出</td></tr>
              <tr><td>服务排名</td><td>设备服役年限排名</td></tr>
              <tr><td>附件管理</td><td>电子档案上传、下载与关联</td></tr>
              <tr><td>备忘录</td><td>工作记录与备忘</td></tr>
              <tr><td>用户管理</td><td>账户管理与角色权限控制（管理员专属）</td></tr>
            </tbody>
          </table>

          <h3>1.2 角色与权限</h3>
          <table>
            <thead><tr><th>角色</th><th>权限说明</th></tr></thead>
            <tbody>
              <tr><td>管理员 (admin)</td><td>全部功能，含用户管理</td></tr>
              <tr><td>编辑者 (editor)</td><td>创建、编辑、删除数据</td></tr>
              <tr><td>查看者 (viewer)</td><td>仅查看数据，不可修改</td></tr>
            </tbody>
          </table>
        </section>

        <!-- 2. 登录与退出 -->
        <section :id="sections[1].id">
          <h2>2. 登录与退出</h2>

          <h3>2.1 登录系统</h3>
          <ol>
            <li>打开浏览器访问系统地址</li>
            <li>在登录页输入用户名和密码</li>
            <li>点击"登录"按钮</li>
          </ol>
          <table>
            <thead><tr><th>默认账号</th><th>密码</th><th>角色</th></tr></thead>
            <tbody>
              <tr><td>admin</td><td>123456</td><td>管理员</td></tr>
              <tr><td>editor</td><td>123456</td><td>编辑者</td></tr>
              <tr><td>viewer</td><td>123456</td><td>查看者</td></tr>
            </tbody>
          </table>
          <blockquote>首次登录后建议立即修改默认密码。</blockquote>

          <h3>2.2 退出系统</h3>
          <p>点击页面右上角用户头像/用户名，选择"退出登录"。</p>
        </section>

        <!-- 3. 项目管理 -->
        <section :id="sections[2].id">
          <h2>3. 项目管理</h2>

          <h3>3.1 查看项目列表</h3>
          <p>点击左侧菜单"项目管理"，列表展示所有项目信息：项目名称、合同金额、建设单位、施工单位、验收日期、质保期限、质保状态。</p>

          <h3>3.2 创建项目</h3>
          <ol>
            <li>点击"新建项目"</li>
            <li>填写项目信息（项目名称为必填，质保到期时间为必填）</li>
            <li>点击"保存"</li>
          </ol>
          <p>项目创建后，即可为路口/点位下的设备选择所属项目。</p>
        </section>

        <!-- 4. 路口管理 -->
        <section :id="sections[3].id">
          <h2>4. 路口管理</h2>
          <p>路口是信号灯和电子警察的容器，先创建项目，再创建路口，最后在路口下添加设备。</p>

          <h3>4.1 创建路口</h3>
          <p>在路口列表页点击"新建路口"，填写路口名称（必填）、路口类型、道路名称等信息。</p>

          <h3>4.2 信号灯管理</h3>
          <p>进入路口详情页 → "信号灯"标签 → "新增信号灯"：</p>
          <ul>
            <li>选择所属项目</li>
            <li>信号机类型：智能/非智能</li>
            <li>填写各设备数量（信号机、箭头灯、满屏灯、行人灯、雷达、诱导屏等）</li>
            <li>填写取电说明</li>
          </ul>

          <h3>4.3 电子警察管理</h3>
          <p>进入路口详情页 → "电子警察"标签 → "新增电子警察"：</p>
          <ul>
            <li>选择所属项目</li>
            <li>抓拍类型：卡口抓拍/综合抓拍等</li>
            <li>填写各设备数量（终端服务器、前后拍相机、补光灯、频闪灯、云台摄像机等）</li>
          </ul>

          <h3>4.4 路口质保延期</h3>
          <p>在路口详情页点击"质保延期"，可选择延期范围（仅信号灯 / 仅电子警察 / 两者同时），设置新的质保到期日期。</p>
        </section>

        <!-- 5. 点位管理 -->
        <section :id="sections[4].id">
          <h2>5. 点位管理</h2>

          <h3>5.1 违停抓拍管理</h3>
          <p>点击左侧菜单"违停管理"进入。先创建点位，再在点位详情中添加设备。设备字段包括：相机抓拍区域、相机数量、违停标志数量、监控标志数量、取电说明、网络取电说明。</p>

          <h3>5.2 卡口管理</h3>
          <p>点击左侧菜单"卡口"进入，操作方式与违停抓拍类似。设备字段包括：卡口类型、相机数量、频闪灯数量、雷达数量、标志牌数量。</p>

          <h3>5.3 结构化相机管理</h3>
          <p>点击左侧菜单"结构化相机"进入，操作方式同上。</p>
        </section>

        <!-- 6. 后端设备 -->
        <section :id="sections[5].id">
          <h2>6. 后端设备管理</h2>
          <p>点击左侧菜单"后端设备"，管理服务器、存储、交换机、防火墙等后端设备。填写设备名称、类型、所属项目、各类设备数量、IP地址、安装位置等信息。</p>
        </section>

        <!-- 7. 数据统计 -->
        <section :id="sections[6].id">
          <h2>7. 数据统计</h2>
          <p>点击左侧菜单"统计报表"，查看按项目/按设备类型的统计数据，以及质保状态分布和到期倒计时。点击"导出Excel"可下载统计报表。</p>
        </section>

        <!-- 8. 服务排名 -->
        <section :id="sections[7].id">
          <h2>8. 服务排名</h2>
          <p>点击左侧菜单"服务排名"，按设备服役年限从长到短排列展示全部设备。支持按设备类型筛选和按名称搜索。服役年限 = 当前日期 - 项目验收日期，数据实时计算。</p>
        </section>

        <!-- 9. 附件管理 -->
        <section :id="sections[8].id">
          <h2>9. 附件管理</h2>
          <p>进入设备详情页，在"附件"区域可上传电子档案（合同、验收报告、技术文档等），支持常见文档格式。可下载或删除已上传的附件。</p>
        </section>

        <!-- 10. 备忘录 -->
        <section :id="sections[9].id">
          <h2>10. 备忘录</h2>
          <p>点击左侧菜单"备忘录"，可创建工作记录与备忘，支持编辑、删除和按标题搜索。</p>
        </section>

        <!-- 11. 用户管理 -->
        <section :id="sections[10].id">
          <h2>11. 用户管理（管理员专属）</h2>
          <p>点击左侧菜单"用户管理"（仅管理员可见）。可查看用户列表，创建新用户（用户名、密码、角色），编辑用户信息，禁用/启用账号，删除用户。</p>
        </section>

        <!-- 12. 常见操作流程 -->
        <section :id="sections[11].id">
          <h2>12. 常见操作流程</h2>

          <h3>完整设备录入流程</h3>
          <pre><code>1. 创建项目 → 2. 创建路口/点位 → 3. 添加设备 → 4. 上传附件</code></pre>

          <h3>设备质保延期流程</h3>
          <pre><code>1. 进入设备所在详情页 → 2. 点击"质保延期" → 3. 设置新到期日 → 4. 确认</code></pre>

          <h3>导出数据报表</h3>
          <pre><code>1. 进入"数据统计" → 2. 查看统计结果 → 3. 点击"导出Excel"</code></pre>
        </section>

        <!-- 13. 注意事项 -->
        <section :id="sections[12].id">
          <h2>13. 注意事项</h2>
          <ol>
            <li>首次登录后请立即修改默认密码</li>
            <li>viewer 角色只能查看，无法修改任何数据</li>
            <li>删除项目或路口前，请确认无关联设备</li>
            <li>设备质保到期日期以项目验收日期+质保期自动计算，手动延期后以延期日期为准</li>
            <li>请勿上传超大文件，单个文件建议不超过 50MB</li>
            <li>推荐使用 Chrome、Edge 最新版本浏览器</li>
          </ol>
        </section>
      </main>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits(['update:modelValue'])

const visible = ref(props.modelValue)
const activeSection = ref('sec-overview')
const contentRef = ref<HTMLElement>()

const sections = [
  { id: 'sec-overview', title: '1. 系统概述' },
  { id: 'sec-login', title: '2. 登录与退出' },
  { id: 'sec-project', title: '3. 项目管理' },
  { id: 'sec-road', title: '4. 路口管理' },
  { id: 'sec-point', title: '5. 点位管理' },
  { id: 'sec-device', title: '6. 后端设备' },
  { id: 'sec-statistics', title: '7. 数据统计' },
  { id: 'sec-ranking', title: '8. 服务排名' },
  { id: 'sec-attachment', title: '9. 附件管理' },
  { id: 'sec-memo', title: '10. 备忘录' },
  { id: 'sec-user', title: '11. 用户管理' },
  { id: 'sec-flow', title: '12. 常见操作流程' },
  { id: 'sec-notice', title: '13. 注意事项' }
]

watch(() => props.modelValue, (val) => { visible.value = val })
watch(visible, (val) => { emit('update:modelValue', val) })

function scrollTo(id: string) {
  activeSection.value = id
  nextTick(() => {
    const el = document.getElementById(id)
    if (el && contentRef.value) {
      contentRef.value.scrollTo({ top: el.offsetTop - 16, behavior: 'smooth' })
    }
  })
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.help-body {
  display: flex;
  height: 580px;
  gap: 0;
}

.help-nav {
  width: 180px;
  min-width: 180px;
  border-right: 1px solid $border-color;
  padding: 12px 8px;
  overflow-y: auto;
  background: $bg-page;
  border-radius: $radius-md 0 0 $radius-md;
}

.nav-item {
  display: block;
  padding: 8px 12px;
  border-radius: $radius-sm;
  font-size: 13px;
  color: $text-secondary;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;

  &:hover {
    background: rgba($primary-color, 0.08);
    color: $primary-color;
  }

  &.active {
    background: rgba($primary-color, 0.12);
    color: $primary-color;
    font-weight: 600;
  }
}

.help-content {
  flex: 1;
  padding: 16px 24px;
  overflow-y: auto;

  h2 {
    font-size: 18px;
    font-weight: 700;
    color: $text-primary;
    margin: 0 0 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid $border-color;
  }

  h3 {
    font-size: 15px;
    font-weight: 600;
    color: $text-primary;
    margin: 16px 0 8px;
  }

  section {
    margin-bottom: 28px;
    padding-top: 8px;
  }

  p {
    font-size: 13px;
    color: $text-secondary;
    line-height: 1.7;
    margin: 0 0 8px;
  }

  ol, ul {
    margin: 0 0 8px;
    padding-left: 20px;

    li {
      font-size: 13px;
      color: $text-secondary;
      line-height: 1.8;
    }
  }

  pre {
    background: $bg-page;
    border: 1px solid $border-color;
    border-radius: $radius-sm;
    padding: 10px 14px;
    margin: 8px 0;
    overflow-x: auto;

    code {
      font-size: 13px;
      color: $text-primary;
    }
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0;
    font-size: 13px;

    th, td {
      border: 1px solid $border-color;
      padding: 8px 12px;
      text-align: left;
    }

    th {
      background: $bg-page;
      font-weight: 600;
      color: $text-primary;
    }

    td {
      color: $text-secondary;
    }
  }

  blockquote {
    border-left: 3px solid #faad14;
    background: rgba(#faad14, 0.06);
    margin: 8px 0;
    padding: 8px 14px;
    border-radius: 0 $radius-sm $radius-sm 0;
    font-size: 13px;
    color: #d48806;
  }
}
</style>
