# WebGazer Blink Detection and Fixation Tuning

> 目标 / Goal：让阅读器在用户稳定注视屏幕某个区域时显示粉色 dot，并减少眨眼或 gaze 不可靠时的错误显示。
>
> 说明：本文记录之前尝试过的 blink detection 方案。项目当前采用的版本已经移除了 blink detection，改为只用 fixation 判断。当前实现请看同一文件夹里的 `webgazer_final_fixation_summary.md`。

## 1. 最终结果 / Result

我们尝试过在 WebGazer 的 gaze 结果上增加 blink detection，并调整 fixation 参数。

目前确认有效、让粉色 dot 更快出现的改动是 fixation 参数：

- `200px`：相邻 gaze 点之间允许的最大移动距离。
- `200ms`：需要保持在这个距离范围内的最短时间。

PR #373 带来的平滑处理改善了定位表现，但它本身不会判断用户是否眨眼。blink detection 的尝试和 fixation 的效果需要分开理解。

## 2. 问题是什么 / What was the problem?

WebGazer 会连续预测用户正在看的屏幕位置。预测结果有时会抖动；眨眼时，预测位置也可能突然变化，或继续产生一个看起来有效的坐标。

最初的 fixation 参数比较严格。用户需要等待较久，粉色 dot 才出现。我们希望更快显示用户大致注视的区域，同时尽量避免把短暂的错误位置当成稳定注视。

## 3. 需要解决什么 / What needed to be solved?

- 判断 gaze 是否在屏幕上某个区域附近保持了一段时间。
- 当 gaze 突然移动到另一个区域时，重新开始计时。
- 观察眨眼时的错误位置是否能被识别并避免显示。
- 不要把平滑定位和眨眼检测当成同一件事。

## 4. 尝试过的方案 / Solutions tried

### A. 使用 WebGazer PR #373 的平滑处理

这个 PR 改善 gaze 坐标的稳定性，因此定位看起来更准。它处理的是 gaze 的抖动，不是眨眼识别。

### B. 检查 WebGazer 是否返回 gaze 数据

没有 gaze 数据时可以清除当前显示。但眨眼期间，WebGazer 有时仍会返回坐标，所以“有坐标”不代表眼睛一定睁开。

### C. 使用眼睛闭合比例（EAR）

EAR 是从眼睛周围的特征点估算眼睛张开程度的一种方法。眼睛闭合时 EAR 通常会变小。这个方法需要可靠的眼部特征点；在当前项目中，它没有稳定解决眨眼造成的 dot 移动。

### D. 检查眼睛区域的亮度变化

另一个尝试是观察眼睛区域在闭眼时的亮度变化，并把它作为 blink detection 的辅助信号。它会受到摄像头、光线和脸部角度影响，因此不能保证每次眨眼都能准确识别。

### E. 使用 fixation 判断稳定注视

Fixation（注视）判断 gaze 是否在一段时间内停留在一个范围内。我们调整了距离和时间参数，发现 `200px + 200ms` 的显示效果更符合“看哪里的大概区域”这个用途。

## 5. 结果和结论 / Results and conclusion

- PR #373 改善了定位的平滑度。
- `200px + 200ms` 改善了粉色 dot 出现得太慢的问题。
- EAR 和亮度变化方案没有可靠解决当前遇到的眨眼问题。
- 这些实验说明，定位更平滑不等于能够准确识别眨眼。

## 6. 如何复现之前的尝试 / How to reproduce the earlier attempts

1. 查看 `frontend/src/hooks/useWebGazer.ts` 中 gaze listener 如何接收坐标，以及 fixation 如何开始、重置和确认。
2. 查看 `frontend/src/components/ConfusionPanel.tsx` 中粉色 dot 如何根据确认后的 fixation 显示。
3. 对比 WebGazer PR #373 的平滑效果和应用自己的 fixation 判断。两者作用不同。
4. 如需重新测试 blink detection，一次只测试一种信号（例如 EAR），并分别记录眨眼时 WebGazer 是否仍返回坐标。

## 7. 以后如何处理类似问题 / How to approach similar problems

1. 先把问题拆开：坐标抖动、眨眼、dot 出现过慢是不同问题。
2. 找到项目中实际显示 dot 的代码，确认它依赖什么数据。
3. 一次只调整一个参数或方案，并实际测试。
4. 记录修改前后的结果，以及仍未解决的问题。
5. 使用简单、符合产品目标的规则；如果之后确实需要眨眼识别，再单独增加和验证 blink detection。

## 参考 / References

- [WebGazer PR #373](https://github.com/brownhci/WebGazer/pull/373/changes)
- [WebGazer issue #114](https://github.com/brownhci/WebGazer/issues/114)
- [Realtime eye tracking with Supabase and WebGazer.js](https://dev.to/laznic/building-a-realtime-eye-tracking-experience-with-supabase-and-webgazerjs-3llj)
