# 窄门课程音频生成标准

未来课程音频统一使用这条链路：

```text
课程正文/元数据 -> 150-230字课程口播稿 -> Edge Neural TTS -> ffmpeg 响度与格式统一 -> 网页/小程序播放
```

## 1. 课程口播稿

不要直接把课程正文丢给 TTS。每条音频先生成 150-230 字左右的自然导入稿，让它听起来像老师在讲课。

优先使用 DeepSeek 生成口播稿；没有 `DEEPSEEK_API_KEY` 时，脚本会使用本地模板生成同规格导入稿。

口播稿必须包含：

- 这门课面对的真实问题
- 用户最可能走的宽门
- 本课要求穿越的窄门
- 今天能完成的最小行动
- 行动后的记录方式

## 2. 神经 TTS

默认 TTS：

```text
engine: edge_tts
voice: zh-CN-YunyangNeural
rate: -8%
pitch: -2Hz
```

声音目标：中文男声、沉稳、慢一点、低一点，适合自我觉察课程。

## 3. ffmpeg 后期规格

所有音频统一处理：

```text
loudnorm=I=-16:TP=-1.5:LRA=9
sample_rate: 24000Hz
channels: mono
format: MP3
bitrate: 48kbps 或 64kbps
```

网页端使用：

```html
<audio controls>
  <source src="audio/intro.mp3" type="audio/mpeg">
</audio>
```

## 4. 生成命令

试听单门课程口播稿：

```bash
python3 scripts/generate_course_audio_neural.py --course-id socratic_introspection --dry-run
```

生成单门课程音频：

```bash
python3 scripts/generate_course_audio_neural.py --course-id socratic_introspection --force
```

生成前 12 门核心课：

```bash
python3 scripts/generate_course_audio_neural.py --limit 12 --force
```

生成全部课程：

```bash
python3 scripts/generate_course_audio_neural.py --force
```

## 5. DeepSeek 配置

如果需要 DeepSeek 写口播稿，配置：

```bash
export DEEPSEEK_API_KEY="你的DeepSeek API Key"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
export DEEPSEEK_MODEL="deepseek-v4-flash"
```

如果不配置，脚本会用本地口播稿模板。

## 6. 质量审计

```bash
python3 scripts/audit_neural_audio.py
```

A级标准：

- MP3
- 24000Hz
- 单声道
- 48-64kbps 附近
- 25-120 秒
- 文件存在且可被 `ffprobe` 读取
