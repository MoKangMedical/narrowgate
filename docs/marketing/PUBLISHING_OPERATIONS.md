# 窄门增长发布执行手册

## 1. 每日发布节奏

每天只执行三件事：

1. 从 `data/marketing/launch_production_calendar.md` 确认当天账号、负责人、发布时间、账号状态和素材状态。
2. 从 `data/marketing/publishing_assets.csv` 取当天素材。
3. 按渠道发布小红书、抖音或数字人视频，并使用对应 `landing_url`。
4. 在次日记录曝光、完播、收藏、评论、私信、官网审计开始数和预约线索数。

## 2. 渠道分工

| 渠道 | 目标 | 主要动作 | 核心指标 |
|---|---|---|---|
| 小红书 | 建立信任和搜索沉淀 | 标题冲突、长图清单、真实复盘 | 收藏率、私信数、搜索流量 |
| 抖音 | 获取曝光和评论 | 前3秒钩子、30-60秒口播、评论区提问 | 完播率、评论率、主页访问 |
| 数字人 | 稳定规模化发布 | 每日一问、课程导览、机构版口播 | 连续发布天数、预约试点数 |

## 3. UTM规则

所有外部渠道链接都使用同一套规则：

```text
https://narrowgatemind.top/?utm_source={channel}&utm_medium=social&utm_campaign=narrowgate_launch_30d&utm_content=day{day}_{channel}
```

已生成的链接见：

- `data/marketing/utm_links.json`
- `data/marketing/publishing_assets.csv`
- `data/marketing/launch_production_calendar.md`
- `data/marketing/launch_production_calendar.csv`
- `data/marketing/week1_publish_checklist.json`
- `data/marketing/week1_publish_scripts.md`
- `data/marketing/digital_human_storyboards.json`

## 4. 发布前质量门

- 不承诺治愈、疗效或保证改变。
- 不制造焦虑式恐吓，不羞辱用户。
- 不替代医疗、心理治疗或危机干预。
- 引导用户做官网灵魂审计或课程试听，不诱导私下交易。
- 发布前核对平台审核提示，必要时降低绝对化表达。

## 5. 线索跟进

官网预约会进入 `/api/marketing/leads`。该接口需要 `NARROWGATE_ADMIN_TOKEN`，避免公开暴露联系方式。

运营可用：

```bash
curl -H "X-Admin-Token: $NARROWGATE_ADMIN_TOKEN" \
  https://narrowgatemind.top/api/marketing/leads.csv
```

公开看板只展示不含联系方式的汇总：

```bash
curl https://narrowgatemind.top/api/marketing/leads/summary
```

## 6. 发布状态与数据回填

每条内容发布后，记录发布链接、状态和24小时数据：

```bash
curl -X POST https://narrowgatemind.top/api/marketing/posts \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: $NARROWGATE_ADMIN_TOKEN" \
  -d '{
    "content_id": "day01_xiaohongshu",
    "day": 1,
    "channel": "xiaohongshu",
    "title": "你不是不自律，你是在逃避一个真问题",
    "status": "published",
    "publish_url": "替换为发布后的链接",
    "metrics": {
      "views": 0,
      "likes": 0,
      "comments": 0,
      "favorites": 0,
      "shares": 0,
      "leads": 0
    },
    "notes": "评论区高频问题"
  }'
```

公开汇总：

```bash
curl https://narrowgatemind.top/api/marketing/posts/summary
```

增长周报：

```bash
curl https://narrowgatemind.top/api/marketing/posts/weekly-report
curl https://narrowgatemind.top/api/marketing/posts/weekly-report.md
```

## 7. 每周复盘

每周只做一次内容策略调整：

1. 保留收藏率最高的3类标题。
2. 删除完播率最低的2类开头。
3. 把私信里重复出现的问题转成下一周课程导览脚本。
4. 把机构咨询问题整理为数字人机构版口播。
