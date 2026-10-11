---
name: write-audio
description: 用代码写乐谱并渲染完整音乐（3 分钟级 MP3/WAV）：引擎只做渲染——无自动作曲、无随机预设，曲式/和弦/旋律/织体由乐谱脚本显式给出；多轨合成 + 侧链 + 母带（-14 LUFS）+ 分轨导出。纯 Python + numpy + FFmpeg。当用户想要"写一段音乐/生成一段曲子/做个某风格的配乐"时使用。
---

> **这是一个 Agent Skill（智能体技能）**。把它放进 `~/.codebuddy/skills/write-audio/`（或兼容的 `skills/` 目录），AI 就能"用代码写乐谱 → 渲染出成品音乐"。Python 包名为 `write_audio`。

# write-audio — AI 写乐谱，引擎只管渲染（通用版 v0.2）

**一句话**：乐谱（显式音符）进 → 成品音乐出。没有随机预设、没有自动作曲；
曲式、和弦、旋律、织体全部由你在 Python 乐谱里显式写出；同一乐谱 → **逐样本可复现**。

```python
import write_audio as ca

s = ca.Song(bpm=124)                          # 空谱
kick = s.track("kick")                        # 声明轨道（选乐器）
kick.grid("x...x...x...x...", step=0.25)      # 写音符（显式）
bass = s.track("bass", gain_db=-4)
bass.notes([(0, "A1", 1), (1, "A1", 0.5), (1.5, "C2", 0.5)])
lead = s.track("pluck", name="lead")
lead.notes([(0, "E5", 0.7), (0.75, "C5", 0.7), (1.5, "A4", 2.4)])   # 手写旋律
s.sidechain("kick", "bass", depth_db=-7)      # 侧链
s.length(bars=4)
rep = s.render("out.mp3", stems="stems/")      # 渲染：MP3 + 分轨
```

命令行：

```bash
python -m write_audio song.py --out track.mp3 --stems stems/   # 运行乐谱脚本并渲染
python -m write_audio song.py --check                          # 只看乐谱摘要
```

## 分工（核心理念）

| 层 | 是谁的事 | 说明 |
|---|---|---|
| 曲式、和弦、旋律、织体、每个音符 | **你（AI）** | 在乐谱脚本里显式写出；用 Python 循环/函数组织重复与变奏 |
| 音源合成、多轨混音、侧链、母带、输出 | **引擎** | `song.py`：忠实渲染，不做任何创作决策 |

- **无随机预设**：引擎里没有“自动选音型/自动旋律/自动曲式”；同乐谱两次渲染逐样本相等。
- **不是循环拼接**：每小节、每一轨都是显式音符事件；重复是你在乐谱里写的循环。
- **可验收**：-14 LUFS / 真峰值 ≤ -1 dBTP（流媒体标准）；输出 MP3 / WAV / 任意轨分轨。
- **自包含**：零外部素材，全部波形现场合成（numpy）；只要 Python 3.8+ / numpy / FFmpeg。

## 环境

- Python 3.8+，`pip install numpy`（唯一必需依赖）
- FFmpeg：在 PATH 中，或用环境变量 `CA_FFMPEG` 指定完整路径（mp3 编码 + 响度测量）

## API 速览

```python
# — 乐谱 —
s = ca.Song(bpm=124, beats_per_bar=4, tail=1.5)
t = s.track(inst, name=None, gain_db=0.0, pan=0.0, seed=1)   # inst 见下表
t.note(at, pitch=None, dur=None, vel=1.0)                     # at/dur 单位 = 拍
t.notes([...])            # 批量：数字 / (at,pitch[,dur[,vel]]) / dict 混合
t.hit(at) / t.hits([...]) # 打击乐快捷
t.grid("x...x.x.", step=0.25, at=0)   # 网格谱：'x'=击发，'|' 分隔不推进

s.length(bars=93)                       # 显式曲长（渲染输出 = 曲长 + tail）
s.sidechain(src, dst, depth_db=-7, release=0.18)
s.fade(in_seconds=..., out_seconds=...)
s.stats()                               # 乐谱摘要（不渲染）
s.render(out="x.mp3", wav=None, stems=None, lufs=-14, bitrate=192, tail=1.0)

# — 乐理工具 —
ca.midi("A3") -> 57     ca.freq("A3") -> 220.0
ca.chord("Am7", 3) -> [57,60,64,67]     ca.chord("C/E", 3)   # 斜杠低音
ca.scale("A", "minor", 3) -> 8 个音的 MIDI 列表
```

**乐器**（`s.track(name)` 的 name）：

- 打击乐：`kick` `hat` `clap` `snare` `crash`（无音高，dur 忽略）
- 音高：`bass` `pluck` `bell` `rhodes`（pitch = 音名/MIDI）
- 和弦：`pad`（pitch 可给 `ca.chord(...)` 列表）
- 过渡/纹理：`riser`（dur=扫频长度）`vinyl`（dur 缺省=到曲终）
- 音效单发：`impact` `whoosh` `ding` `click` `riser` `bassdrop` 等 19 种（pitch=半音移调）

详见 `knowledge/instruments.md`。

## 示例曲

- `examples/night-drive/make.py`：《Night Drive》93 小节 / A 小调 / 124 BPM ≈ 3 分钟，
  全部音符显式（鼓型网格谱、手写 hook 旋律、4 小节和弦循环、段落 MA）；渲染 ≈ 35 秒。
- `examples/two-tigers/make.py`：《两只老虎 · 午夜电波》童谣二创（80 小节 ≈ 2 分 37 秒）：
  C 大调 → A 小调、电子舞曲编配、副歌切分加花、原创收尾终止式；渲染 ≈ 39 秒。

```bash
python examples/night-drive/make.py
python examples/two-tigers/make.py
```

## 验证（本仓库自带）

```bash
python examples/night-drive/make.py    # 端到端：渲染 3 分钟曲目，报告 LUFS/真峰值/每轨峰值
python examples/two-tigers/make.py     # 端到端：童谣二创示例
```

渲染报告会打印 `lufs` / `tp`（真峰值）/ 每轨音符数与峰值 dB——用于校准各轨增益，避免某轨盖过其他轨。

## 目录

- `knowledge/write-music.md` — 写乐谱指南（音符写法/编曲方法/母带/套路/避坑）
- `knowledge/instruments.md` — 乐器参考表（音域/默认时值/增益建议）
- `runtime/write_audio/` — 运行时（纯 Python，可读源码学手艺）
- `examples/night-drive/` — 示例曲（含成曲、分轨与分析脚本）
- `examples/two-tigers/` — 童谣二创示例（含成曲与能量图）
- `SKILL.md` / `README.md` / `HANDOFF.md` — 技能说明 / 安装 / 项目状态

## 历史

v0.1.x 是“自动作曲”路线（风格预设 + 随机旋律），已废弃；
v0.2.0 改为“AI 写乐谱、引擎只管渲染”——无随机预设，全部显式。
