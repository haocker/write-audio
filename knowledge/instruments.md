# 乐器参考（write_audio v0.2）

`INST` 注册表（`ca.INST`）里六类 kind，共 12 种乐器 + 19 种音效。

## 打击乐（kind=perc）

无音高（pitch 忽略）；`dur` 忽略，音频长度固定。

| 名称 | 长度 | 特点 | 建议 gain_db | 典型用法 |
|---|---|---|---|---|
| `kick` | 0.4s | 150→45Hz 扫频 + 点击 | 0 | 每拍四踩；build 加倍 |
| `hat` | 0.07s | 7kHz 高通噪声 | -10 | 8 分/16 分/反拍 |
| `clap` | 0.22s | 3 连拍噪声叠层 | -4 | 2/4 拍 |
| `snare` | 0.2s | 196Hz 体音 + 噪声 | -8 | 2/4 拍（替代 clap）；roll |
| `crash` | 1.7s | 金属分音 + 长衰减 | -9 | 段落头 |

## 音高乐器（kind=tone）

pitch 必填（音名/MIDI）；`dur`=音符时值（拍），缺省用默认时值。

| 名称 | 默认时值 | 音色 | 建议 gain_db | 音域建议 |
|---|---|---|---|---|
| `bass` | 1.0 拍 | 锯齿双振荡 + 低通 880Hz | -3 | A1~C2（MIDI 29-36） |
| `pluck` | 0.5 拍 | 短荥光滑波（琶音/lead） | -8（arp）/-6（lead） | C4~E6 |
| `bell` | 1.5 拍 | 非谐钟声（2.76×/5.4×） | -9 | C5~C6 点亮色 |
| `rhodes` | 1.5 拍 | 电钢（含 4.6Hz 顫音） | -9 | A3~E5 主歌旋律 |

## 和弦（kind=poly）

| 名称 | 默认时值 | 说明 |
|---|---|---|
| `pad` | 4.0 拍 | 多振荡去谐和声垫；pitch 可给 `ca.chord("Am7", 3)` 或音名列表 |

- **每小节一个 pad、和弦逐小节对齐**；建议 gain_db 约 -14。
- 常用包装：`ch + [ch[0] + 12]`（加高八度根音，更饱满）。

## 过渡 / 纹理

| 名称 | kind | 说明 |
|---|---|---|
| `riser` | riser | 扫频上升（f0=160→f1=1500Hz），`dur`=扫频长度（拍），常用 4~8 拍 |
| `vinyl` | texture | 黑胶底噪；只要一个音符（`vinyl.note(beat(1))`），dur 缺省 = 铺到曲终 |

## 音效单发（kind=sfx，19 种）

`pitch` = **半音移调**（数值；0=原位）。可当乐器轨用：

```python
dings = s.track("ding", gain_db=-8)
dings.note(beat(64), 12)        # +12 半音
s.track("whoosh", gain_db=-9).note(beat(16))   # 转场扫声
```

| 名称 | 长度 | 用途 |
|---|---|---|
| `impact` | 0.8s | 重击落地（推位） |
| `punch` / `pop` | 0.4s / 0.16s | 短促点缀 |
| `swish` / `swipe` / `whoosh` | 0.28~0.5s | 转场扫声 |
| `click` / `tick` | 0.05s / 0.04s | 节奏点缀 |
| `ding` / `chime` | 0.9s / 1.2s | 提示/装饰 |
| `success` / `error` | 0.5s / 0.4s | 状态音 |
| `riser` | 1.2s | 短上升（另有同名乐器版） |
| `glitch` / `sparkle` | 0.3s / 0.8s | 数字感/闪烁 |
| `notification` / `typing` | 0.7s / 1.0s | 通知/打字 |
| `bassdrop` / `shutter` | 1.0s / 0.18s | 低频下降/快门 |

## 引擎与乐器的边界（重要）

- 乐器的一切参数（除 seed 微噪声）都是固定算法；想改声音细节 = 改 `audio.py` 里的合成函数（同步加测试）。
- 所有乐器确定性合成：同参数同输出（噪声用固定 seed；每音符 seed = `track.seed + round(at*331)`）。
- `track(seed=...)` 可以换一轨的噪声纹理（kick/hat 的细节），但听感差异很小，不建议依赖。
