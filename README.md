# 智能音乐工具

## 功能
- 在logic pro里面，还原乐器的音符，用用户所需要的音源和音色
- 精准分离完所有的乐器+人声
- 制作midi文件

## 要求

- 全部自动化完成
- 工作内容完全自动化

## MVP

这一版只做分轨之后的固定流水线。分轨来自 Audio Jam 导出的音频。Python 状态机按写死的顺序调用五步，不由模型决定先跑哪一步。

1. `ingest`：读取分轨，认人声、鼓、贝斯、吉他、钢琴、其他
2. `transcribe`：为鼓、贝斯、人声、钢琴写 MIDI
3. `score`：写每轨置信度
4. `duty`：只返回 `continue`、`audio_only` 或 `handoff`
5. `finish`：落盘。`done/` 里已有的歌不会被覆盖

吉他和其他轨在这一版标成低置信度，只保留音频。

## 朋友测试

在仓库根目录执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m music_tool.download_models
```

把一首歌的分轨放进 `inbox/<歌名>/`。文件名需要能对上轨道，例如 `vocals.wav`、`drums.wav`、`bass.wav`、`guitar.wav`、`piano.wav`、`other.wav`。也认中文名：人声、鼓、贝斯、吉他、钢琴、其他。

```bash
python -m music_tool inbox/<歌名>
```

检查：

- `logs/<歌名>.log` 里按顺序出现 step 1 到 step 5，没有跳步
- `done/<歌名>/job.json` 存在，该有 MIDI 的轨在 `done/<歌名>/midi/`
- `job.json` 里的 `action` 只有 `continue`、`audio_only`、`handoff` 三种
- `handoff` 的结果在 `review/<歌名>/`，不会写进 `done/`
- 再跑一次同一首歌时，日志出现 `skip already_done`，`done/` 里的文件不变

默认值班员是规则后端。要改用本机小模型时：

```bash
DUTY_BACKEND=model DUTY_MODEL_PATH=/本机模型路径 python -m music_tool inbox/<歌名>
```

模型只能回答这三个词。答偏了会记进日志，并改用规则后端把这首歌跑完。
