# 视频与日志展示指南

本页说明如何在文档站点中嵌入游戏演示视频和 JSON 日志。

## 视频展示

### 方法 1: HTML5 Video 标签（推荐用于 MP4）

将 MP4 文件放入 `docs-site/public/videos/` 目录，然后在 Markdown 中使用：

```html
<video controls width="100%" style="max-width: 600px; border-radius: 8px;">
  <source src="/videos/simple_demo.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>
```

**效果预览**：视频将以带控制栏的播放器形式嵌入页面。

### 方法 2: GIF 动图

将 GIF 文件放入 `docs-site/public/videos/` 目录：

```markdown
![Simple Game Demo](/videos/simple_demo.gif)
```

::: tip 生成 GIF
使用 ffmpeg 将 MP4 转换为 GIF：
```bash
ffmpeg -i simple_demo.mp4 -vf "fps=10,scale=400:-1" -loop 0 simple_demo.gif
```
:::

### 方法 3: 外部视频托管

如果视频较大，建议上传到视频平台后嵌入：

```html
<!-- YouTube -->
<iframe width="560" height="315" 
  src="https://www.youtube.com/embed/VIDEO_ID"
  frameborder="0" allowfullscreen>
</iframe>

<!-- Bilibili -->
<iframe src="//player.bilibili.com/player.html?bvid=BV_ID"
  width="560" height="315" frameborder="0" allowfullscreen>
</iframe>
```

### 视频文件组织

建议的目录结构：

```
docs-site/public/
├── videos/
│   ├── simple_demo.mp4       # Simple 演示
│   ├── spread_demo.mp4       # Spread 演示
│   ├── adversary_demo.mp4    # Adversary 演示
│   ├── push_demo.mp4
│   ├── tag_demo.mp4
│   ├── crypto_demo.mp4
│   ├── reference_demo.mp4
│   ├── speaker_listener_demo.mp4
│   └── world_comm_demo.mp4
└── gifs/
    ├── simple_demo.gif
    └── ...
```

### 从 Benchmark 结果获取视频

运行 benchmark 后生成的视频可以直接复制到 docs 目录：

```bash
# 复制精选视频到文档站
cp results/benchmarks/spread/spread_ep1.mp4 docs-site/public/videos/spread_demo.mp4
```

## 日志展示

### 方法 1: 内联 JSON 代码块

直接在 Markdown 中展示关键日志片段：

````markdown
```json
{
  "step": 5,
  "agent": "agent_0",
  "observation": {
    "vel": [0.12, -0.05],
    "landmark_rel": [-0.15, 0.08]
  },
  "action": [0.0, 0.3, 0.0, 0.0, 0.1],
  "thought": "Almost at target, reducing thrust to avoid overshoot",
  "reward": -0.03
}
```
````

### 方法 2: 可折叠日志

使用 VitePress 的 `details` 语法展示完整日志：

```markdown
::: details 点击查看完整日志
```json
[
  {"step": 0, "agent": "agent_0", "action": [...], "reward": -0.85},
  {"step": 1, "agent": "agent_0", "action": [...], "reward": -0.62},
  ...
]
```
:::
```

### 方法 3: 日志分析表格

将 JSON 日志中的关键数据整理为表格：

```markdown
| Step | Agent | Action | Reward | 策略 |
|:----:|:-----:|:------:|:------:|:-----|
| 0 | agent_0 | [0, 0.8, 0, 0, 0.6] | -0.85 | 向左上冲刺 |
| 5 | agent_0 | [0, 0.3, 0, 0, 0.1] | -0.12 | 接近目标，减速 |
| 10 | agent_0 | [0, 0, 0, 0, 0] | -0.02 | 到达目标，停止 |
```

### 方法 4: 自定义 Vue 组件（高级）

创建一个 Vue 组件来交互式展示 JSON 日志：

```
docs-site/.vitepress/
└── components/
    └── LogViewer.vue
```

```vue
<!-- .vitepress/components/LogViewer.vue -->
<template>
  <div class="log-viewer">
    <div class="controls">
      <button @click="prevStep" :disabled="currentStep <= 0">◀ 上一步</button>
      <span>Step {{ currentStep }} / {{ maxStep }}</span>
      <button @click="nextStep" :disabled="currentStep >= maxStep">下一步 ▶</button>
    </div>
    <pre class="log-content">{{ currentEntry }}</pre>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({ data: Array })
const currentStep = ref(0)
const steps = computed(() => props.data?.filter(e => 'step' in e) ?? [])
const maxStep = computed(() => steps.value.length - 1)
const currentEntry = computed(() =>
  JSON.stringify(steps.value[currentStep.value], null, 2)
)
function prevStep() { if (currentStep.value > 0) currentStep.value-- }
function nextStep() { if (currentStep.value < maxStep.value) currentStep.value++ }
</script>
```

在 Markdown 中使用：

```markdown
<LogViewer :data="logData" />

<script setup>
import LogViewer from '../.vitepress/components/LogViewer.vue'
const logData = [/* 你的JSON数据 */]
</script>
```

## 实验结果展示

### 对比表格模板

```markdown
## 模型对比结果

| Environment | Qwen-3-Max | DeepSeek-Chat | GPT-4o |
|:------------|:----------:|:-------------:|:------:|
| Simple      | -0.123 ± 0.05 | -0.234 ± 0.08 | -0.089 ± 0.03 |
| Spread      | -12.3 ± 1.2 | -15.6 ± 2.1 | -10.1 ± 0.9 |
| Tag         | -5.4 ± 3.2 | -8.1 ± 4.5 | -3.2 ± 2.1 |
```

### 图表嵌入

```markdown
<!-- 静态图片 -->
![Reward Comparison Chart](/charts/reward_comparison.png)

<!-- 建议使用 matplotlib 或 echarts 生成 -->
```

### 生成图表的 Python 脚本

```python
import json
import matplotlib.pyplot as plt
import numpy as np

# 加载 benchmark 结果
envs = ["simple", "spread", "adversary", "push", "tag",
        "crypto", "reference", "speaker_listener", "world_comm"]

means = []
stds = []
for env in envs:
    with open(f"results/benchmarks/{env}_summary.json") as f:
        data = json.load(f)
    means.append(data["mean_reward"])
    stds.append(data["std_reward"])

# 绘制柱状图
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(envs))
ax.bar(x, means, yerr=stds, capsize=5, color='steelblue', alpha=0.8)
ax.set_xticks(x)
ax.set_xticklabels(envs, rotation=45, ha='right')
ax.set_ylabel('Mean Reward')
ax.set_title('MPE Benchmark Results')
plt.tight_layout()
plt.savefig("docs-site/public/charts/benchmark_results.png", dpi=150)
```

## 部署到 GitHub Pages

### 1. 构建站点

```bash
cd docs-site
npm install
npm run docs:build
```

### 2. 配置 GitHub Actions

在仓库根目录创建 `.github/workflows/deploy-docs.yml`：

```yaml
name: Deploy Docs

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - name: Install and Build
        run: |
          cd docs-site
          npm install
          npm run docs:build
      - uses: actions/configure-pages@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: docs-site/.vitepress/dist
      - name: Deploy
        id: deployment
        uses: actions/deploy-pages@v4
```

### 3. 启用 GitHub Pages

在仓库 Settings → Pages → Source 选择 **GitHub Actions**。

### 4. 设置 Base 路径

如果仓库名非 `username.github.io`，需要在 `config.mts` 中设置：

```typescript
export default defineConfig({
  base: '/MPE_muiltiagent_benchmark/',
  // ...
})
```
