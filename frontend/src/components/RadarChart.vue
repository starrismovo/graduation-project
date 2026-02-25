<template>
  <div class="radar-chart-wrapper">
    <div ref="chartRoot" class="radar-chart"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

interface TraitData {
  name: string
  score: number
}

const props = withDefaults(
  defineProps<{
    data?: TraitData[]
  }>(),
  {
    data: () => []
  }
)

const chartRoot = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

// 初始化图表
function initChart() {
  if (!chartRoot.value) return

  if (!chart) {
    chart = echarts.init(chartRoot.value)
  }

  if (!props.data || props.data.length === 0) {
    chart.setOption({
      textStyle: {
        color: '#909399'
      },
      graphic: {
        elements: [
          {
            type: 'text',
            left: 'center',
            top: 'center',
            style: {
              text: '暂无数据',
              fill: '#909399',
              fontSize: 16
            }
          }
        ]
      }
    })
    return
  }

  // 转换数据格式
  const traits = props.data.map((item) => item.name)
  const scores = props.data.map((item) => item.score || 0)

  const option: echarts.EChartsOption = {
    radar: {
      indicator: traits.map((name) => ({
        name,
        max: 10
      })),
      shape: 'polygon',
      splitNumber: 4,
      name: {
        textStyle: {
          color: '#606266',
          fontSize: 12
        }
      },
      splitLine: {
        lineStyle: {
          color: ['#e4e7ed', '#e4e7ed', '#e4e7ed', '#e4e7ed']
        }
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(64, 158, 255, 0.05)', 'rgba(64, 158, 255, 0.08)', 'rgba(64, 158, 255, 0.1)', 'rgba(64, 158, 255, 0.12)']
        }
      },
      axisLine: {
        lineStyle: {
          color: '#c0c4cc'
        }
      }
    },
    series: [
      {
        name: '我的特质评分',
        type: 'radar',
        symbolSize: 4,
        data: [
          {
            value: scores,
            name: '评估结果',
            areaStyle: {
              color: 'rgba(102, 126, 234, 0.3)'
            },
            lineStyle: {
              color: '#667eea',
              width: 2
            },
            itemStyle: {
              color: '#667eea',
              borderColor: '#fff',
              borderWidth: 2
            }
          }
        ],
        smooth: true
      }
    ],
    textStyle: {
      color: '#606266'
    }
  }

  chart.setOption(option)
}

// 响应式调整
function handleResize() {
  if (chart) {
    chart.resize()
  }
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

// 监听数据变化
watch(
  () => props.data,
  () => {
    initChart()
  },
  { deep: true }
)

// 清理
defineExpose({
  chart,
  resize: handleResize
})
</script>

<style scoped>
.radar-chart-wrapper {
  width: 100%;
  min-height: 350px;
  display: flex;
  justify-content: center;
}

.radar-chart {
  width: 100%;
  height: 350px;
}
</style>
