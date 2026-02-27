# Videos & Logs Guide

## Embedding Videos

### Method 1: HTML5 Video Tag (Recommended for MP4)

Place MP4 files in `docs-site/public/videos/`, then use:

```html
<video controls width="100%" style="max-width: 600px; border-radius: 8px;">
  <source src="/videos/simple_demo.mp4" type="video/mp4">
</video>
```

### Method 2: GIF

```markdown
![Demo](/videos/simple_demo.gif)
```

### Method 3: External Hosting (YouTube/Bilibili)

```html
<iframe width="560" height="315" src="https://www.youtube.com/embed/VIDEO_ID" frameborder="0" allowfullscreen></iframe>
```

## Embedding Logs

### Inline JSON Block

````markdown
```json
{"step": 5, "agent": "agent_0", "action": [0, 0.8, 0, 0, 0.5], "reward": -0.34}
```
````

### Collapsible Sections

```markdown
::: details Click to view full log
```json
[{"step": 0, ...}, {"step": 1, ...}]
```
:::
```

## Deploying to GitHub Pages

1. Build: `cd docs-site && npm run docs:build`
2. Add GitHub Actions workflow (see [Chinese guide](/zh/advanced/media-guide) for full YAML)
3. Enable Pages in repo Settings → Source: GitHub Actions
4. Update `base` in `config.mts` if needed
