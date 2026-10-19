# WebGazer 最终 Fixation 方案 / Final Fixation Approach

这份文档说明项目当前如何显示 gaze 的粉色 dot，以及如何复现这个版本。

This document explains how the current version shows the pink gaze dot and how to reproduce it.

## 1. 要解决的问题 / The problem

WebGazer 会连续给出用户可能正在看的屏幕坐标。单个坐标可能会抖动或突然跳动。如果每收到一个坐标就显示 dot，dot 看起来会不稳定。

WebGazer continuously estimates where the user is looking. A single estimate can jump, so showing a dot for every estimate can make it unstable.

## 2. 当前规则 / Current rule

项目把一连串相近的 gaze 坐标当作一次 fixation（注视）：

The app treats a sequence of nearby gaze coordinates as a fixation:

1. 收到第一个坐标时，记下位置和时间，作为当前区域的起点。
2. 后续坐标离起点超过 `200px` 时，把它当作用户看向了另一个区域，并从新位置重新计时。
3. 如果 gaze 在 `200ms` 内一直留在 `200px` 范围内，就确认 fixation，并显示粉色 dot。
4. 如果 WebGazer 没有给出坐标，就清除当前显示。

1. When the first coordinate arrives, save its position and time as the start of a candidate region.
2. If a later coordinate is more than `200px` away, treat it as a new region and restart the timer there.
3. If gaze stays within `200px` for `200ms`, confirm a fixation and show the pink dot.
4. If WebGazer provides no coordinate, clear the current display.

代码位于 `frontend/src/hooks/useWebGazer.ts`；粉色 dot 根据确认后的 fixation 在 `frontend/src/components/ConfusionPanel.tsx` 中显示。

The logic is in `frontend/src/hooks/useWebGazer.ts`. `frontend/src/components/ConfusionPanel.tsx` displays the pink dot for a confirmed fixation.

## 3. `200px` 和 `200ms` 是什么意思？ / What do `200px` and `200ms` mean?

- `200px` 是屏幕上的距离，用来定义“还在同一个大致区域”。它不是眼球在现实空间移动了 200 像素。
- `200ms` 是时间，等于 0.2 秒。gaze 需要在这个时间里留在该区域附近，系统才确认 fixation。

- `200px` is a screen distance used to define the same approximate region. It is not a measurement of the eye moving in physical space.
- `200ms` is 0.2 seconds. Gaze must stay near that region for this long before the app confirms a fixation.

这两个值是根据实际使用感受调整的起点，不是适用于所有屏幕、用户和摄像头的通用标准。较小的距离或较长的时间可能让 dot 更稳定，但也可能让它更慢出现。

These values are practical tuning choices, not universal standards for every screen, user, or camera. A smaller distance or longer time may make the dot steadier but can also delay it.

## 4. 为什么移除了 blink logic？ / Why was blink logic removed?

当前功能目标是显示用户大致在看哪个屏幕区域。EAR、眼睛区域亮度和 `isBlinking` 等眨眼判断曾经尝试过，但在当前设备条件下没有可靠解决 dot 跟着眨眼移动的问题。最终版本只保留 fixation 的距离和时间判断。

The current goal is to show the approximate screen region the user is looking at. EAR, eye-region brightness, and `isBlinking` were tried, but did not reliably stop the dot from moving during blinks under the current setup. The final version keeps only the fixation distance and time checks.

需要知道这个限制：如果用户眨眼时 WebGazer 仍持续返回位于 `200px` 范围内的坐标，fixation 规则本身可能仍会保留 dot。它不是眨眼检测器。

One limitation remains: if WebGazer continues returning coordinates within `200px` during a blink, the fixation rule may keep the dot visible. This rule does not detect blinks.

## 5. 如何复现 / How to reproduce

1. 打开 `frontend/src/hooks/useWebGazer.ts`，找到 WebGazer 的 gaze listener。
2. 确认新坐标与当前 fixation 起点的距离超过 `200px` 时，会重置起点和计时。
3. 确认在 `200ms` 内坐标留在该范围时，会设置 fixation。
4. 打开 `frontend/src/components/ConfusionPanel.tsx`，确认粉色 dot 使用确认后的 `fixation` 坐标显示。
5. 在浏览器中完成校准并实际观察 dot：分别测试稳定注视、快速移动视线和眨眼。记录结果，再一次只调整一个值。

1. Open the gaze listener in `frontend/src/hooks/useWebGazer.ts`.
2. Check that a coordinate more than `200px` from the current fixation start resets the start point and timer.
3. Check that a fixation is set after coordinates remain in range for `200ms`.
4. In `frontend/src/components/ConfusionPanel.tsx`, confirm the pink dot uses the confirmed `fixation` coordinate.
5. Calibrate in the browser and observe the dot while looking steadily, moving your eyes quickly, and blinking. Record the results and change one value at a time.

## 6. 总结 / Summary

当前版本用 `200px + 200ms` 确认用户注视的大致区域。这个调整让 dot 更快出现。它改善的是 fixation 显示规则，不负责识别眨眼。

The current version uses `200px + 200ms` to confirm an approximate gaze region. This made the dot appear sooner. It tunes fixation display; it does not detect blinks.
