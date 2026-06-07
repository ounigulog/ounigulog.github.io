---
title: 'STM32中断概念详解：从GPIO引脚到CPU的完整旅程'
date: 2026-06-04
draft: false
categories:
  - 嵌入式STM32学习
tags:
  - STM32
  - 中断
  - NVIC
  - EXTI
  - GPIO
  - 嵌入式
  - 寄存器
cover: /images/covers/reimu.png
banner: images/banner.webp
description: '从生活中的中断类比起步，逐步深入STM32的中断概念：信号如何从GPIO引脚→EXTI→NVIC→CPU，异常向量表的结构，优先级抢占规则，以及用按键中断控制LED的实战案例。面向初学者，逐层剥开中断的神秘面纱。'
keywords:
  - STM32中断
  - NVIC
  - EXTI
  - 异常向量表
  - 中断优先级
  - GPIO中断
  - 嵌入式
toc: true
math: false
mermaid: false
comments: true
outdated: false
---

初学嵌入式时，"中断"这个词总让人感到神秘。本文尝试从生活中的类比出发，一步步拆解 STM32 中断的完整路径——从 GPIO 引脚上一瞬间的电平变化，到 CPU 最终执行你的回调函数，中间经过了哪些硬件关卡。

---

## 1. 什么是中断？

### 1.1 一个生活中的类比

想象你正在安静地看书（CPU 在执行 `main` 函数的 `while(1)` 循环）。突然手机响了（按键被按下），你夹好书签、接电话，挂断后翻回书签继续看书。

这就是"中断"的本质——**让 CPU 能够暂停当前工作，去处理紧急事件，处理完再回来继续。**

### 1.2 中断在计算机体系中的位置

CPU 在运行过程中会被各种"异常"打断。**中断是异常的一种**。ARM Cortex-M3（STM32F103 的内核）定义了以下异常类型：

| 异常类型 | 说明 | 生活中类比 |
|----------|------|-----------|
| **Reset（复位）** | 上电或按下复位键 | 合上书重新开始 |
| **NMI（不可屏蔽中断）** | 最紧急的硬件故障 | 火灾警报必须立即响应 |
| **HardFault（硬件错误）** | 程序跑飞、非法访问 | 书页被撕坏无法继续 |
| **MemManage Fault** | 内存访问违规（如访问不存在的地址） | 翻到了不存在的页码 |
| **BusFault** | 总线访问错误 | 书架塌了取不到书 |
| **UsageFault** | 未定义指令等 | 书上的字不认识 |
| **SVC（系统服务调用）** | 程序主动触发，类似软件中断 | 主动打电话给朋友求助 |
| **PendSV（可挂起系统服务）** | RTOS 任务切换的核心 | 书签功能 |
| **SysTick（系统滴答）** | 定时器中断，HAL_Delay 的时基 | 闹钟定时提醒 |
| **IRQ（中断请求）** | **外部硬件外设触发的中断** | 手机来电 / 门铃响 |

{{<alertBlockquote type="important">}}
日常说的"中断"，通常特指 **IRQ（Interrupt Request）**——由 GPIO、定时器、串口等硬件外设产生的中断。本文后续提到的"中断"如无特殊说明，均指 IRQ。
{{</alertBlockquote>}}

### 1.3 常见的中断源

导致中断发生的外设很多，几乎每个外设都能产生中断：

| 中断源 | 触发时机 | 实际应用 |
|--------|----------|----------|
| **GPIO** | 引脚电平变化（上升沿/下降沿） | 按键检测、旋转编码器、外部传感器告警 |
| **定时器 (TIM)** | 计数到设定值 | 定时采样、PWM 输出、编码器计数 |
| **ADC** | 模拟信号转换完成 | 读取传感器数据完毕 |
| **UART** | 收到数据或发送完成 | 串口通信、蓝牙/WiFi 透传模块 |
| **I2C / SPI** | 主从通信完成 | 外部 Flash、显示屏驱动 |
| **DMA** | 数据块传输完毕 | 高速数据搬运（摄像头、音频） |

这么多"中断源"汇集到一个叫 **NVIC** 的硬件模块，由它统一仲裁——谁的优先级最高，就优先通知 CPU。

---

## 2. 中断的处理流程（全景）

ARM Cortex-M3 对中断的处理分为 6 个阶段。其中有些阶段是**硬件自动完成的**，有些是**软件（你的代码）完成的**。

### 2.1 阶段一：初始化（软件配置，在 main 中执行）

在进入 `while(1)` 之前，你需要依次设置：

```
① 配置外设，让它能产生中断
   例：在 gpio.c 中将 PB14 设为 GPIO_MODE_IT_RISING_FALLING（双边沿中断模式）

② 配置中断控制器（NVIC）
   HAL_NVIC_SetPriority(EXTI15_10_IRQn, 0, 0);  // 设置优先级
   HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);           // 使能中断通道

③ CPU 总开关
   默认已使能（PRIMASK = 0）
   可调用 __disable_irq() 临时关闭，__enable_irq() 重新打开
```

### 2.2 阶段二：正常运行

初始化完成后，CPU 正常执行 `main()` 中的 `while(1)` 循环，等待中断到来。

### 2.3 阶段三：中断产生（硬件自动完成）

```
按下按键 → PB14 引脚电平变化 → EXTI 边沿检测电路捕捉 → 通知 NVIC
```

### 2.4 阶段四：CPU 响应（硬件自动完成，无需任何代码）

当 NVIC 判定中断优先级足够高时，CPU 硬件自动执行三个动作：

**① 保存现场（入栈）**

CPU 将当前程序的"断点信息"自动压入堆栈：

- R0～R3（通用寄存器）
- R12
- LR（返回地址）
- PC（当前指令地址）
- xPSR（程序状态寄存器）

{{<alertBlockquote type="note">}}
这些操作是 **硬件自动完成** 的，不需要写一行汇编，不需要手动压栈。这是 Cortex-M3 硬件设计的优势——中断响应零代码。
{{</alertBlockquote>}}

**② 查找中断向量表**

CPU 根据中断号，在向量表中找到对应 ISR 的地址，跳转执行。

**③ 跳转到 ISR**

PC 指针被设置为 `EXTI15_10_IRQHandler` 的地址，开始执行中断服务函数。

### 2.5 阶段五：ISR 内部处理（软件完成）

中断服务函数内部通常做三件事：

```
① 分辨具体中断源
   EXTI15_10_IRQn 这个通道管理 EXTI10~15 共 6 条线
   需要检查 EXTI_PR 寄存器判断具体是哪根线触发的
   HAL 库的 HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_14) 帮你实现了这一步

② 清除中断挂起标志
   清除 EXTI_PR 中对应位，告诉硬件"我已经处理完了"
   （这个操作至关重要，不清理的话 ISR 会反复触发）

③ 执行用户的业务逻辑
   通过回调函数 HAL_GPIO_EXTI_Callback() 执行
   比如：读引脚电平 → 判断按下/松开 → 控制 LED
```

### 2.6 阶段六：恢复现场（硬件自动完成）

ISR 函数返回后，CPU 硬件自动将之前压栈的寄存器值弹出（出栈），程序从被中断的位置无缝继续运行。

---

## 3. 中断信号路径：四重关卡

这是理解中断最核心的内容。一个 GPIO 中断信号，从引脚到 CPU，需要经过四道"关卡"。每一道都有自己的控制寄存器，缺一不可。

{{<gallery>}}
![图1](/images/gallery/中断示意图.png)
{{</gallery>}}

```
┌─────────────────────────────────────────────────────────────────┐
│                     中断信号的四重关卡                             │
│                                                                 │
│  PB14  ──►  [GPIO]  ──►  [EXTI] ──► [NVIC]  ──►  [CPU]          │
│  引脚        ①端口       ②外部中断     ③中断        ④内核总          │
│                          控制器       控制器        开关           │
│                                                                 │
│  物理      AFIO_EXTICR  EXTI_RTSR     NVIC_ISER   PRIMASK        │
│  按键      选择引脚映射    EXTI_FTSR    NVIC_IPR    BASEPRI        │
│            到EXTI线      配置触发边沿   使能/屏蔽    全局中断         │
│                          EXTI_IMR    优先级分配     开关           │
│                          中断屏蔽                                 │
│                          EXTI_PR                                 │
│                          挂起标志                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.1 第一关：GPIO + AFIO（哪个引脚能发中断？）

**核心问题**：STM32F103 有 GPIOA～GPIOE 共 5 个端口，每个端口 16 个引脚。但 **EXTI 只有 16 条线**（EXTI0～EXTI15）。

这意味着 PA0、PB0、PC0、PD0、PE0 这 5 个"0 号引脚"不能同时用作中断——同一时间**只有 1 个**能连接到 EXTI0。选择哪一个？通过 **AFIO_EXTICRx 寄存器** 来配置。

```
AFIO_EXTICR1 寄存器（32位，管理 EXTI0~3）：

bit[3:0]   → 选择 EXTI0 的 GPIO 来源:
                0000 = PA0
                0001 = PB0
                0010 = PC0
                0011 = PD0
                0100 = PE0

bit[7:4]   → 选择 EXTI1 的来源
bit[11:8]  → 选择 EXTI2 的来源
bit[15:12] → 选择 EXTI3 的来源
```

`AFIO_EXTICR2` 管理 EXTI4～7，`AFIO_EXTICR3` 管理 EXTI8～11，`AFIO_EXTICR4` 管理 EXTI12～15。

> 在 `0601_key_isr` 中：`HAL_GPIO_Init(GPIOB, ...)` 内部自动将 PB14 写入 `AFIO_EXTICR3` 对应位，映射到 EXTI14。你不需要手动写 AFIO 寄存器。

### 3.2 第二关：EXTI（怎样触发中断？）

**EXTI**（External Interrupt/Event Controller）是 STM32 的外部中断/事件控制器。它在 GPIO 信号和 NVIC 之间，负责精细控制每一条 EXTI 线的行为。

每一条 EXTI 线都有以下可配置的寄存器：

| 寄存器 | 全称 | 作用 | 示例（EXTI14） |
|--------|------|------|---------------|
| **EXTI_RTSR** | Rising Trigger Selection Register | 上升沿触发使能 | bit14=1 → PB14 低→高时触发 |
| **EXTI_FTSR** | Falling Trigger Selection Register | 下降沿触发使能 | bit14=1 → PB14 高→低时触发 |
| **EXTI_SWIER** | Software Interrupt Event Register | 软件触发（调试用） | 软件模拟中断 |
| **EXTI_IMR** | Interrupt Mask Register | **中断总屏蔽** | bit14=1 → 允许通往 NVIC |
| **EXTI_EMR** | Event Mask Register | 事件屏蔽 | 与中断类似但不进 NVIC，用于触发 DMA |
| **EXTI_PR** | Pending Register | **挂起标志** | 硬件自动置 1，软件写 1 清除 |

{{<alertBlockquote type="warning">}}
**关键细节**：EXTI_PR 是"硬件置 1，软件写 1 清 0"。如果你在 ISR 中忘记清除挂起标志，ISR 会反复被触发，导致程序卡死在中断里。
{{</alertBlockquote>}}

以 `0601_key_isr` 中的 PB14 双边沿中断为例，`HAL_GPIO_Init()` 内部自动配置了：

```
EXTI_RTSR[14] = 1   ← 使能上升沿触发（按键松开）
EXTI_FTSR[14] = 1   ← 使能下降沿触发（按键按下）
EXTI_IMR[14]  = 1   ← 允许中断通往 NVIC
```

### 3.3 第三关：NVIC（中断如何仲裁？）

**NVIC**（Nested Vectored Interrupt Controller，嵌套向量中断控制器）是 Cortex-M3 内核自带的硬件模块，不是 ST 设计的。它是所有外设中断的"总调度中心"。

NVIC 的核心职责有三项：

**① 中断使能/屏蔽**

```
NVIC_ISER（中断使能寄存器）  →  写 1 允许某中断通过
NVIC_ICER（中断清除使能寄存器） → 写 1 屏蔽某中断

对应 HAL 库函数：
HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);   // 使能
HAL_NVIC_DisableIRQ(EXTI15_10_IRQn);  // 屏蔽
```

**② 中断优先级管理**

每个中断在 `NVIC_IPR` 中有一个 8 位的优先级字段。STM32F103 **只实现了高 4 位**（bit[7:4]），即 0～15 共 16 个优先级档位（数值越小优先级越高）。

优先级又分为**抢占优先级**和**子优先级**，详见第 5 节。

**③ 异常向量表**

NVIC 维护一张表，记录每个中断对应的 ISR 函数地址。当 CPU 检测到中断时，根据中断号查表跳转。

**STM32F103 的部分中断编号（与本文相关）**：

| 中断号 | 处理器内部编号 | 名称 | 管理的 EXTI 线 |
|--------|---------------|------|---------------|
| 6 | 22 | EXTI0 | EXTI Line 0 独占 |
| 7 | 23 | EXTI1 | EXTI Line 1 独占 |
| 8 | 24 | EXTI2 | EXTI Line 2 独占 |
| 9 | 25 | EXTI3 | EXTI Line 3 独占 |
| 10 | 26 | EXTI4 | EXTI Line 4 独占 |
| 23 | 39 | **EXTI9_5** | EXTI Line 5～9 共用 |
| 40 | 56 | **EXTI15_10** | EXTI Line 10～15 共用 |

{{<alertBlockquote type="important">}}
注意：EXTI0～EXTI4 各自独享一个 NVIC 通道，而 EXTI5～9 共用 EXTI9_5，EXTI10～15 共用 EXTI15_10。共用通道时，需要在 ISR 内部通过检查 `EXTI_PR` 来区分具体是哪根线触发的。
{{</alertBlockquote>}}

### 3.4 第四关：CPU（总开关）

CPU 内部也有三个开关寄存器控制是否响应中断：

| 寄存器 | 作用 | C 语言操作 |
|--------|------|-----------|
| **PRIMASK** | 写 1 = **禁止所有**可屏蔽中断；写 0 = 使能 | `__disable_irq()` / `__enable_irq()` |
| **BASEPRI** | 禁止"优先级 ≥ 某值"的中断（精确屏蔽低优先级） | `__set_BASEPRI(0x60)` |
| **FAULTMASK** | 写 1 = 连 HardFault 也屏蔽（极少数场景使用） | — |

正常运行时 PRIMASK = 0，所有已使能的中断均可响应。在临界区保护（如写 Flash、保护共享变量）时可临时关中断。

---

## 4. 异常向量表

### 4.1 什么是向量表？

异常向量表就是一个**函数指针数组**，存储在 Flash 的起始地址（`0x00000000`）。

当 CPU 检测到中断/异常时：

1. 根据异常编号计算偏移量：`偏移 = 异常编号 × 4`（每条记录 4 字节）
2. 从向量表中读取对应地址
3. 跳转到该地址执行

### 4.2 向量表在代码中的样子

文件：`startup_stm32f103xb.s`（汇编启动文件）

```asm
; 向量表位于 Flash 0x00000000 处
__Vectors   DCD  __initial_sp              ; 0x00: SP 初始值
            DCD  Reset_Handler             ; 0x04: 复位
            DCD  NMI_Handler               ; 0x08: NMI
            DCD  HardFault_Handler         ; 0x0C: 硬件错误
            DCD  MemManage_Handler         ; 0x10: 内存管理
            DCD  BusFault_Handler          ; 0x14: 总线错误
            DCD  UsageFault_Handler        ; 0x18: 用法错误
            DCD  0                         ; 保留
            DCD  0                         ; 保留
            DCD  0                         ; 保留
            DCD  0                         ; 保留
            DCD  SVC_Handler               ; 0x2C: SVC
            DCD  DebugMon_Handler          ; 0x30: 调试监视器
            DCD  0                         ; 保留
            DCD  PendSV_Handler            ; 0x38: PendSV
            DCD  SysTick_Handler           ; 0x3C: SysTick
            ; ── 以下是外设中断 ──
            DCD  EXTI0_IRQHandler          ; 0x58: EXTI0
            DCD  EXTI1_IRQHandler          ; 0x5C: EXTI1
            ; ... ...
            DCD  EXTI15_10_IRQHandler      ; 0xA0: EXTI15~10（PB14 在这里！）
```

### 4.3 向量表是如何"告诉"NVIC 的？

CPU 内部有一个 **VTOR 寄存器**（Vector Table Offset Register，位于系统控制块 SCB 中）。

上电复位后，VTOR 默认 = `0x00000000`，指向 Flash 起始地址。所以向量表默认就在 Flash 开头。

如果你做 IAP 升级（Bootloader + App 双区），两套程序的向量表不同，就需要在 `SystemInit()` 中修改 VTOR 的值，指向 App 的向量表。

### 4.4 `[WEAK]` 关键字：为什么你定义函数就能自动生效？

在启动文件中，除了 `Reset_Handler`，所有 ISR 都用了 `[WEAK]`（弱导出）：

```asm
EXTI15_10_IRQHandler  PROC
    EXPORT  EXTI15_10_IRQHandler  [WEAK]   ; ← 弱导出
    B       .                               ; ← 默认：原地死循环
    ENDP
```

这意味着：
- 启动文件提供了一个**默认的空壳**（死循环，表示"未处理"）
- 如果你在 C 文件中写了同名函数（强符号），链接时**强符号覆盖弱符号**
- 不需要任何函数指针注册，零运行时开销

这就是为什么你在 `stm32f1xx_it.c` 中写了 `EXTI15_10_IRQHandler()`，它就自动成为 ISR。

---

## 5. 中断优先级

### 5.1 优先级寄存器的 8 位结构

在 NVIC 里，每个中断都有一个 8 位的优先级字段（位于 `NVIC_IPR` 寄存器中）：

```
NVIC_IPR 中每个中断占 8 位：
┌───┬───┬───┬───┬───┬───┬───┬───┐
│ 7 │ 6 │ 5 │ 4 │ 3 │ 2 │ 1 │ 0 │
└───┴───┴───┴───┴───┴───┴───┴───┘
   ▲                       ▲
   └── 可能是抢占优先级 ────┴── 可能是子优先级
   （具体各占几位？由"优先级分组"决定）
```

关于这 8 位，有两个关键问题：

### 5.2 问题一：这 8 位都实现了吗？

**答：不一定。**

STM32F103 系列芯片**只实现了高 4 位**（bit[7:4]），bit[3:0] 不存在（读为 0，写无效）。

| 芯片系列 | 实现的位数 | 可用优先级档位 |
|----------|-----------|---------------|
| STM32F0 | 2 位 | 4 档 |
| **STM32F103** | **4 位** | **16 档（0～15）** |
| STM32F4 | 4 位 | 16 档 |
| STM32F7/H7 | 4 位 | 16 档 |

> 实现位数越多，硬件设计越复杂、功耗越高。具体实现几位，由芯片公司根据产品定位决定。

### 5.3 问题二：这 4 位中，哪几位是抢占优先级？哪几位是子优先级？

**答：可配置**。通过 NVIC 的优先级分组寄存器（`NVIC_PRIGROUP`，位于 SCB 的 `AIRCR` 寄存器中）来设定。

**抢占优先级**（Preempt Priority）：
- 决定一个中断**能否打断**另一个正在执行的中断
- 抢占优先级高的可以"抢占"抢占优先级低的中断

**子优先级**（Sub Priority）：
- 当两个中断**同时到达**时，决定谁先被处理
- 子优先级**不能抢占**同抢占优先级的中断，只能排队

STM32F103 的 4 位优先级分组配置：

| 分组值 | 抢占位数 | 子优先级位数 | 抢占档位 | 子档位 |
|--------|---------|-------------|---------|--------|
| 0 | bit[7:5]（3位） | bit[4]（1位） | 0～7（8档） | 0～1（2档） |
| 1 | bit[7:6]（2位） | bit[5:4]（2位） | 0～3（4档） | 0～3（4档） |
| 2 | bit[7]（1位） | bit[6:4]（3位） | 0～1（2档） | 0～7（8档） |
| 3 | bit[7:5]（3位） | bit[4]（1位） | 0～7（8档） | 0～1（2档） |
| **4** | **bit[7:4]（4位）** | **无** | **0～15（16档）** | **无** |

HAL 库默认使用**分组 4**——全部 4 位都用作抢占优先级：

```c
// HAL_Init() 内部
HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_4);  // 全抢占，无子优先级
```

### 5.4 优先级仲裁的三个规则

以三个中断为例：

| 中断 | 抢占优先级 | 子优先级 | 编号 |
|------|-----------|---------|------|
| EXTI0 | 2 | 1 | 6 |
| EXTI1 | 2 | 0 | 7 |
| EXTI2 | 1 | 3 | 8 |

**规则一：抢占优先级决定谁先响应**

- 同时到达 → EXTI2 最先（抢占优先级 1 最小），然后 EXTI1（子优先级 0 更小），最后 EXTI0（子优先级 1）

**规则二：抢占优先级相同，不会互相抢占**

- EXTI0 正在执行，EXTI1 到达 → **不能打断**（同抢占优先级 2），等 EXTI0 完成后处理

**规则三：抢占优先级不同，高抢占低**

- EXTI0（抢占=2）正在执行，EXTI2（抢占=1）到达 → **立即打断**，EXTI2 抢占 EXTI0

{{<alertBlockquote type="note">}}
如果抢占优先级和子优先级都相同，则按中断编号排序，编号小的优先。这是 NVIC 硬件设计确定的最终规则。
{{</alertBlockquote>}}

---

## 6. 实战案例：按键中断控制 LED

结合 `0601_key_isr` 这个实际项目，走一遍 PB14 按键中断控制 PC13 LED 的完整流程。

### 6.1 硬件连接

```
PB14 ──── 按键 ──── GND      按下时 PB14 = 低电平
PC13 ──── LED ──── VDD       PC13 输出低 = LED 亮（低电平有效）
```

### 6.2 初始化代码路径

```
main()
  ├── HAL_Init()
  │     ├── 使能 Flash 预取缓冲
  │     ├── 设优先级分组为"分组4"（全抢占）
  │     ├── 配置 SysTick 每 1ms 中断一次（HAL_Delay 的时基）
  │     └── HAL_MspInit()                    ← 用户实现
  │           ├── __HAL_RCC_AFIO_CLK_ENABLE()  ← EXTI 配置需要 AFIO
  │           └── __HAL_RCC_PWR_CLK_ENABLE()   ← 电源控制时钟
  │
  ├── SystemClock_Config()
  │     └── 配置 HSI 内部 8MHz 振荡器作为系统时钟
  │
  └── MX_GPIO_Init()                         ← gpio.c（CubeMX 生成）
        ├── __HAL_RCC_GPIOC_CLK_ENABLE()      ← 使能 GPIOC 时钟
        ├── __HAL_RCC_GPIOB_CLK_ENABLE()      ← 使能 GPIOB 时钟
        │
        ├── 配置 PC13 → 推挽输出，初始低（LED 亮）
        │     HAL_GPIO_Init(GPIOC, &GPIO_InitStruct)
        │
        ├── 配置 PB14 → 双边沿中断
        │     HAL_GPIO_Init(GPIOB, &GPIO_InitStruct)
        │       内部自动完成：
        │        ├── 配置 GPIOB_CRH → PB14 浮动输入
        │        ├── 配置 AFIO_EXTICR3 → PB14 映射到 EXTI14
        │        ├── EXTI_RTSR[14] = 1 → 上升沿触发
        │        ├── EXTI_FTSR[14] = 1 → 下降沿触发
        │        └── EXTI_IMR[14] = 1  → 允许通往 NVIC
        │
        ├── HAL_NVIC_SetPriority(EXTI15_10_IRQn, 0, 0)  ← 最高优先级
        └── HAL_NVIC_EnableIRQ(EXTI15_10_IRQn)           ← 使能 NVIC 通道
```

### 6.3 按键按下时的完整调用链

```
按键按下：PB14 引脚 HIGH → LOW
═══════════════════════════════════════════════════════

① EXTI 硬件检测到下降沿
    → EXTI_PR[14] 硬件自动置 1（挂起标志）
    → NVIC 仲裁（优先级 0,0 = 最高，立即响应）

② CPU 硬件自动入栈 + 查向量表
    → 从 __Vectors[40] 取到 EXTI15_10_IRQHandler 的地址
    → 跳转执行

③ EXTI15_10_IRQHandler()              ← stm32f1xx_it.c:204
    ↓
④ HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_14) ← stm32f1xx_hal_gpio.c:546
    ├── 检查 EXTI_PR[14] == 1  ✓
    ├── 清除 EXTI_PR[14]（写1清0）  ← 关键！忘清则死循环
    └── HAL_GPIO_EXTI_Callback(GPIO_PIN_14)  ← 调用用户回调
    ↓
⑤ 用户回调（main.c:46）
    ├── HAL_GPIO_ReadPin(GPIOB, PIN_14) → GPIO_PIN_RESET（按下=低电平）
    └── HAL_GPIO_WritePin(GPIOC, PIN_13, GPIO_PIN_RESET) → LED 亮

⑥ CPU 硬件出栈，回到 while(1) 继续循环
```

按键松开时流程完全相同，只是检测到上升沿，`ReadPin` 读到高电平，LED 熄灭。

### 6.4 HAL 的 `__weak` 回调机制

这是 HAL 库最精巧的设计模式——如何在不使用函数指针的情况下，让框架代码调用用户代码：

```c
// ── HAL 库中（stm32f1xx_hal_gpio.c:561）──
__weak void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    UNUSED(GPIO_Pin);  // 默认空壳，什么都不做
}

// ── 你的代码中（main.c:46）──
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)  // 强符号覆盖弱符号
{
    if (GPIO_Pin == GPIO_PIN_14)
    {
        if (HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_14) == GPIO_PIN_RESET)
            HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET); // 亮
        else
            HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_SET);   // 灭
    }
}
```

链接时，用户定义的强符号覆盖 HAL 的 `__weak` 定义。这就是"框架调用用户代码"在纯 C 语言中的实现方式——零指针、零运行时开销、编译期绑定。

---

## 7. 总结：中断配置检查清单

当你配置了一个中断但它不触发时，按这个清单逐项排查：

```
☐ ① GPIO + EXTI 层
    ☐ GPIO 时钟已使能：__HAL_RCC_GPIOx_CLK_ENABLE()
    ☐ GPIO 模式设为中断模式：GPIO_MODE_IT_RISING / _FALLING / _RISING_FALLING
    ☐ 已调用 HAL_GPIO_Init()（内部自动配 AFIO_EXTICR、EXTI_RTSR/FTSR）
    ☐ AFIO 时钟已使能（STM32F1 特有！忘开则 EXTI 不工作）

☐ ② EXTI 层
    ☐ 触发边沿已配置（HAL_GPIO_Init 自动完成）
    ☐ EXTI_IMR 未屏蔽（HAL_GPIO_Init 自动完成）

☐ ③ NVIC 层
    ☐ HAL_NVIC_SetPriority() 已调用
    ☐ HAL_NVIC_EnableIRQ() 已调用

☐ ④ CPU 层
    ☐ 没有意外调用 __disable_irq()
    ☐ 没有在更高优先级的中断中长时间阻塞

☐ ⑤ ISR 处理
    ☐ ISR 函数名与向量表一致（如 EXTI15_10_IRQHandler）
    ☐ ISR 中调用了 HAL_GPIO_EXTI_IRQHandler() 清除挂起标志
    ☐ 实现了 HAL_GPIO_EXTI_Callback() 回调函数
    ☐ 回调中通过 GPIO_Pin 参数正确区分了具体引脚
```

---

## 参考资源

- **芯片参考手册**（中断相关章节）：Chapter 9 - Interrupts and events（NVIC & EXTI），Chapter 8 - General-purpose and alternate-function I/Os（GPIO & AFIO）
- **示例代码**：`0601_key_isr` — 按键中断控制 LED，GPIO 双边沿中断模式
- **ARM 官方文档**：Cortex-M3 Devices Generic User Guide — Chapter 4: Nested Vectored Interrupt Controller

---

## 附录

### 附录 A：入栈与出栈详解

这是正文 2.4 节和 2.6 节提到的"保存现场"和"恢复现场"的详细展开。理解入栈/出栈，是理解中断底层机制的关键一步。

#### A.1 什么是栈？

栈（Stack）是一块 RAM 区域，遵循 **"后进先出"（LIFO）** 的规则。它由 **SP 寄存器**（Stack Pointer，R13）管理——SP 始终指向栈顶。在 Cortex-M3 中：

- **栈向下生长**：压入数据时，SP **减小**（向低地址方向）；弹出数据时，SP **增大**
- STM32F103 的栈位于 RAM 顶部（`0x20005000` 区域），启动文件中定义了栈大小为 `0x400`（1024 字节）

```
高地址    ┌──────────────┐  ← __initial_sp（栈的起始位置，栈为空时 SP 指向这里）
          │              │
          │   可用栈空间   │
          │              │
          │  已使用的栈    │  ← 随着函数调用和中断，栈向下生长
          │  （局部变量、  │
          │    返回地址等） │
低地址    └──────────────┘  ← 栈底（Stack_Mem）
```

#### A.2 发生中断时，硬件自动保存什么？

Cortex-M3 发生中断时，硬件**自动**将 8 个寄存器的值压入栈中。不需要写任何汇编代码。

**保存顺序（从栈顶到栈底，即从高地址到低地址）**：

```
中断前的 SP（高地址）
┌──────────────────┐
│  xPSR  (bit[31:0])   │  ← 程序状态寄存器（含当前条件标志、中断号等）
├──────────────────┤
│  PC    (bit[31:0])   │  ← 程序计数器（被中断时正在执行的指令地址）
├──────────────────┤
│  LR    (bit[31:0])   │  ← 链接寄存器（被中断函数的返回地址）
├──────────────────┤
│  R12   (bit[31:0])   │  ← 通用寄存器
├──────────────────┤
│  R3    (bit[31:0])   │  ← 通用寄存器
├──────────────────┤
│  R2    (bit[31:0])   │  ← 通用寄存器
├──────────────────┤
│  R1    (bit[31:0])   │  ← 通用寄存器
├──────────────────┤
│  R0    (bit[31:0])   │  ← 通用寄存器（常用来传函数参数）
├──────────────────┤
│  (R4~R11 如需使用)   │  ← C 编译器会自动生成 PUSH 指令保存这些
中断后的 SP（低地址）     （如果 ISR 中会用到这些寄存器）
└──────────────────┘
```

**一共 8 × 4 = 32 字节**（不含 R4～R11，这些由编译器按需保存）。

{{<alertBlockquote type="note">}}
如果你用 `__attribute__((naked))` 声明 ISR 为裸函数，编译器不会自动保存 R4～R11，你需要手动写汇编。普通 ISR 不需要这样做。
{{</alertBlockquote>}}

**入栈过程（SP 的变化）**：

```
① 中断发生前：SP = 0x20005000（举例）
② 硬件开始入栈：SP 先减 32 → SP = 0x20004FE0
③ 依次将 xPSR、PC、LR、R12、R3、R2、R1、R0 写入栈中
④ 入栈完成，跳转到 ISR 执行
```

#### A.3 ISR 执行期间：MSP 与 PSP

Cortex-M3 有两个栈指针：

| 栈指针 | 全称 | 用途 |
|--------|------|------|
| **MSP** | Main Stack Pointer | 复位后默认使用，裸机程序（无 RTOS）中始终用 MSP |
| **PSP** | Process Stack Pointer | RTOS 中每个任务使用独立的 PSP，内核中断继续用 MSP |

裸机程序（如 `0601_key_isr`）中，主程序和 ISR 共用 MSP，入栈/出栈都在主栈上完成。

RTOS 场景下：
- 任务代码跑在 PSP 上
- 中断和内核代码始终用 MSP
- 任务切换时，PSP 指向不同任务的私有栈，实现任务隔离

#### A.4 中断返回时，如何恢复现场？

ISR 执行完毕后，CPU 执行一条"中断返回指令"。在 Cortex-M3 中，这不是一条专门的指令，而是通过给 **PC 赋值一个特殊的值** 来实现的。

LR（R14）在进入 ISR 时被硬件设置为一个特殊值——**EXC_RETURN**：

| EXC_RETURN 值 | 含义 |
|---------------|------|
| `0xFFFFFFF1` | 返回到 Handler 模式，继续使用 MSP |
| `0xFFFFFFF9` | 返回到 Thread 模式，使用 MSP |
| `0xFFFFFFFD` | 返回到 Thread 模式，使用 PSP（RTOS 场景） |

ISR 结束时，执行 `BX LR`（或 `POP {PC}`），CPU 检测到 EXC_RETURN 值，自动执行出栈：

```
① CPU 识别 EXC_RETURN → 触发硬件出栈
② 栈中依次弹出 R0、R1、R2、R3、R12、LR、PC、xPSR
③ SP 增加 32 → 恢复到中断前的 SP 值
④ 程序从 PC 指向的地址继续执行 → 无缝衔接
```

#### A.5 入栈/出栈的完整时序图

```
时间线
─────────────────────────────────────────────────────────────►

main() 执行中          中断发生             ISR执行            main()继续
    │                    │                   │                  │
    │  while(1) {..}     │  PB14↓            │  Callback()      │  while(1){..}
    │                    │                   │                  │
    ▼                    ▼                   ▼                  ▼
  [正常运行]    ──→  [硬件入栈32字节]  ──→ [执行ISR代码] ──→ [硬件出栈32字节]
                      SP -= 32              │              SP += 32
                      保存8个寄存器到栈       │              恢复8个寄存器
                      查向量表→跳转ISR       │              从被中断处继续
                                            │
                                    ① 分辨中断源
                                    ② 清 EXTI_PR
                                    ③ 用户 Callback
                                    ④ 返回(BX LR)
```

---

### 附录 B：中断相关寄存器速查表

下表汇总了本文涉及的所有中断相关寄存器，方便快速查阅。

#### B.1 系统级寄存器（SCB — System Control Block）

| 寄存器 | 全称 | 作用 | 本文对应章节 |
|--------|------|------|-------------|
| **VTOR** | Vector Table Offset Register | 向量表基地址 | 4.3 |
| **AIRCR** | Application Interrupt and Reset Control Register | 含优先级分组配置（PRIGROUP） | 5.3 |
| **SHPR1/2/3** | System Handler Priority Registers | 系统异常（SysTick、PendSV、SVC）的优先级 | — |

#### B.2 NVIC 寄存器

| 寄存器 | 全称 | 作用 | C 语言操作 |
|--------|------|------|-----------|
| **NVIC_ISER** | Interrupt Set-Enable Register | 写 1 使能某中断 | `HAL_NVIC_EnableIRQ()` |
| **NVIC_ICER** | Interrupt Clear-Enable Register | 写 1 屏蔽某中断 | `HAL_NVIC_DisableIRQ()` |
| **NVIC_ISPR** | Interrupt Set-Pending Register | 软件挂起某中断（调试用） | `HAL_NVIC_SetPendingIRQ()` |
| **NVIC_ICPR** | Interrupt Clear-Pending Register | 清除软件挂起 | `HAL_NVIC_ClearPendingIRQ()` |
| **NVIC_IABR** | Interrupt Active Bit Register | 只读，指示哪些中断正在执行 | — |
| **NVIC_IPR** | Interrupt Priority Register | 每个中断 8 位优先级（F103 只实现高 4 位） | `HAL_NVIC_SetPriority()` |

#### B.3 EXTI 寄存器

| 寄存器 | 方向 | 作用 | 操作方式 |
|--------|------|------|----------|
| **EXTI_IMR** | 读/写 | 中断屏蔽：1=允许通往 NVIC | `SET_BIT` / `CLEAR_BIT` |
| **EXTI_EMR** | 读/写 | 事件屏蔽：1=允许触发事件（不进 NVIC） | `SET_BIT` / `CLEAR_BIT` |
| **EXTI_RTSR** | 读/写 | 上升沿触发选择 | `SET_BIT` / `CLEAR_BIT` |
| **EXTI_FTSR** | 读/写 | 下降沿触发选择 | `SET_BIT` / `CLEAR_BIT` |
| **EXTI_SWIER** | 读/写 | 软件触发（写 1 触发，写 0 无效） | 调试用 |
| **EXTI_PR** | 读/写 1 清 0 | 挂起标志：硬件置 1，**软件写 1 清除** | `__HAL_GPIO_EXTI_CLEAR_FLAG()` |

#### B.4 GPIO / AFIO 寄存器

| 寄存器 | 作用 | 本文章节 |
|--------|------|---------|
| **AFIO_EXTICR1～4** | 将 GPIO 端口引脚映射到 EXTI0～15 | 3.1 |
| **GPIOx_CRL / CRH** | 配置引脚模式（输入/输出/AF/模拟） | 6.2 |
| **GPIOx_IDR** | 输入数据寄存器（读引脚电平） | 6.3 |
| **GPIOx_ODR** | 输出数据寄存器（写引脚电平） | 6.3 |
| **GPIOx_BSRR** | 位设置/复位寄存器（原子操作，不破坏其他位） | 6.2 |

#### B.5 CPU 中断屏蔽寄存器

| 寄存器 | 范围 | C 语言操作 |
|--------|------|-----------|
| **PRIMASK** | 关所有可屏蔽中断 | `__disable_irq()` / `__enable_irq()` |
| **BASEPRI** | 关≤指定优先级的中断 | `__set_BASEPRI(N)` |
| **FAULTMASK** | 关所有（含 HardFault） | 极少使用 |

---

### 附录 C：CubeMX USER CODE 标记与中断代码放置

如果你使用 STM32CubeMX 生成代码，会发现文件中有许多 `USER CODE BEGIN` / `USER CODE END` 注释对（本文在 2.1 节的初始化代码路径中多次出现）。这些标记是 CubeMX 的"保护区"——重新生成代码时，标记之间的用户代码会被保留，标记之外的会被覆盖。

中断相关的关键 USER CODE 位置：

| 文件 | USER CODE 区域 | 适合放什么中断代码 |
|------|---------------|-------------------|
| **main.c** | `USER CODE BEGIN PV` | **中断回调函数**（如 `HAL_GPIO_EXTI_Callback`） |
| **main.c** | `USER CODE BEGIN 2` | 中断使能前的最后初始化（如设置初始状态） |
| **stm32f1xx_it.c** | `USER CODE BEGIN Includes` | 中断处理中需要的额外头文件 |
| **stm32f1xx_it.c** | `USER CODE BEGIN 0` | 中断相关的辅助变量或函数 |
| **stm32f1xx_hal_msp.c** | `USER CODE BEGIN MspInit 0/1` | 中断相关时钟使能（如 AFIO）和 GPIO 初始化 |
| **gpio.c** | `USER CODE BEGIN 1/2` | 不要在 gpio.c 中改中断配置！`MX_GPIO_Init` 外的代码会被覆盖 |

**一个常见错误**：在 `gpio.c` 的 `MX_GPIO_Init()` 中手动添加 NVIC 配置代码（`SetPriority`/`EnableIRQ`），但忘记 CubeMX 重新生成时这段代码不在 USER CODE 区，直接丢失。正确的做法是让 CubeMX 在 Pinout 界面中勾选中断选项，让它自动在 `MX_GPIO_Init()` 末尾生成 NVIC 配置；或者在 `main.c` 的 `USER CODE BEGIN 2` 中手动配置。

---

### 附录 D：STM32F1 中断的特别注意事项

F1 系列（Cortex-M3）的中断机制与其他 STM32 系列（如 F4/F7/H7）有以下值得注意的差异：

**① AFIO 时钟必须手动使能**

这是 F1 特有的设计。F4 及之后的系列使用 `SYSCFG` 替代 `AFIO` 来做 EXTI 引脚映射。在 F1 中，如果你忘了在 `HAL_MspInit()` 中写：

```c
__HAL_RCC_AFIO_CLK_ENABLE();  // F103 必须！忘写则 EXTI 完全不工作
```

其结果就是 `HAL_GPIO_Init()` 内部写 `AFIO_EXTICR` 寄存器时写不进去（因为 AFIO 时钟没开），EXTI 无法收到任何 GPIO 信号。

排查技巧：在调试器中查看 `AFIO_EXTICR3` 的值是否为 0，如果是 0 且你的中断不触发，大概率是 AFIO 时钟没开。

**② 优先级只有 4 位**

STM32F103 的 NVIC 只实现了 4 位优先级（0～15 档），而 F4/F7/H7 通常也实现 4 位。F0 系列只实现了 2 位（0～3 档）。不要假设所有芯片都有 8 位优先级。

**③ 没有优先级分组 5、6、7**

STM32F103 虽然实现 4 位优先级，但优先级分组值只有 0～4（对应 3 种位分配方式）。NVIC 硬件不支持分组 5、6、7。

**④ EXTI 线路共享**

EXTI5～9 共用 NVIC 通道 EXTI9_5，EXTI10～15 共用 EXTI15_10。如果你同时使用了 PB8（EXTI8）和 PB9（EXTI9），它们会进入同一个 ISR（EXTI9_5_IRQHandler），你需要在回调中通过 `GPIO_Pin` 参数区分。

---

### 附录 E：Cortex-M3 中断优化机制（进阶）

Cortex-M3 设计了两种硬件优化，让中断处理比传统 ARM 内核更快。这些是**纯硬件行为**，无需任何软件配置。

#### E.1 尾链（Tail-Chaining）

当 CPU 刚执行完一个 ISR、即将返回时，如果 NVIC 中已有另一个挂起的中断在排队：

```
传统做法：出栈（恢复旧现场）→ 立即入栈（保存同样的现场）→ 执行新 ISR
           ▲                        ▲
           └── 两次栈操作是浪费！ ──┘

尾链优化：跳过出栈+入栈，直接跳转到下一个 ISR
           省掉两次 32 字节的栈操作，节省约 12 个时钟周期
```

尾链发生的条件：两个中断之间没有需要执行的主程序代码，第二个中断在第一个 ISR 返回时已经处于挂起状态。

#### E.2 迟到中断（Late-Arriving）

当 CPU 正在为一个中断入栈时，如果来了一个**更高优先级**的中断：

```
传统做法：完成当前入栈 → 执行低优先级 ISR → 被打断 → 高优先级 ISR 执行

迟到优化：立即切换到高优先级中断的向量，高优先级 ISR 先执行
           低优先级 ISR 在高优先级 ISR 完成后、但还没返回主程序时执行
```

迟到发生的窗口非常窄——只在入栈阶段（约 12 个时钟周期）。一旦开始执行第一条 ISR 指令，迟到窗口就关闭了，接下来只能通过正常的抢占机制处理。

#### E.3 出栈-抢占（Pop Preemption）

在出栈阶段，如果有高优先级中断到达，CPU 会暂停出栈，转而处理高优先级中断。这与尾链配合，最大程度减少了中断延迟。

---

### 附录 F：关键术语中英对照表

| 中文 | 英文 | 缩写 |
|------|------|------|
| 中断 | Interrupt | IRQ |
| 异常 | Exception | — |
| 嵌套向量中断控制器 | Nested Vectored Interrupt Controller | NVIC |
| 外部中断/事件控制器 | External Interrupt/Event Controller | EXTI |
| 中断服务函数（中断服务例程） | Interrupt Service Routine | ISR |
| 异常向量表 | Vector Table | — |
| 抢占优先级 | Preempt Priority / Group Priority | — |
| 子优先级 | Sub Priority / Subgroup Priority | — |
| 优先级分组 | Priority Grouping | PRIGROUP |
| 弱符号 | Weak Symbol | `__weak` / `[WEAK]` |
| 主栈指针 | Main Stack Pointer | MSP |
| 进程栈指针 | Process Stack Pointer | PSP |
| 程序状态寄存器 | Program Status Register | xPSR |
| 链接寄存器 | Link Register | LR（R14） |
| 尾链 | Tail-Chaining | — |
| 迟到中断 | Late-Arriving Interrupt | — |
| 备用功能 I/O | Alternate Function I/O | AFIO |
| 系统控制块 | System Control Block | SCB |
