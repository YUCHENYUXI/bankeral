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
            if st.button("🔍 审查",use_container_width=True):
                st.session_state.page = "view"
            if st.button("▶️ 模拟",use_container_width=True):
                st.session_state.page = "simulator"


    pages[st.session_state.page]()

# 欢迎页面
def page_welcome():
    st.title("银行家算法模拟系统")
    st.markdown("""
    ## 欢迎使用银行家算法模拟系统！

    **银行家算法**是操作系统中用于避免死锁的重要算法，本系统通过可视化方式帮助理解其工作原理。
    """)
    cols = st.columns(2)
    if cols[0].button("随机模拟",use_container_width=True):
        st.session_state.page = "config"
        st.rerun()

    if cols[1].button("手动输入",use_container_width=True):
        st.session_state.page = "page_input"
        st.rerun()

# 配置页面
def page_config():
    st.title("系统配置")

    if "current_step" not in st.session_state:
        st.session_state.current_step = 0

    # 步骤1：输入基本参数
    if st.session_state.current_step == 0:
        with st.form("basic_params"):
            cols = st.columns(3)
            n = cols[0].number_input("进程数 (n)", 1, 10, 3)
            m = cols[1].number_input("资源种类数 (m)", 1, 5, 2)
            lowest = cols[2].number_input("最低资源数", 1, 5, 2)

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
            st.dataframe(sys_df.style.applymap(
                lambda x: 'color: blue' if x == min(st.session_state.sys_resource) else 'color: pink' if x == max(
                    st.session_state.sys_resource) else ''))

        with resources[1]:
            st.markdown("**可用资源**")
            avail_df = pd.DataFrame(
                [st.session_state.available],
                columns=[f"资源{i}" for i in range(st.session_state.m)],
                index=["可用量"]
            )
            st.dataframe(avail_df.style.applymap(
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
            st.dataframe(max_df.style.applymap(lambda x: 'color: blue' if x == min(
                map(min, st.session_state.max_alloc)) else 'color: pink' if x == max(
                map(max, st.session_state.max_alloc)) else ''))

        with cols[1]:
            st.markdown("**已分配矩阵 (ALLOC)**")
            alloc_df = pd.DataFrame(
                st.session_state.alloc,
                columns=[f"资源{i}" for i in range(st.session_state.m)],
                index=[f"进程{i}" for i in range(st.session_state.n)]
            )
            st.dataframe(alloc_df.style.applymap(
                lambda x: 'color: blue' if x == min(map(min, st.session_state.alloc)) else 'color: pink' if x == max(
                    map(max, st.session_state.alloc)) else ''))

        with cols[2]:
            st.markdown("**需求矩阵 (NEED)**")
            need_df = pd.DataFrame(
                st.session_state.need,
                columns=[f"资源{i}" for i in range(st.session_state.m)],
                index=[f"进程{i}" for i in range(st.session_state.n)]
            )
            st.dataframe(need_df.style.applymap(
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


# 配置页面
def page_input():
   pass

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
        st.dataframe(sys_df.style.applymap(
            lambda x: 'color: blue' if x == min(st.session_state.sys_resource) else 'color: pink' if x == max(
                st.session_state.sys_resource) else ''))

    with resources[1]:
        st.markdown("**可用资源**")
        avail_df = pd.DataFrame(
            [st.session_state.available],
            columns=[f"资源{i}" for i in range(st.session_state.m)],
            index=["可用量"]
        )
        st.dataframe(avail_df.style.applymap(
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
        st.dataframe(sys_df.style.applymap(
            lambda x: 'color: blue' if x == min(st.session_state.sys_resource) else 'color: pink' if x == max(
                st.session_state.sys_resource) else ''))

    with resources[1]:
        st.markdown("**可用资源**")
        avail_df = pd.DataFrame(
            [st.session_state.available],
            columns=[f"资源{i}" for i in range(st.session_state.m)],
            index=["可用量"]
        )
        st.dataframe(avail_df.style.applymap(
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

    # 安全序列计算
    st.subheader("安全序列分析")
    safe_sequences = bankers_algorithm()

    if safe_sequences:
        st.success(f"找到 {len(safe_sequences)} 个安全序列")
        for seq in safe_sequences:
            st.code(" -> ".join([f"P{p}" for p in seq]))
    else:
        st.error("当前状态不安全！")
        st.session_state.state="unsafe"

    # 操作按钮
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⏭️ 计算下一个",use_container_width=True):
            process_next()
        if st.button("⏩ 跳过",use_container_width=True):
            skip_request()
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
    st.session_state.tick += 1


if __name__ == "__main__":
    main()
