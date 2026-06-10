<template>
  <div class="statistics-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">数据统计报表</h1>
        <p class="page-subtitle">全量设备数据汇总 · 按类型分Tab展示</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="exportData">
          <el-icon><Download /></el-icon>
          导出Excel
        </el-button>
      </div>
    </div>

    <div class="summary-bar">
      <div class="summary-item">
        <span class="sum-label">点位总计</span>
        <span class="sum-value">{{ totalCount }}</span>
      </div>
      <div class="summary-item green">
        <span class="sum-label">在保点位</span>
        <span class="sum-value">{{ inWarrantyCount }}</span>
      </div>
      <div class="summary-item red">
        <span class="sum-label">过保点位</span>
        <span class="sum-value">{{ expiredCount }}</span>
      </div>
      <div class="summary-item blue">
        <span class="sum-label">涉及项目</span>
        <span class="sum-value">{{ projectCount }}</span>
      </div>
    </div>

    <div class="component-summary">
      <div class="comp-card" v-for="c in componentTotals" :key="c.label">
        <span class="comp-label">{{ c.label }}</span>
        <span class="comp-value" :style="{ color: c.color }">{{ c.value.toLocaleString() }}</span>
      </div>
    </div>

    <div class="filter-bar">
      <el-row :gutter="12">
        <el-col :span="6">
          <el-select v-model="filterWarranty" placeholder="质保状态" clearable @change="handleFilter">
            <el-option label="全部" value="" />
            <el-option label="在保" value="在保" />
            <el-option label="过保" value="过保" />
            <el-option label="点位无关联项目" value="点位无关联项目" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-select v-model="filterProject" placeholder="归属项目" clearable filterable @change="handleFilter">
            <el-option label="全部" value="" />
            <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
          </el-select>
        </el-col>
        <el-col :span="10">
          <el-input v-model="searchKeyword" placeholder="搜索设备名称、路口名称..." clearable @input="handleFilter">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
      </el-row>
    </div>

    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="项目概览" name="project_overview">
        <div class="filter-bar" style="margin-bottom: 16px;">
          <el-row :gutter="12">
            <el-col :span="10">
              <el-select v-model="filterProjectOverviewWarranty" placeholder="质保状态" clearable>
                <el-option label="全部" value="" />
                <el-option label="在保" value="在保" />
                <el-option label="过保" value="过保" />
              </el-select>
            </el-col>
            <el-col :span="14">
              <el-input v-model="searchProjectOverviewKeyword" placeholder="搜索项目名称、建设单位..." clearable>
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
            </el-col>
          </el-row>
        </div>
        <el-table :data="pagedData.project_overview" stripe v-loading="loading" border size="small">
          <el-table-column label="序号" width="55" fixed>
            <template #default="{ $index }">{{ (currentPage - 1) * pageSize + $index + 1 }}</template>
          </el-table-column>
          <el-table-column prop="name" label="项目名称" min-width="140" fixed />
          <el-table-column prop="builder" label="建设单位" min-width="100" />
          <el-table-column prop="tl" label="信号灯" width="80" align="center" />
          <el-table-column prop="ep" label="电子警察" width="80" align="center" />
          <el-table-column prop="pe" label="违停球" width="80" align="center" />
          <el-table-column prop="cp" label="卡口" width="80" align="center" />
          <el-table-column prop="sn" label="结构化相机" width="100" align="center" />
          <el-table-column prop="bd" label="后端设备" width="80" align="center" />
          <el-table-column prop="total" label="合计" width="70" align="center">
            <template #default="{ row }">
              <b>{{ row.total }}</b>
            </template>
          </el-table-column>
          <el-table-column prop="warranty_expire_date" label="质保到期" width="110" />
          <el-table-column prop="warranty_status" label="质保状态" width="90">
            <template #default="{ row }">
              <el-tag :type="tagType(row.warranty_status)" size="small">{{ row.warranty_status }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="信号灯" name="traffic_light">
        <el-table :data="pagedData.traffic_light" stripe v-loading="loading" border size="small">
          <el-table-column label="序号" width="55" fixed>
            <template #default="{ $index }">
              {{ (currentPage - 1) * pageSize + $index + 1 }}
            </template>
          </el-table-column>
          <el-table-column prop="intersection_name" label="路口名称" min-width="130" fixed />
          <el-table-column prop="intersection_type" label="路口类型" width="100" />
          <el-table-column prop="project_name" label="归属项目" min-width="130" />
          <el-table-column prop="acceptance_date" label="项目验收日期" width="120" />
          <el-table-column prop="warranty_period" label="项目质保期" width="100">
            <template #default="{ row }">{{ row.warranty_period ? row.warranty_period + '年' : '-' }}</template>
          </el-table-column>
          <el-table-column prop="warranty_expire_date" label="质保到期" width="120" />
          <el-table-column prop="warranty_status" label="质保状态" width="90">
            <template #default="{ row }">
              <el-tag :type="tagType(row.warranty_status)" size="small">{{ row.warranty_status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="construction_unit" label="建设单位" min-width="110" />
          <el-table-column prop="construction_company" label="施工单位" min-width="110" />
          <el-table-column prop="signal_type" label="信号机类型" width="110" />
          <el-table-column prop="signal_count" label="信号机数量" width="100" align="center" />
          <el-table-column prop="left_arrow_count" label="左转箭头灯" width="100" align="center" />
          <el-table-column prop="straight_arrow_count" label="直行箭头灯" width="100" align="center" />
          <el-table-column prop="right_arrow_count" label="右转箭头灯" width="100" align="center" />
          <el-table-column prop="full_screen_count" label="满屏灯" width="80" align="center" />
          <el-table-column prop="non_motor_count" label="非机动灯" width="90" align="center" />
          <el-table-column prop="pedestrian_count" label="人行灯" width="80" align="center" />
          <el-table-column prop="countdown_timer_count" label="倒计时器" width="90" align="center" />
          <el-table-column prop="radar_count" label="车流量雷达" width="100" align="center" />
          <el-table-column prop="guide_screen_count" label="诱导屏" width="80" align="center" />
          <el-table-column prop="power_source" label="取电说明" min-width="120" show-overflow-tooltip />
          <el-table-column prop="usage_days" label="使用时长（天）" width="120" align="center" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="电子警察" name="electronic_police">
        <el-table :data="pagedData.electronic_police" stripe v-loading="loading" border size="small">
          <el-table-column label="序号" width="55" fixed>
            <template #default="{ $index }">
              {{ (currentPage - 1) * pageSize + $index + 1 }}
            </template>
          </el-table-column>
          <el-table-column prop="intersection_name" label="路口名称" min-width="130" fixed />
          <el-table-column prop="intersection_type" label="路口类型" width="100" />
          <el-table-column prop="project_name" label="归属项目" min-width="130" />
          <el-table-column prop="acceptance_date" label="项目验收日期" width="120" />
          <el-table-column prop="warranty_period" label="项目质保期" width="100">
            <template #default="{ row }">{{ row.warranty_period ? row.warranty_period + '年' : '-' }}</template>
          </el-table-column>
          <el-table-column prop="warranty_expire_date" label="质保到期" width="120" />
          <el-table-column prop="warranty_status" label="质保状态" width="90">
            <template #default="{ row }">
              <el-tag :type="tagType(row.warranty_status)" size="small">{{ row.warranty_status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="construction_unit" label="建设单位" min-width="110" />
          <el-table-column prop="construction_company" label="施工单位" min-width="110" />
          <el-table-column prop="capture_type" label="抓拍类型" width="100" />
          <el-table-column prop="terminal_server_count" label="终端服务器" width="100" align="center" />
          <el-table-column prop="forward_capture_count" label="正向抓拍" width="90" align="center" />
          <el-table-column prop="reverse_capture_count" label="反向抓拍" width="90" align="center" />
          <el-table-column prop="led_light_count" label="LED灯" width="80" align="center" />
          <el-table-column prop="strobe_light_count" label="爆闪灯" width="80" align="center" />
          <el-table-column prop="ptz_count" label="监控球机" width="90" align="center" />
          <el-table-column prop="signal_detector_count" label="信号检测器" width="100" align="center" />
          <el-table-column prop="network_source" label="取网说明" min-width="120" show-overflow-tooltip />
          <el-table-column prop="usage_days" label="使用时长（天）" width="120" align="center" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="违停球" name="parking_enforcement">
        <el-table :data="pagedData.parking_enforcement" stripe v-loading="loading" border size="small">
          <el-table-column label="序号" width="55" fixed>
            <template #default="{ $index }">
              {{ (currentPage - 1) * pageSize + $index + 1 }}
            </template>
          </el-table-column>
          <el-table-column prop="point_name" label="点位名称" min-width="130" fixed />
          <el-table-column prop="camera_area" label="抓拍区域" min-width="120" />
          <el-table-column prop="project_name" label="归属项目" min-width="130" />
          <el-table-column prop="acceptance_date" label="项目验收日期" width="120" />
          <el-table-column prop="warranty_period" label="项目质保期" width="100">
            <template #default="{ row }">{{ row.warranty_period ? row.warranty_period + '年' : '-' }}</template>
          </el-table-column>
          <el-table-column prop="warranty_expire_date" label="质保到期" width="120" />
          <el-table-column prop="warranty_status" label="质保状态" width="90">
            <template #default="{ row }">
              <el-tag :type="tagType(row.warranty_status)" size="small">{{ row.warranty_status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="construction_unit" label="建设单位" min-width="110" />
          <el-table-column prop="construction_company" label="施工单位" min-width="110" />
          <el-table-column prop="camera_count" label="抓拍机数量" width="100" align="center" />
          <el-table-column prop="parking_sign_count" label="违停标牌" width="90" align="center" />
          <el-table-column prop="monitor_sign_count" label="监控标牌" width="90" align="center" />
          <el-table-column prop="power_source" label="取电说明" min-width="120" show-overflow-tooltip />
          <el-table-column prop="network_source" label="取网说明" min-width="120" show-overflow-tooltip />
          <el-table-column prop="usage_days" label="使用时长（天）" width="120" align="center" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="卡口" name="checkpoint">
        <el-table :data="pagedData.checkpoint" stripe v-loading="loading" border size="small">
          <el-table-column label="序号" width="55" fixed>
            <template #default="{ $index }">
              {{ (currentPage - 1) * pageSize + $index + 1 }}
            </template>
          </el-table-column>
          <el-table-column prop="point_name" label="点位名称" min-width="130" fixed />
          <el-table-column prop="point_type" label="卡口类型" width="150" />
          <el-table-column prop="project_name" label="归属项目" min-width="130" />
          <el-table-column prop="acceptance_date" label="项目验收日期" width="120" />
          <el-table-column prop="warranty_period" label="项目质保期" width="100">
            <template #default="{ row }">{{ row.warranty_period ? row.warranty_period + '年' : '-' }}</template>
          </el-table-column>
          <el-table-column prop="warranty_expire_date" label="质保到期" width="120" />
          <el-table-column prop="warranty_status" label="质保状态" width="90">
            <template #default="{ row }">
              <el-tag :type="tagType(row.warranty_status)" size="small">{{ row.warranty_status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="construction_unit" label="建设单位" min-width="110" />
          <el-table-column prop="construction_company" label="施工单位" min-width="110" />
          <el-table-column prop="camera_count" label="抓拍机数量" width="100" align="center" />
          <el-table-column prop="strobe_light_count" label="爆闪灯数量" width="100" align="center" />
          <el-table-column prop="radar_count" label="测速雷达" width="90" align="center" />
          <el-table-column prop="sign_count" label="标牌数量" width="90" align="center" />
          <el-table-column prop="power_source" label="取电说明" min-width="120" show-overflow-tooltip />
          <el-table-column prop="network_source" label="取网说明" min-width="120" show-overflow-tooltip />
          <el-table-column prop="usage_days" label="使用时长（天）" width="120" align="center" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="结构化相机" name="sky_net">
        <el-table :data="pagedData.sky_net" stripe v-loading="loading" border size="small">
          <el-table-column label="序号" width="55" fixed>
            <template #default="{ $index }">
              {{ (currentPage - 1) * pageSize + $index + 1 }}
            </template>
          </el-table-column>
          <el-table-column prop="point_name" label="点位名称" min-width="130" fixed />
          <el-table-column prop="camera_area" label="监控区域" min-width="120" />
          <el-table-column prop="project_name" label="归属项目" min-width="130" />
          <el-table-column prop="acceptance_date" label="项目验收日期" width="120" />
          <el-table-column prop="warranty_period" label="项目质保期" width="100">
            <template #default="{ row }">{{ row.warranty_period ? row.warranty_period + '年' : '-' }}</template>
          </el-table-column>
          <el-table-column prop="warranty_expire_date" label="质保到期" width="120" />
          <el-table-column prop="warranty_status" label="质保状态" width="90">
            <template #default="{ row }">
              <el-tag :type="tagType(row.warranty_status)" size="small">{{ row.warranty_status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="construction_unit" label="建设单位" min-width="110" />
          <el-table-column prop="construction_company" label="施工单位" min-width="110" />
          <el-table-column prop="camera_count" label="相机数量" width="90" align="center" />
          <el-table-column prop="bracket_count" label="支架数量" width="90" align="center" />
          <el-table-column prop="pole_count" label="立杆数量" width="90" align="center" />
          <el-table-column prop="box_count" label="挂箱数量" width="90" align="center" />
          <el-table-column prop="fill_light_count" label="补光灯数量" width="100" align="center" />
          <el-table-column prop="speaker_count" label="音箱数量" width="90" align="center" />
          <el-table-column prop="power_source" label="取电说明" min-width="120" show-overflow-tooltip />
          <el-table-column prop="network_source" label="取网说明" min-width="120" show-overflow-tooltip />
          <el-table-column prop="usage_days" label="使用时长（天）" width="120" align="center" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="后端设备" name="backend_device">
        <el-table :data="pagedData.backend_device" stripe v-loading="loading" border size="small">
          <el-table-column label="序号" width="55" fixed>
            <template #default="{ $index }">
              {{ (currentPage - 1) * pageSize + $index + 1 }}
            </template>
          </el-table-column>
          <el-table-column prop="name" label="设备名称" min-width="140" fixed />
          <el-table-column prop="model" label="品牌型号" width="130" />
          <el-table-column prop="type" label="设备类型" width="130" />
          <el-table-column prop="quantity" label="设备数量" width="90" align="center" />
          <el-table-column prop="project_name" label="归属项目" min-width="130" />
          <el-table-column prop="acceptance_date" label="项目验收日期" width="120" />
          <el-table-column prop="warranty_period" label="项目质保期" width="100">
            <template #default="{ row }">{{ row.warranty_period ? row.warranty_period + '年' : '-' }}</template>
          </el-table-column>
          <el-table-column prop="warranty_expire_date" label="质保到期" width="120" />
          <el-table-column prop="warranty_status" label="质保状态" width="90">
            <template #default="{ row }">
              <el-tag :type="tagType(row.warranty_status)" size="small">{{ row.warranty_status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="construction_unit" label="建设单位" min-width="110" />
          <el-table-column prop="construction_company" label="施工单位" min-width="110" />
          <el-table-column prop="usage_days" label="使用时长（天）" width="120" align="center" />
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <div class="pager">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[20, 50, 100]"
        :total="currentTabTotal"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        class="dark-pagination"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Search } from '@element-plus/icons-vue'
import { intersectionApi } from '@/api/intersections'
import { pointApi, checkpointPointApi, backendDeviceApi, skyNetApi } from '@/api/points'
import { projectApi } from '@/api/projects'
import apiClient from '@/api'

const loading = ref(false)
const activeTab = ref('traffic_light')
const currentPage = ref(1)
const pageSize = ref(20)

const filterWarranty = ref('')
const filterProject = ref('')
const searchKeyword = ref('')
const filterProjectOverviewWarranty = ref('')
const searchProjectOverviewKeyword = ref('')

const projects = ref<any[]>([])
const trafficLights = ref<any[]>([])
const electronicPolices = ref<any[]>([])
const parkingEnforcements = ref<any[]>([])
const checkpoints = ref<any[]>([])
const skyNetPoints = ref<any[]>([])
const backendDevices = ref<any[]>([])

function tagType(status: string) {
  if (status === '在保') return 'success'
  if (status === '过保') return 'danger'
  return 'info'
}

function applyFilter(list: any[]) {
  return list.filter(item => {
    if (filterWarranty.value && item.warranty_status !== filterWarranty.value) return false;
    if (filterProject.value && item.project_id !== filterProject.value) return false;
    if (searchKeyword.value) {
      const kw = searchKeyword.value.toLowerCase();
      const haystack = [item.name, item.intersection_name, item.point_name, item.project_name, item.intersection_type, item.type]
        .filter(Boolean).join(' ').toLowerCase();
      if (!haystack.includes(kw)) return false;
    }
    return true;
  });
}

function calculateUsageDays(acceptanceDate: string): string {
  if (!acceptanceDate) return '';
  const accDate = new Date(acceptanceDate);
  const today = new Date();
  const diffTime = Math.abs(today.getTime() - accDate.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays.toString();
}

const filteredData = computed(() => {
  return {
    traffic_light: applyFilter(trafficLights.value).map(item => ({
      ...item,
      usage_days: calculateUsageDays(item.acceptance_date)
    })),
    electronic_police: applyFilter(electronicPolices.value).map(item => ({
      ...item,
      usage_days: calculateUsageDays(item.acceptance_date)
    })),
    parking_enforcement: applyFilter(parkingEnforcements.value).map(item => ({
      ...item,
      usage_days: calculateUsageDays(item.acceptance_date)
    })),
    checkpoint: applyFilter(checkpoints.value).map(item => ({
      ...item,
      usage_days: calculateUsageDays(item.acceptance_date)
    })),
    sky_net: applyFilter(skyNetPoints.value).map(item => ({
      ...item,
      usage_days: calculateUsageDays(item.acceptance_date)
    })),
    backend_device: applyFilter(backendDevices.value).map(item => ({
      ...item,
      usage_days: calculateUsageDays(item.acceptance_date)
    }))
  };
})

const pagedData = computed(() => {
  if (activeTab.value === 'project_overview') {
    const start = (currentPage.value - 1) * pageSize.value
    return { project_overview: filteredProjectSummary.value.slice(start, start + pageSize.value) }
  }
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  const result: Record<string, any[]> = {}
  for (const [key, data] of Object.entries(filteredData.value)) {
    result[key] = data.slice(start, end)
  }
  return result
})

const currentTabTotal = computed(() => {
  const tab = activeTab.value
  if (tab === 'project_overview') return filteredProjectSummary.value.length
  return (filteredData.value as any)[tab]?.length || 0
})

const componentTotals = computed(() => {
  const tl = trafficLights.value, ep = electronicPolices.value, pe = parkingEnforcements.value
  const cp = checkpoints.value, sn = skyNetPoints.value, bd = backendDevices.value

  const sum = (arr: any[], field: string) => arr.reduce((s, i) => s + (Number(i[field]) || 0), 0)

  return [
    { label: '信号机', value: sum(tl, 'signal_count'), color: '#52c41a' },
    { label: '雷达', value: sum(tl, 'radar_count'), color: '#fa8c16' },
    { label: '诱导屏', value: sum(tl, 'guide_screen_count'), color: '#13c2c2' },
    { label: '正向抓拍相机', value: sum(ep, 'forward_capture_count'), color: '#1890ff' },
    { label: '反向抓拍相机', value: sum(ep, 'reverse_capture_count'), color: '#722ed1' },
    { label: '监控球机', value: sum(ep, 'ptz_count'), color: '#eb2f96' },
    { label: '终端服务器', value: sum(ep, 'terminal_server_count'), color: '#2f54eb' },
    { label: '违停抓拍机', value: sum(pe, 'camera_count'), color: '#faad14' },
    { label: '卡口相机', value: sum(cp, 'camera_count'), color: '#00d4ff' },
    { label: '测速雷达', value: sum(cp, 'radar_count'), color: '#fa541c' },
    { label: '结构化相机', value: sum(sn, 'camera_count'), color: '#c41d7f' },
    { label: '后端设备', value: bd.length, color: '#595959' },
  ].filter(c => c.value > 0)
})

const projectSummary = computed(() => {
  const projects = new Map<number, any>()
  const allData = [...trafficLights.value, ...electronicPolices.value, ...parkingEnforcements.value,
    ...checkpoints.value, ...skyNetPoints.value, ...backendDevices.value]

  allData.forEach((item: any) => {
    const pid = item.project_id
    if (!pid) return
    if (!projects.has(pid)) {
      projects.set(pid, {
        id: pid,
        name: item.project_name || '未知项目',
        builder: item.construction_unit || '-',
        warranty_expire_date: item.warranty_expire_date || '-',
        warranty_status: '在保',
        tl: 0, ep: 0, pe: 0, cp: 0, sn: 0, bd: 0, total: 0
      })
    }
    const p = projects.get(pid)!
    if ('signal_type' in item) p.tl++
    else if ('capture_type' in item) p.ep++
    else if ('checkpoint_type' in item) p.cp++
    else if ('parking_sign_count' in item) p.pe++
    else if ('bracket_count' in item || 'pole_count' in item) p.sn++
    else if ('server_count' in item || 'switch_count' in item || 'storage_count' in item) p.bd++
    else if ('intersection_name' in item && 'total_signal_count' in item) p.tl++
    else if ('intersection_name' in item) p.ep++
    // track worst warranty status
    if (item.warranty_status === '过保') p.warranty_status = '过保'
    if (item.warranty_expire_date && (!p.warranty_expire_date || p.warranty_expire_date === '-' || item.warranty_expire_date < p.warranty_expire_date)) {
      p.warranty_expire_date = item.warranty_expire_date
    }
  })

  const result = Array.from(projects.values())
  result.forEach(p => { p.total = p.tl + p.ep + p.pe + p.cp + p.sn + p.bd })
  return result.sort((a, b) => b.total - a.total)
})

const filteredProjectSummary = computed(() => {
  return projectSummary.value.filter(p => {
    if (searchProjectOverviewKeyword.value) {
      const kw = searchProjectOverviewKeyword.value.toLowerCase()
      const haystack = [p.name, p.builder].filter(Boolean).join(' ').toLowerCase()
      if (!haystack.includes(kw)) return false
    }
    if (filterProjectOverviewWarranty.value) {
      if (filterProjectOverviewWarranty.value === '在保' && p.warranty_status !== '在保') return false
      if (filterProjectOverviewWarranty.value === '过保' && p.warranty_status !== '过保') return false
    }
    return true
  })
})

const totalCount = computed(() => {
  return trafficLights.value.length + electronicPolices.value.length +
    parkingEnforcements.value.length + checkpoints.value.length + skyNetPoints.value.length + backendDevices.value.length
})

const inWarrantyCount = computed(() => {
  return [...trafficLights.value, ...electronicPolices.value, ...parkingEnforcements.value,
    ...checkpoints.value, ...skyNetPoints.value, ...backendDevices.value]
    .filter(i => i.warranty_status === '在保').length
})

const expiredCount = computed(() => {
  return [...trafficLights.value, ...electronicPolices.value, ...parkingEnforcements.value,
    ...checkpoints.value, ...skyNetPoints.value, ...backendDevices.value]
    .filter(i => i.warranty_status === '过保').length
})

const projectCount = computed(() => {
  const ids = new Set<number>()
  ;[...trafficLights.value, ...electronicPolices.value, ...parkingEnforcements.value,
    ...checkpoints.value, ...skyNetPoints.value, ...backendDevices.value]
    .forEach(i => { if (i.project_id) ids.add(i.project_id) })
  return ids.size
})

function handleFilter() { currentPage.value = 1 }
function handleTabChange() { currentPage.value = 1 }
function handleSizeChange() { currentPage.value = 1 }
function handleCurrentChange() {}
function handleProjectOverviewFilter() { currentPage.value = 1 }

async function fetchData() {
  loading.value = true
  try {
    const [
      p, tl, ep, pe, cp, sn, bd
    ] = await Promise.all([
      projectApi.list({ per_page: 0 }),
      intersectionApi.getTrafficLightsAll(),
      intersectionApi.getElectronicPolicesAll(),
      pointApi.getParkingEnforcementsAll(),
      checkpointPointApi.getCheckpointsAll(),
      skyNetApi.getSkyNetsAll(),
      backendDeviceApi.list({ per_page: 0 })
    ])
    projects.value = p.data || []
    trafficLights.value = tl.data || []
    electronicPolices.value = ep.data || []
    parkingEnforcements.value = pe.data || []
    checkpoints.value = cp.data || []
    skyNetPoints.value = sn.data || []
    backendDevices.value = bd.data || []
  } catch (error) {
    console.error('获取数据失败', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

async function exportData() {
  try {
    ElMessage.info('正在导出数据...')
    const response = await apiClient.get('/export/statistics', { responseType: 'blob' }) as unknown as Blob
    const url = window.URL.createObjectURL(new Blob([response]))
    const a = document.createElement('a')
    a.href = url
    a.download = `智能交通设备统计_${new Date().toISOString().split('T')[0]}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败', error)
    ElMessage.error('导出失败')
  }
}

onMounted(fetchData)
</script>

<style lang="scss" scoped>
@import '@/styles/variables.scss';

.statistics-page {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.page-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 20px;
  .page-title { font-size: 22px; font-weight: 700; color: $text-primary; margin: 0; }
  .page-subtitle { font-size: 13px; color: $text-secondary; margin: 4px 0 0; }
}

.summary-bar {
  display: flex; gap: 16px; margin-bottom: 16px;
  .summary-item {
    flex: 1; background: $bg-card; border-radius: $radius-md; padding: 16px 20px;
    box-shadow: $shadow-md; text-align: center; border: 1px solid $border-color;
    .sum-label { display: block; font-size: 12px; color: $text-secondary; margin-bottom: 4px; }
    .sum-value { font-size: 24px; font-weight: 700; color: $text-primary; }
    &.green .sum-value { color: $success-color; }
    &.red .sum-value { color: $error-color; }
    &.blue .sum-value { color: $primary-color; }
  }
}

.component-summary {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 10px;
  margin-bottom: 16px;

  .comp-card {
    background: $bg-card;
    border: 1px solid $border-color;
    border-radius: $radius-md;
    padding: 14px 16px;
    text-align: center;
    transition: all $transition-fast;
    box-shadow: $shadow-md;
    &:hover {
      border-color: rgba($primary-color, 0.3);
      transform: translateY(-2px);
    }
    .comp-label {
      display: block;
      font-size: 11px;
      color: $text-secondary;
      margin-bottom: 4px;
    }
    .comp-value {
      font-size: 26px;
      font-weight: 700;
    }
  }
}

.filter-bar {
  background: $bg-card; padding: 12px 16px; border-radius: $radius-md;
  box-shadow: $shadow-md; margin-bottom: 16px; border: 1px solid $border-color;
  .el-select, .el-input { width: 100%; }
}

.pager {
  display: flex; justify-content: flex-end; margin-top: 16px;
  padding: 12px 16px; background: $bg-card; border-radius: $radius-md;
  box-shadow: $shadow-md; border: 1px solid $border-color;
}
</style>
