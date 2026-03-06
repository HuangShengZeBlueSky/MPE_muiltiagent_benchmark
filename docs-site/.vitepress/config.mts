import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(defineConfig({
    title: 'MPE Multi-Agent Benchmark',
    description: 'LLM-Driven Multi-Agent Particle Environment Benchmark Suite',

    // GitHub Pages base path
    base: '/MPE_muiltiagent_benchmark/',

    head: [
        ['link', { rel: 'icon', href: '/favicon.ico' }],
    ],

    // 多语言配置
    locales: {
        zh: {
            label: '中文',
            lang: 'zh-CN',
            link: '/zh/',
            themeConfig: {
                nav: [
                    { text: '首页', link: '/zh/' },
                    { text: '指南', link: '/zh/guide/overview' },
                    { text: '游戏环境', link: '/zh/games/simple' },
                    { text: '进阶', link: '/zh/advanced/prompt-engineering' },
                    { text: 'Leadboard', link: '/zh/advanced/leadboard' },
                ],
                sidebar: {
                    '/zh/guide/': [
                        {
                            text: '入门',
                            items: [
                                { text: '项目概述', link: '/zh/guide/overview' },
                                { text: '系统架构', link: '/zh/guide/architecture' },
                                { text: '快速开始', link: '/zh/guide/quickstart' },
                            ]
                        }
                    ],
                    '/zh/games/': [
                        {
                            text: '🎮 游戏环境',
                            items: [
                                { text: '环境总览', link: '/zh/games/' },
                                { text: 'Simple - 导航', link: '/zh/games/simple' },
                                { text: 'Spread - 协作覆盖', link: '/zh/games/spread' },
                                { text: 'Adversary - 欺骗推理', link: '/zh/games/adversary' },
                                { text: 'Push - 对抗推挤', link: '/zh/games/push' },
                                { text: 'Tag - 追逐捕获', link: '/zh/games/tag' },
                                { text: 'Crypto - 加密通信', link: '/zh/games/crypto' },
                                { text: 'Reference - 多任务通信', link: '/zh/games/reference' },
                                { text: 'Speaker-Listener - 单向通信', link: '/zh/games/speaker-listener' },
                                { text: 'World Comm - 大规模协调', link: '/zh/games/world-comm' },
                            ]
                        }
                    ],
                    '/zh/advanced/': [
                        {
                            text: '⚙️ 进阶主题',
                            items: [
                                { text: '提示词工程', link: '/zh/advanced/prompt-engineering' },
                                { text: 'Benchmark 评测', link: '/zh/advanced/benchmark' },
                                { text: '视频与日志展示', link: '/zh/advanced/media-guide' },
                                { text: 'Leadboard 报告', link: '/zh/advanced/leadboard' },
                            ]
                        }
                    ],
                },
                footer: {
                    message: 'Built with ❤️ for Multi-Agent AI Research',
                    copyright: 'Copyright © 2024-present'
                },
                editLink: {
                    pattern: 'https://github.com/your-repo/edit/main/docs-site/:path',
                    text: '在 GitHub 上编辑此页面'
                },
                lastUpdated: {
                    text: '最后更新于'
                },
                outline: {
                    label: '页面导航',
                    level: [2, 3]
                },
                docFooter: {
                    prev: '上一页',
                    next: '下一页'
                },
            }
        },
        en: {
            label: 'English',
            lang: 'en-US',
            link: '/en/',
            themeConfig: {
                nav: [
                    { text: 'Home', link: '/en/' },
                    { text: 'Guide', link: '/en/guide/overview' },
                    { text: 'Games', link: '/en/games/simple' },
                    { text: 'Advanced', link: '/en/advanced/prompt-engineering' },
                    { text: 'Leadboard', link: '/en/advanced/leadboard' },
                ],
                sidebar: {
                    '/en/guide/': [
                        {
                            text: 'Getting Started',
                            items: [
                                { text: 'Overview', link: '/en/guide/overview' },
                                { text: 'Architecture', link: '/en/guide/architecture' },
                                { text: 'Quick Start', link: '/en/guide/quickstart' },
                            ]
                        }
                    ],
                    '/en/games/': [
                        {
                            text: '🎮 Game Environments',
                            items: [
                                { text: 'Overview', link: '/en/games/' },
                                { text: 'Simple - Navigation', link: '/en/games/simple' },
                                { text: 'Spread - Cooperative', link: '/en/games/spread' },
                                { text: 'Adversary - Deception', link: '/en/games/adversary' },
                                { text: 'Push - Physical Blocking', link: '/en/games/push' },
                                { text: 'Tag - Predator-Prey', link: '/en/games/tag' },
                                { text: 'Crypto - Encryption', link: '/en/games/crypto' },
                                { text: 'Reference - Bidirectional', link: '/en/games/reference' },
                                { text: 'Speaker-Listener', link: '/en/games/speaker-listener' },
                                { text: 'World Comm - Large-Scale', link: '/en/games/world-comm' },
                            ]
                        }
                    ],
                    '/en/advanced/': [
                        {
                            text: '⚙️ Advanced Topics',
                            items: [
                                { text: 'Prompt Engineering', link: '/en/advanced/prompt-engineering' },
                                { text: 'Benchmark Evaluation', link: '/en/advanced/benchmark' },
                                { text: 'Videos & Logs Guide', link: '/en/advanced/media-guide' },
                                { text: 'Leadboard Report', link: '/en/advanced/leadboard' },
                            ]
                        }
                    ],
                },
                footer: {
                    message: 'Built with ❤️ for Multi-Agent AI Research',
                    copyright: 'Copyright © 2024-present'
                },
                outline: {
                    label: 'On this page',
                    level: [2, 3]
                },
            }
        },
    },

    themeConfig: {
        search: {
            provider: 'local'
        },
        socialLinks: [
            { icon: 'github', link: 'https://github.com/your-repo/MPE_muiltiagent_benchmark' }
        ],
    },

    lastUpdated: true,
    cleanUrls: true,

    markdown: {
        lineNumbers: true,
        image: {
            lazyLoading: true
        }
    }
}))
