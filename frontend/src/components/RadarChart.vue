<template>
  <div class="radar-chart-wrapper">
    <div ref="chartRoot" class="radar-chart"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

interface TraitData {
  name: string
  score: number
}

const props = withDefaults(
  defineProps<{
    data?: TraitData[]
    size?: number
  }>(),
  {
    data: () => [],
    size: 380
  }
)

const chartRoot = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

function initChart() {
  if (!chartRoot.value) return

  if (!chart) {
    chart = echarts.init(chartRoot.value)
  }

  if (!props.data || props.data.length === 0) {
    chart.setOption({
      graphic: {
        elements: [
          {
            type: 'text',
            left: 'center',
            top: 'center',
            style: {
              text: '暂无评估数据',
              fill: '#c0c4cc',
              fontSize: 14,
              fontWeight: 400
            }
          }
        ]
      }
    })
    return
  }

  const traits = props.data.map((item) => item.name)
  const scores = props.data.map((item) => item.score || 0)

  const option = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255,255,255,0.96)',
      borderColor: '#e4e7ed',
      borderWidth: 1,
      padding: [10, 14],
      textStyle: { color: '#303133', fontSize: 13 },
      formatter: (params: any) => {
        const data = params.data
        if (!data || !data.value) return ''
        return traits
          .map((name, i) => {
            const val = data.value[i]
            const color = val >= 7 ? '#67c23a' : val >= 4 ? '#409eff' : '#e6a23c'
            return `<span style="color:${color};font-weight:600">●</span> ${name}：<b>${val.toFixed(1)}</b> / 10`
          })
          .join('<br/>')
      }
    },
    radar: {
      indicator: traits.map((name) => ({
        name,
        max: 10
      })),
      center: ['50%', '52%'],
      radius: '68%',
      shape: 'polygon',
      splitNumber: 5,
      name: {
        color: '#4a5568',
        fontSize: 13,
        fontWeight: 500,
        padding: [2, 0]
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(148, 163, 184, 0.25)',
          width: 1
        }
      },
      splitArea: {
        areaStyle: {
          color: [
            'rgba(99, 102, 241, 0.02)',
            'rgba(99, 102, 241, 0.04)',
            'rgba(99, 102, 241, 0.06)',
            'rgba(99, 102, 241, 0.08)',
            'rgba(99, 102, 241, 0.10)'
          ]
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(148, 163, 184, 0.2)'
        }
      }
    },
    series: [
      {
        name: '心理特质',
        type: 'radar',
        symbol: 'circle',
        symbolSize: 6,
        data: [
          {
            value: scores,
            name: '评估结果',
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(99, 102, 241, 0.35)' },
                { offset: 1, color: 'rgba(139, 92, 246, 0.08)' }
              ])
            },
            lineStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#6366f1' },
                { offset: 1, color: '#8b5cf6' }
              ]),
              width: 2.5,
              shadowColor: 'rgba(99, 102, 241, 0.3)',
              shadowBlur: 6
            },
            itemStyle: {
              color: '#6366f1',
              borderColor: '#fff',
              borderWidth: 2,
              shadowColor: 'rgba(99, 102, 241, 0.4)',
              shadowBlur: 4
            }
          }
        ],
        animationDuration: 1200,
        animationEasing: 'cubicInOut'
      }
    ]
  }

  chart.setOption(option, true)
}

function handleResize() {
  chart?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
  chart = null
})

watch(
  () => props.data,
  () => initChart(),
  { deep: true }
)

defineExpose({ chart, resize: handleResize })
</script>

<style scoped>
.radar-chart-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.radar-chart {
  width: v-bind("size + 'px'");
  height: v-bind("size + 'px'");
}
</style>
