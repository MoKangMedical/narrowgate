# Qwen TTS 配置指南

窄门课程语音建议使用 `qwen3-tts-instruct-flash` 生成课程导师式音频。本文只记录本地配置方式，不保存真实密钥。

> 当前未来课程音频主标准已调整为 `DeepSeek 口播稿 + edge_tts + zh-CN-YunyangNeural + ffmpeg loudnorm + MP3`。Qwen TTS 保留为可选方案或后续对比方案。主标准见 `docs/AUDIO_GENERATION_STANDARD.md`。

## 1. 已安装的本地依赖

项目需要：

- `dashscope>=1.25`
- `requests>=2.31`
- `ffmpeg`

验证命令：

```bash
python3 scripts/check_qwen_tts_setup.py
```

## 2. 需要你在阿里云完成的账号权限

这些步骤涉及账号、计费和密钥，不能由代码自动替你申请：

1. 登录阿里云 Model Studio / 百炼控制台。
2. 开通 DashScope / 百炼模型服务。
3. 确认账号有可用额度或已完成必要的计费授权。
4. 创建 API Key。
5. 确认所在地域：北京或新加坡。API Key 与地域接口需要匹配。
6. 确认账号可调用 Qwen TTS 模型，优先选择 `qwen3-tts-instruct-flash`。

## 3. 本机环境变量配置

不要把真实 Key 写进 GitHub。建议只在终端里临时设置：

```bash
export DASHSCOPE_API_KEY="你的API_KEY"
export DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/api/v1"
export QWEN_TTS_MODEL="qwen3-tts-instruct-flash"
export QWEN_TTS_VOICE="Cherry"
export QWEN_TTS_LANGUAGE="Chinese"
export QWEN_TTS_INSTRUCTIONS="请用沉稳、温和、低速、有停顿的中文课程导师声音朗读。语气不要表演化，要像陪伴一个人安静地面对自己。重要句子前后稍作停顿，整体适合自我觉察课程。"
```

新加坡地域使用：

```bash
export DASHSCOPE_BASE_URL="https://dashscope-intl.aliyuncs.com/api/v1"
```

## 4. 配置验证

```bash
python3 scripts/check_qwen_tts_setup.py
```

全部配置正确时会看到：

```text
Qwen TTS local setup looks ready.
```

## 5. 窄门推荐策略

先生成 1 门课试听，再批量替换 100 门导览音频：

1. 试听：`socratic_introspection`
2. 小批量：12 门核心课
3. 全量：100 门导览音频
4. 进阶：每章讲解音频和洞察引导音频

当前项目已有音频目录结构：

```text
data/courses/<course_id>/audio/intro.txt
data/courses/<course_id>/audio/intro.m4a
```

后续接入 Qwen TTS 时，应优先复用这个结构，避免改动页面播放逻辑。
