import numpy as np
import streamlit as st
import random
import pandas as pd
from copy import deepcopy

# 页面配置
st.set_page_config(page_title="Banker's Algorithm Simulator", layout="wide")

# 页面路由
def main():

    if "page" not in st.session_state:
        st.session_state.page = "welcome"

    pages = {
        "welcome": page_welcome,
        "config": page_config,
        "input": page_input,
        "view": page_view,
        "example": page_sample_init,
        "simulator": page_simulator

    }

    with st.sidebar:
        st.header("导航")
        if st.button("🏠 首页",use_container_width=True):
            st.session_state.page = "welcome"
        if "n" in st.session_state:
            if st.button("⚙️ 配置",use_container_width=True):
                st.session_state.page = "config"
            if st.button("📝 输入",use_container_width=True):
                st.session_state.page = "input"
            if st.button("📋 示例", use_container_width=True):
                st.session_state.page = "example"
            if st.button("🔍 审查",use_container_width=True):
                st.session_state.page = "view"
            if st.button("▶️ 模拟",use_container_width=True):
                st.session_state.page = "simulator"


    pages[st.session_state.page]()

# 欢迎页面
def page_welcome():
    # 重置session
    st.session_state.sys_resource = 0
    st.session_state.n = 0
    st.session_state.m = 0
    st.session_state.max_alloc = 0
    st.session_state.alloc = 0
    st.session_state.need = 0
    st.session_state.reqs = 0
    st.session_state.current_step = 0
    st.session_state.available = 0
    st.session_state.tick = 0
    st.session_state.safe_seq = 0
    #
    st.title("银行家算法模拟系统")
    cols = st.columns(2)
    if cols[0].button("随机模拟", use_container_width=True):
        st.session_state.page = "config"
        st.rerun()

    if cols[1].button("手动输入", use_container_width=True):
        st.session_state.page = "input"
        st.rerun()
    intros = st.columns(2)

    intros[1].markdown("""
欢迎使用银行家算法模拟系统！
本系统旨在帮助您理解银行家算法的工作原理，并通过可视化的方式展示算法的执行过程。
请按照以下步骤使用本系统：
1. 点击“配置”按钮，设置系统的资源和进程数量。
2. 点击“输入”按钮，输入每个进程的资源需求和可用资源。

# 银行家算法

**银行家算法**（Banker's Algorithm）是一个避免死锁的著名算法，是由荷兰计算机科学家艾兹赫尔·戴克斯特拉在1965年为T.H.E操作系统设计的一种避免死结产生的算法。它以银行借贷系统的分配策略为基础，判断并保证系统的安全运行。

## 背景

在银行中，客户申请贷款的数量是有限的，每个客户在第一次申请贷款时要声明完成该项目所需的最大资金量，在满足所有贷款要求时，客户应及时归还。银行家在客户申请的贷款数量不超过自己拥有的最大值时，都应尽量满足客户的需要。在这样的描述中，银行家就好比操作系统，资金就是资源，客户就相当于要申请资源的进程。
    """)
    intros[1].image("./img/dj.png")
    intros[0].markdown("""
## 处理程序

```
       Allocation　　Max　　　Available
       ＡＢＣＤ　　  ＡＢＣＤ　　ＡＢＣＤ
  P1   ００１４　　  ０６５６　　１５２０　
  P2   １４３２　　  １９４２　
  P3   １３５４　  　１３５６
  P4   １０００　　  １７５０
```

我们会看到一个资源分配表，要判断是否为安全状态，首先先找出它的Need，Need即Max（最多需要多少资源）减去Allocation（原本已经分配出去的资源），计算结果如下：

```
    NEED
  ＡＢＣＤ
  ０６４２　
  ０５１０
  ０００２
  ０７５０
```

然后加一个全都为false的栏位

```
  FINISH
  false
  false
  false
  false
```

接下来找出need比available小的（千万不能把它当成4位数 他是4个不同的数）

```
    NEED　　  Available
  ＡＢＣＤ　　ＡＢＣＤ
  ０６４２　　１５２０
  ０５１０<-
  ０００２
  ０７５０
```

P2的需求小于能用的，所以配置给他再回收

```
   NEED　　   Available
  ＡＢＣＤ　　ＡＢＣＤ
  ０６４２　　１５２０
  ００００　＋１４３２
  ０００２－－－－－－－
  ０７５０　　２９５２
```

此时P2 FINISH的false要改成true（已完成）

```
  FINISH
  false
  true
  false
  false
```

接下来继续往下找，发现P3的需求为0002，小于能用的2952，所以资源配置给他再回收

```
  　NEED　　    Available
  ＡＢＣＤ　　Ａ　Ｂ　Ｃ　Ｄ
  ０６４２　　２　９　５　２
  ００００　＋１　３　５　４
  ００００－－－－－－－－－－
  ０７５０　　３　12　10　6
```

依此类推，做完P4→P1，当全部的FINISH都变成true时，就是安全状态。

## 安全和不安全的状态

如果所有Process都可以完成并终止，则一个状态（如上述范例）被认为是安全的。由于系统无法知道什么时候一个过程将终止，或者之后它需要多少资源，系统假定所有进程将最终试图获取其声明的最大资源并在不久之后终止。在大多数情况下，这是一个合理的假设，因为系统不是特别关注每个进程运行了多久（至少不是从避免死锁的角度）。此外，如果一个进程终止前没有获取其能获取的最多的资源，它只是让系统更容易处理。

基于这一假设，该算法通过尝试寻找允许每个进程获得的最大资源并结束（把资源返还给系统）的进程请求的一个理想集合，来决定一个状态是否是安全的。不存在这个集合的状态都是不安全的。

## 虚拟码（pseudo-code）

```pseudo
P - 进程的集合

Mp - 进程p的最大的请求数目

Cp - 进程p当前被分配的资源

A - 当前可用的资源

 while (P != ∅) {
     found = FALSE;
     foreach (p ∈ P) {
         if (Mp − Cp ≤ A) {
              /* p可以获得他所需的资源。假设他得到资源后执行；执行终止，并释放所拥有的资源。*/
              A = A + Cp ;
              P = P − {p};
              found = TRUE;
         }
     }
     if (! found) return FAIL;
 }
 return OK;
```

## 参考文献

### 引用

 Concurrency (PDF). [2009-01-13].[link](https://web.archive.org/web/20140106205032/http://www.cs.huji.ac.il/course/2006/os/notes/notes4.pdf)

### 书籍

* 《操作系统概念（Operating System Concepts）》第六版[1](https://books.google.com.hk/books?hl=zh-TW&id=bohQAAAAMAAJ&dq=Operating+System+Concepts+sixth+edition&q=bank+algorithm&pgis=1&redir_esc=y) [存档](https://web.archive.org/web/20171204114609/https://books.google.com.hk/books?hl=zh-TW&id=bohQAAAAMAAJ&dq=Operating+System+Concepts+sixth+edition&q=bank+algorithm&pgis=1&redir_esc=y)

    """)


# 配置页面
def page_config():

    st.title("系统配置")

    if "current_step" not in st.session_state:
        st.session_state.current_step = 0

    # 步骤1：输入基本参数
    if st.session_state.current_step == 0:
        # 重置session
        st.session_state.sys_resource = 0
        st.session_state.n = 0
        st.session_state.m = 0
        st.session_state.max_alloc = 0
        st.session_state.alloc = 0
        st.session_state.need = 0
        st.session_state.reqs = 0
        st.session_state.current_step = 0
        st.session_state.available = 0
        st.session_state.tick = 0
        st.session_state.safe_seq = 0
        #
        with st.form("basic_params"):
            cols = st.columns(3)
            n = cols[0].number_input("进程数 (n)", 1, 10, 3)
            m = cols[1].number_input("资源种类数 (m)", 1, 5, 2)
            lowest = cols[2].number_input("最低资源数", 1, 5, 5)

            if st.form_submit_button("确认",use_container_width=True):
                st.session_state.n = n
                st.session_state.m = m
                st.session_state.lowest = lowest
                st.session_state.current_step = 1
                st.rerun()

    # 步骤2：生成系统资源
    if st.session_state.current_step == 1:
        max_resource = 20
        sys_resource = [max(random.randint(0, max_resource) ,st.session_state.lowest)
                        for _ in range(st.session_state.m)]

        # 生成已分配矩阵，加和小于系统资源
        alloc = []
        sys_resource_cp = deepcopy(sys_resource)
        for _ in range(st.session_state.n):
            row = [random.randint(0, res) for res in sys_resource_cp]
            sys_resource_cp = [res - r for res, r in zip(sys_resource_cp, row)] # 减去已分配的资源
            alloc.append(row) # 加入已分配矩阵


        # 生成最大分配矩阵
        max_alloc = []
        for i in range(st.session_state.n):
            row = [random.randint(alloc[i][j] , sys_resource[j]) for j in range(st.session_state.m)]# 最大分配矩阵大于等于已分配矩阵
            max_alloc.append(row)

        # 计算需求矩阵
        need = []
        for i in range(st.session_state.n):
            row = [max_alloc[i][j] - alloc[i][j] for j in range(st.session_state.m)]
            need.append(row)

        # 生成请求列表
        reqs = []
        need_copy = deepcopy(need)
        '''
        生成请求列表，每个进程随机请求1到need[i][j]的资源，
        直到need[i][j]为0，然后随机生成下一个进程的请求，
        直到所有进程的请求都生成完毕，然后随机生成5个padding请求
        '''
        for i in range(st.session_state.n):
            while sum(need_copy[i]) > 0:
                req = []
                for j in range(st.session_state.m):
                    if need_copy[i][j] == 0:
                        req.append(0)
                    else:
                        req.append(random.randint(1, need_copy[i][j]))
                reqs.append((i, req))
                for j in range(st.session_state.m):
                    need_copy[i][j] -= req[j]
        random.shuffle(reqs) # 随机打乱请求列表
        # reqs += [(-1, [0] * st.session_state.m)] * 5  # 添加padding
        # 完毕

        # 计算初始可用资源
        alloc_sum = [sum(col) for col in zip(*alloc)]
        available = [sys_resource[i] - alloc_sum[i] for i in range(st.session_state.m)]

        # 保存到session
        st.session_state.sys_resource = sys_resource
        st.session_state.max_alloc = max_alloc
        st.session_state.alloc = alloc
        st.session_state.need = need
        st.session_state.reqs = reqs
        st.session_state.tick = 0
        st.session_state.current_step = 2
        st.session_state.available = available
        st.rerun()

    # 步骤3：显示配置结果
    if st.session_state.current_step == 2:
        # st.success("系统初始化完成！")

        # 显示资源分配
        st.subheader("系统资源分配")

        # 系统资源和可用资源显示
        resources = st.columns(2)
        with resources[0]:
            st.markdown("**系统总资源**")
            sys_df = pd.DataFrame(
                [st.session_state.sys_resource],
                columns=[f"资源{i}" for i in range(st.session_state.m)],
                index=["总量"]
            )
            st.dataframe(sys_df.style.map(
                lambda x: 'color: blue' if x == min(st.session_state.sys_resource) else 'color: pink' if x == max(
                    st.session_state.sys_resource) else ''))

        with resources[1]:
            st.markdown("**可用资源**")
            avail_df = pd.DataFrame(
                [st.session_state.available],
                columns=[f"资源{i}" for i in range(st.session_state.m)],
                index=["可用量"]
            )
            st.dataframe(avail_df.style.map(
                lambda x: 'color: blue' if x == min(st.session_state.available) else 'color: pink' if x == max(
                    st.session_state.available) else ''))

        # 矩阵显示
        st.subheader("资源分配矩阵")
        cols = st.columns(3)

        with cols[0]:
            st.markdown("**最大分配矩阵 (MAX)**")
            max_df = pd.DataFrame(
                st.session_state.max_alloc,
                columns=[f"资源{i}" for i in range(st.session_state.m)],
                index=[f"进程{i}" for i in range(st.session_state.n)]
            )
            st.dataframe(max_df.style.map(lambda x: 'color: blue' if x == min(
                map(min, st.session_state.max_alloc)) else 'color: pink' if x == max(
                map(max, st.session_state.max_alloc)) else ''))

        with cols[1]:
            st.markdown("**已分配矩阵 (ALLOC)**")
            alloc_df = pd.DataFrame(
                st.session_state.alloc,
                columns=[f"资源{i}" for i in range(st.session_state.m)],
                index=[f"进程{i}" for i in range(st.session_state.n)]
            )
            st.dataframe(alloc_df.style.map(
                lambda x: 'color: blue' if x == min(map(min, st.session_state.alloc)) else 'color: pink' if x == max(
                    map(max, st.session_state.alloc)) else ''))

        with cols[2]:
            st.markdown("**需求矩阵 (NEED)**")
            need_df = pd.DataFrame(
                st.session_state.need,
                columns=[f"资源{i}" for i in range(st.session_state.m)],
                index=[f"进程{i}" for i in range(st.session_state.n)]
            )
            st.dataframe(need_df.style.map(
                lambda x: 'color: blue' if x == min(map(min, st.session_state.need)) else 'color: pink' if x == max(
                    map(max, st.session_state.need)) else ''))



        # 显示请求序列
        st.subheader("生成的请求序列")
        req_df = pd.DataFrame(
            [(i, req[0], req[1]) for i, req in enumerate(st.session_state.reqs)],
            columns=["Tick", "进程ID", "请求资源"]
        )
        st.dataframe(
            req_df.style.apply(lambda x: ['background: lightblue' if x.name % 2 == 0 else '' for i in x], axis=1),
            height=250)

        # 操作按钮
        c1, c2 = st.columns(2)
        if c1.button("✅ 确认配置", use_container_width=True):
            st.session_state.page = "view"
            st.rerun()
        if c2.button("🔄 重新生成", use_container_width=True):
            st.session_state.current_step = 0
            st.rerun()

def page_sample_init():
    st.title("样例初始化")

    # 样例数据
    sample_data = {
        "Allocation": [
            [0, 0, 1, 4],
            [1, 4, 3, 2],
            [1, 3, 5, 4],
            [1, 0, 0, 0]
        ],
        "Max": [
            [0, 6, 5, 6],
            [1, 9, 4, 2],
            [1, 3, 5, 6],
            [1, 7, 5, 0]
        ],
        "Available": [1, 5, 2, 0]
    }

    # 显示样例数据
    st.subheader("样例数据")
    cols = st.columns(3)
    with cols[0]:
        st.markdown("**Allocation**")
        alloc_df = pd.DataFrame(
            sample_data["Allocation"],
            columns=["A", "B", "C", "D"],
            index=[f"P{i+1}" for i in range(len(sample_data["Allocation"]))]
        )
        st.dataframe(alloc_df)

    with cols[1]:
        st.markdown("**Max**")
        max_df = pd.DataFrame(
            sample_data["Max"],
            columns=["A", "B", "C", "D"],
            index=[f"P{i+1}" for i in range(len(sample_data["Max"]))]
        )
        st.dataframe(max_df)

    with cols[2]:
        st.markdown("**Available**")
        avail_df = pd.DataFrame(
            [sample_data["Available"]],
            columns=["A", "B", "C", "D"],
            index=["Available"]
        )
        st.dataframe(avail_df)

    # 初始化按钮
    if st.button("🚀 使用样例初始化系统", use_container_width=True):
        # 计算Need矩阵
        need = []
        for i in range(len(sample_data["Allocation"])):
            row = [
                sample_data["Max"][i][j] - sample_data["Allocation"][i][j]
                for j in range(len(sample_data["Available"]))
            ]
            need.append(row)

        # 生成请求序列
        reqs = []
        need_copy = deepcopy(need)
        for i in range(len(need_copy)):
            while sum(need_copy[i]) > 0:
                req = []
                for j in range(len(need_copy[i])):
                    if need_copy[i][j] == 0:
                        req.append(0)
                    else:
                        req.append(random.randint(1, need_copy[i][j]))
                reqs.append((i, req))
                for j in range(len(need_copy[i])):
                    need_copy[i][j] -= req[j]

        random.shuffle(reqs)
        # reqs += [(-1, [0] * len(sample_data["Available"]))] * 5

        # 保存到session_state
        st.session_state.n = len(sample_data["Allocation"])
        st.session_state.m = len(sample_data["Available"])
        st.session_state.sys_resource = [
            sum(col) for col in zip(*sample_data["Allocation"])
        ]
        st.session_state.sys_resource = [
            st.session_state.sys_resource[i] + sample_data["Available"][i]
            for i in range(len(sample_data["Available"]))
        ]
        st.session_state.max_alloc = sample_data["Max"]
        st.session_state.alloc = sample_data["Allocation"]
        st.session_state.need = need
        st.session_state.reqs = reqs
        st.session_state.tick = 0
        st.session_state.available = sample_data["Available"]

        st.success("系统初始化完成！")
        st.session_state.page = "view"
        st.rerun()



# 配置页面
def page_input():
    st.title("手动配置系统参数")
    st.session_state.lowest = 1
    if "current_step" not in st.session_state:
        st.session_state.current_step = 0

    # 步骤1：输入基本参数
    if st.session_state.current_step == 0:
        with st.form("basic_params"):
            st.subheader("步骤1/3 - 输入基本参数")
            cols = st.columns(3)
            n = cols[0].number_input("进程数 (n)", 1, 10, 3, key="input_n")
            m = cols[1].number_input("资源种类数 (m)", 1, 5, 2, key="input_m")
            sys_resource = cols[2].text_input("系统总资源（逗号分隔）", "9,6", key="input_sys")

            if st.form_submit_button("下一步 ▶️"):
                try:
                    # 解析系统资源
                    sys_resource = [int(x.strip()) for x in sys_resource.split(",")]
                    if len(sys_resource) != m:
                        st.error(f"需要输入{m}种资源，当前输入{len(sys_resource)}个")
                        return
                    if any(x <= 0 for x in sys_resource):
                        st.error("资源数量必须大于0")
                        return

                    st.session_state.n = n
                    st.session_state.m = m
                    st.session_state.sys_resource = sys_resource
                    st.session_state.current_step = 1
                    st.rerun()
                except ValueError:
                    st.error("请输入有效的数字（用英文逗号分隔）")

    # 步骤2：输入分配矩阵
    elif st.session_state.current_step == 1:
        st.subheader("步骤2/3 - 输入分配矩阵")
        st.write(f"系统总资源: {st.session_state.sys_resource}")

        # 生成输入表格
        max_alloc = []
        alloc = []
        with st.form("matrix_input"):
            # 最大分配矩阵
            st.markdown("**最大分配矩阵 (Max)**")
            max_cols = st.columns(st.session_state.m)
            max_header = [f"R{i}" for i in range(st.session_state.m)]
            max_data = []
            for i in range(st.session_state.n):
                row = []
                cols = st.columns(st.session_state.m)
                for j in range(st.session_state.m):
                    row.append(cols[j].number_input(
                        f"P{i}-R{j}", 0, st.session_state.sys_resource[j],
                        key=f"max_{i}_{j}"
                    ))
                max_data.append(row)

            # 已分配矩阵
            st.markdown("**已分配矩阵 (Alloc)**")
            alloc_data = []
            for i in range(st.session_state.n):
                row = []
                cols = st.columns(st.session_state.m)
                for j in range(st.session_state.m):
                    max_val = max_data[i][j]
                    row.append(cols[j].number_input(
                        f"P{i}-R{j}", 0, max_val, 0,
                        key=f"alloc_{i}_{j}"
                    ))
                alloc_data.append(row)

            if st.form_submit_button("下一步 ▶️"):
                # 验证分配合理性
                alloc_sum = [sum(col) for col in zip(*alloc_data)]
                valid = True
                for j in range(st.session_state.m):
                    if alloc_sum[j] > st.session_state.sys_resource[j]:
                        st.error(f"资源R{j}已分配总数{alloc_sum[j]}超过系统总量{st.session_state.sys_resource[j]}")
                        valid = False

                if valid:
                    st.session_state.max_alloc = max_data
                    st.session_state.alloc = alloc_data
                    st.session_state.current_step = 2
                    st.rerun()

    # 步骤3：确认配置
    elif st.session_state.current_step == 2:
        st.subheader("步骤3/3 - 确认配置")

        # 计算需求矩阵
        need = []
        for i in range(st.session_state.n):
            row = [
                st.session_state.max_alloc[i][j] - st.session_state.alloc[i][j]
                for j in range(st.session_state.m)
            ]
            need.append(row)

        # 生成请求序列
        reqs = []
        need_copy = deepcopy(need)
        for i in range(st.session_state.n):
            while sum(need_copy[i]) > 0:
                req = []
                for j in range(st.session_state.m):
                    if need_copy[i][j] == 0:
                        req.append(0)
                    else:
                        req.append(random.randint(1, need_copy[i][j]))
                reqs.append((i, req))
                for j in range(st.session_state.m):
                    need_copy[i][j] -= req[j]

        random.shuffle(reqs)
        reqs += [(-1, [0] * st.session_state.m)] * 5

        # 保存数据
        st.session_state.need = need
        st.session_state.reqs = reqs
        st.session_state.tick = 0

        # 显示配置摘要
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**最大分配矩阵**")
            st.dataframe(pd.DataFrame(
                st.session_state.max_alloc,
                columns=[f"R{i}" for i in range(st.session_state.m)],
                index=[f"P{i}" for i in range(st.session_state.n)]
            ))

        with col2:
            st.markdown("**已分配矩阵**")
            st.dataframe(pd.DataFrame(
                st.session_state.alloc,
                columns=[f"R{i}" for i in range(st.session_state.m)],
                index=[f"P{i}" for i in range(st.session_state.n)]
            ))

        st.markdown("**生成的请求序列**")
        req_df = pd.DataFrame(
            [(i, req[0], req[1]) for i, req in enumerate(st.session_state.reqs)],
            columns=["Tick", "进程ID", "请求资源"]
        )
        st.dataframe(req_df, height=300)

        # 操作按钮
        c1, c2, c3 = st.columns(3)
        if c1.button("✅ 确认配置", use_container_width=True):
            st.session_state.page = "view"
            st.rerun()
        if c2.button("🔄 重新输入", use_container_width=True):
            st.session_state.current_step = 0
            st.rerun()
        if c3.button("✏️ 修改矩阵", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()
# 审查页面
def page_view():
    st.title("系统状态审查")

    # 显示基本信息
    cols = st.columns(3)
    cols[0].metric("进程数", st.session_state.n)
    cols[1].metric("资源种类数", st.session_state.m)
    cols[2].metric("当前Tick", st.session_state.tick)


#%%
    # 显示资源分配
    st.subheader("系统资源分配")

    # 系统资源和可用资源显示
    resources = st.columns(2)
    with resources[0]:
        st.markdown("**系统总资源**")
        sys_df = pd.DataFrame(
            [st.session_state.sys_resource],
            columns=[f"资源{i}" for i in range(st.session_state.m)],
            index=["总量"]
        )
        st.dataframe(sys_df.style.map(
            lambda x: 'color: blue' if x == min(st.session_state.sys_resource) else 'color: pink' if x == max(
                st.session_state.sys_resource) else ''))

    with resources[1]:
        st.markdown("**可用资源**")
        avail_df = pd.DataFrame(
            [st.session_state.available],
            columns=[f"资源{i}" for i in range(st.session_state.m)],
            index=["可用量"]
        )
        st.dataframe(avail_df.style.map(
            lambda x: 'color: blue' if x == min(st.session_state.available) else 'color: pink' if x == max(
                st.session_state.available) else ''))
#%%
    # 显示矩阵
    st.subheader("资源分配矩阵")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("最大分配矩阵")
        st.dataframe(pd.DataFrame(
            st.session_state.max_alloc,
            columns=[f"R{i}" for i in range(st.session_state.m)],
            index=[f"P{i}" for i in range(st.session_state.n)]
        ))

    with col2:
        st.write("已分配矩阵")
        st.dataframe(pd.DataFrame(
            st.session_state.alloc,
            columns=[f"R{i}" for i in range(st.session_state.m)],
            index=[f"P{i}" for i in range(st.session_state.n)]
        ))

    with col3:
        st.write("需求矩阵")
        st.dataframe(pd.DataFrame(
            st.session_state.need,
            columns=[f"R{i}" for i in range(st.session_state.m)],
            index=[f"P{i}" for i in range(st.session_state.n)]
        ))
    # 显示请求序列
    st.subheader("生成的请求序列")
    req_df = pd.DataFrame(
        [(i, req[0], req[1]) for i, req in enumerate(st.session_state.reqs)],
        columns=["Tick", "进程ID", "请求资源"]
    )
    st.dataframe(
        req_df.style.apply(lambda x: ['background: lightblue' if x.name % 2 == 0 else '' for i in x], axis=1),
        height=250)

    # 操作按钮
    c1, c2 = st.columns(2)
    if c1.button("▶️ 开始模拟",use_container_width=True):
        st.session_state.page = "simulator"
        st.rerun()
    if c2.button("↩️ 返回配置",use_container_width=True):
        st.session_state.page = "config"
        st.rerun()

def calculate_efficiency(system, sequence):
    """加权资源利用率计算"""
    total_weight = sum(system["resources"])
    usage = 0.0

    # 模拟执行过程计算资源利用率
    work = system["available"].copy()
    alloc_copy = deepcopy(system["allocation"])

    for client in sequence:
        # 分配资源
        for ri in range(len(work)):
            work[ri] += alloc_copy[client][ri]

        # 计算当前利用率
        for ri in range(len(work)):
            used = system["resources"][ri] - work[ri]
            weight = system["resources"][ri] / total_weight
            usage += (used / system["resources"][ri]) * weight

    # 平均利用率
    return usage / len(sequence)

def display_safe_sequences(safe_sequences, system):
    """展示安全序列及其评分"""
    if not safe_sequences:
        st.error("未找到安全序列！")
        return

    # 计算每个安全序列的评分
    results = []
    for seq in safe_sequences:
        efficiency = calculate_efficiency(system, seq)
        results.append({
            "安全序列": " -> ".join([f"P{p}" for p in seq]),
            "资源利用率": f"{efficiency:.2%}"
        })

    # 转换为DataFrame
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True,)
# 模拟页面
def page_simulator():
    st.title("算法模拟")
    # 显示基本信息
    cols = st.columns(3)
    cols[0].metric("进程数", st.session_state.n)
    cols[1].metric("资源种类数", st.session_state.m)
    cols[2].metric("当前Tick", st.session_state.tick)

    # %%
    # 显示资源分配
    st.subheader("系统资源分配")

    # 系统资源和可用资源显示
    resources = st.columns(2)
    with resources[0]:
        st.markdown("**系统总资源**")
        sys_df = pd.DataFrame(
            [st.session_state.sys_resource],
            columns=[f"资源{i}" for i in range(st.session_state.m)],
            index=["总量"]
        )
        st.dataframe(sys_df.style.map(
            lambda x: 'color: blue' if x == min(st.session_state.sys_resource) else 'color: pink' if x == max(
                st.session_state.sys_resource) else ''))

    with resources[1]:
        st.markdown("**可用资源**")
        avail_df = pd.DataFrame(
            [st.session_state.available],
            columns=[f"资源{i}" for i in range(st.session_state.m)],
            index=["可用量"]
        )
        st.dataframe(avail_df.style.map(
            lambda x: 'color: blue' if x == min(st.session_state.available) else 'color: pink' if x == max(
                st.session_state.available) else ''))
        #%%
    # 显示矩阵
    st.subheader("资源分配矩阵")
    col1, col2, col3,col4 = st.columns(4)

    with col1:
        st.write("最大分配矩阵")
        st.dataframe(pd.DataFrame(
            st.session_state.max_alloc,
            columns=[f"R{i}" for i in range(st.session_state.m)],
            index=[f"P{i}" for i in range(st.session_state.n)]
        ))

    with col2:
        st.write("已分配矩阵")
        st.dataframe(pd.DataFrame(
            st.session_state.alloc,
            columns=[f"R{i}" for i in range(st.session_state.m)],
            index=[f"P{i}" for i in range(st.session_state.n)]
        ))

    with col3:
        st.write("需求矩阵")
        st.dataframe(pd.DataFrame(
            st.session_state.need,
            columns=[f"R{i}" for i in range(st.session_state.m)],
            index=[f"P{i}" for i in range(st.session_state.n)]
        ))

    with col4:
        pid, req = st.session_state.reqs[st.session_state.tick]
        reqd=deepcopy(st.session_state.sys_resource)
        for i in range(st.session_state.m):
            reqd[i]=req[i]

        st.markdown(f"进程ID: {pid}请求资源")
        sys_df = pd.DataFrame(
            [reqd],
            columns=[f"资源{i}" for i in range(st.session_state.m)],
            index=["总量"]
        )
        st.dataframe(sys_df.style.map(
            lambda x: 'color: blue' if x == min(reqd) else 'color: pink' if x == max(
                reqd) else ''))


    # 安全序列计算
    st.subheader("安全序列分析")
    safe_sequences = bankers_algorithm()
    st.session_state.state=any(safe_sequences)

    if safe_sequences:
        if st.session_state.tick==0:
            st.success(f"初始状态，找到{len(safe_sequences)} 个安全序列，可计算下一个")
        else:
            st.success(f"对tick<{st.session_state.tick}的请求做分配后，找到 {len(safe_sequences)} 个安全序列，可计算下一个")
        # for seq in safe_sequences:
        #     st.code(" → ".join([f"P{p}" for p in seq]))
        system = {
            "resources": deepcopy(st.session_state.sys_resource),  # 系统总资源
            "available": deepcopy(st.session_state.available),  # 可用资源
            "allocation": deepcopy(st.session_state.alloc),
        }
        # 在Streamlit中展示
        st.title("安全序列及其评分")
        display_safe_sequences(safe_sequences, system)

    else:
        st.error("当前状态不安全！请跳过该分配请求！")

    # 操作按钮
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.session_state.state and st.button("⏭️ 计算下一个",use_container_width=True):
            process_next()
        if not st.session_state.state and st.button("⏩ 跳过",use_container_width=True):
            skip_request()
    # 显示请求序列
    st.subheader("生成的请求序列")
    req_df = pd.DataFrame(
        [(i, req[0], req[1]) for i, req in enumerate(st.session_state.reqs)],
        columns=["Tick", "进程ID", "请求资源"]
    )
    st.dataframe(
        req_df.style.apply(lambda x: ['background: lightblue' if x.name % 2 == 0 else '' for i in x], axis=1),
        height=250)

    if col3.button("🏠 返回首页",use_container_width=True):
        st.session_state.page = "welcome"
        st.rerun()


def calculate_available():
    alloc_sum = [sum(col) for col in zip(*st.session_state.alloc)]
    return [st.session_state.sys_resource[i] - alloc_sum[i]
            for i in range(st.session_state.m)]


def bankers_algorithm():
    available = calculate_available()
    need = deepcopy(st.session_state.need)
    alloc = deepcopy(st.session_state.alloc)
    sequences = []

    def dfs(seq, work, finish):
        if len(seq) == st.session_state.n:
            sequences.append(seq)
            return

        for i in range(st.session_state.n):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(st.session_state.m)):
                new_work = [work[j] + alloc[i][j] for j in range(st.session_state.m)]
                new_finish = finish.copy()
                new_finish[i] = True
                dfs(seq + [i], new_work, new_finish)

    dfs([], available, [False] * st.session_state.n)
    return sequences


def process_next():
    if st.session_state.tick >= len(st.session_state.reqs)-1:
        st.error("已经是最后一个请求！")
        return

    pid, req = st.session_state.reqs[st.session_state.tick]
    available = calculate_available()

    # 尝试分配资源
    # 合法性检查
    if all(req[j] <= st.session_state.need[pid][j] for j in range(st.session_state.m)) and \
            all(req[j] <= available[j] for j in range(st.session_state.m)):

        # 预分配
        for j in range(st.session_state.m):
            st.session_state.alloc[pid][j] += req[j]
            st.session_state.need[pid][j] -= req[j]
            available[j] -= req[j]

        # 检查是否完成
        if all(n == 0 for n in st.session_state.need[pid]):
            # 释放资源
            for j in range(st.session_state.m):
                available[j] += st.session_state.alloc[pid][j]
                st.session_state.alloc[pid][j] = 0

    st.session_state.tick += 1


def skip_request():
    if st.session_state.tick >= len(st.session_state.reqs)-1:
        st.error("已经是最后一个请求！")
        return

    st.session_state.tick += 1


if __name__ == "__main__":
    main()
