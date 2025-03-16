import streamlit as st
import numpy as np
import random
from copy import deepcopy

# 页面配置
st.set_page_config(page_title="Banker's Algorithm Simulator", layout="wide")

# 初始化session state
if 'page' not in st.session_state:
    st.session_state.page = 'Welcome'
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0


# 工具函数
def initsysresource(m, maxnum, lowestnum):
    return [random.randint(0, maxnum) + lowestnum for _ in range(m)]


def initmaxalloc(n, m, sysresource):
    return [[random.randint(0, sysresource[j]) for j in range(m)] for i in range(n)]


def initalloc(n, m, maxalloc):
    return [[random.randint(0, maxalloc[i][j]) for j in range(m)] for i in range(n)]


def calneed(maxalloc, alloc):
    return [[maxalloc[i][j] - alloc[i][j] for j in range(len(maxalloc[0]))] for i in range(len(maxalloc))]


def initreqs(n, m, need):
    reqs = []
    need_cp = deepcopy(need)

    for i in range(n):
        while sum(need_cp[i]) > 0:
            req = [0] * m
            for j in range(m):
                if need_cp[i][j] > 0:
                    req[j] = random.randint(1, need_cp[i][j])
                    need_cp[i][j] -= req[j]
                else:
                    req[j] = 0
            reqs.append((i, req))

    random.shuffle(reqs)
    for _ in range(5):  # 添加padding
        reqs.append((0, [0] * m))
    return reqs


def refreshavailable(n, m, maxresource, alloc):
    used = [sum(alloc[i][j] for i in range(n)) for j in range(m)]
    return [maxresource[j] - used[j] for j in range(m)]


def is_safe(available, need, alloc):
    n = len(need)
    work = available.copy()
    finish = [False] * n
    safe_seq = []

    while True:
        found = False
        for i in range(n):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(len(work))):
                for j in range(len(work)):
                    work[j] += alloc[i][j]
                finish[i] = True
                safe_seq.append(i)
                found = True
                break
        if not found:
            break
    return all(finish), safe_seq


# 页面渲染函数
def welcome_page():
    st.title("银行家算法模拟系统")
    st.write("欢迎使用银行家算法模拟系统！")
    st.write("本系统可以帮助您理解操作系统中资源分配的安全算法")
    if st.button("开始模拟"):
        st.session_state.page = 'config'


def config_page():
    st.title("系统配置")

    if 'n' not in st.session_state:
        st.session_state.n = 3
    if 'm' not in st.session_state:
        st.session_state.m = 2
    if 'lowestnum' not in st.session_state:
        st.session_state.lowestnum = 3

    with st.form("config_form"):
        cols = st.columns(3)
        with cols[0]:
            n = st.number_input("进程数量 (n)", 1, 10, st.session_state.n)
        with cols[1]:
            m = st.number_input("资源种类数 (m)", 1, 5, st.session_state.m)
        with cols[2]:
            lowestnum = st.number_input("每类资源最低数量", 1, 10, st.session_state.lowestnum)

        if st.form_submit_button("确认配置"):
            st.session_state.n = n
            st.session_state.m = m
            st.session_state.lowestnum = lowestnum

            # 初始化系统资源
            maxresource = 20
            sysresource = initsysresource(m, maxresource, lowestnum)
            maxalloc = initmaxalloc(n, m, sysresource)
            alloc = initalloc(n, m, maxalloc)
            need = calneed(maxalloc, alloc)
            reqs = initreqs(n, m, need)
            available = refreshavailable(n, m, sysresource, alloc)

            # 保存到session state
            st.session_state.sysresource = sysresource
            st.session_state.maxalloc = maxalloc
            st.session_state.alloc = alloc
            st.session_state.need = need
            st.session_state.reqs = reqs
            st.session_state.available = available
            st.session_state.tick = 0
            st.session_state.current_step = 1

    if st.session_state.current_step >= 1:
        st.subheader("系统配置结果")
        cols = st.columns(2)
        with cols[0]:
            st.write("### 资源总量")
            st.write(st.session_state.sysresource)

            st.write("### 最大分配矩阵")
            st.dataframe(st.session_state.maxalloc)

            st.write("### 已分配矩阵")
            st.dataframe(st.session_state.alloc)

        with cols[1]:
            st.write("### 需求矩阵")
            st.dataframe(st.session_state.need)

            st.write("### 可用资源")
            st.write(st.session_state.available)

            st.write("### 请求序列（前10个）")
            st.table(st.session_state.reqs[:10])

        if st.button("确认进入模拟"):
            st.session_state.page = 'simulator'


def simulator_page():
    st.title("模拟运行")
    tick = st.session_state.tick

    # 显示当前状态
    cols = st.columns([2, 1])
    with cols[0]:
        st.write("### 当前时钟刻:", tick)
        st.write("### 当前请求:")
        if tick < len(st.session_state.reqs):
            req = st.session_state.reqs[tick]
            st.write(f"进程 {req[0]} 请求资源: {req[1]}")

    # 显示矩阵
    with cols[1]:
        st.write("### 可用资源")
        st.write(st.session_state.available)

    st.write("### 资源分配状态")
    cols = st.columns(3)
    with cols[0]:
        st.write("最大分配矩阵")
        st.dataframe(st.session_state.maxalloc)
    with cols[1]:
        st.write("已分配矩阵")
        st.dataframe(st.session_state.alloc)
    with cols[2]:
        st.write("需求矩阵")
        st.dataframe(st.session_state.need)

    # 安全检查
    safe, seq = is_safe(st.session_state.available,
                        st.session_state.need,
                        st.session_state.alloc)

    st.write("### 安全状态检查")
    if safe:
        st.success(f"系统安全！安全序列: {seq}")
    else:
        st.error("系统不安全！")

    # 控制按钮
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("计算下一个") and safe:
            process_next()
    with col2:
        if st.button("跳过请求"):
            process_skip()
    with col3:
        if st.button("返回主页"):
            st.session_state.page = 'Welcome'


def process_next():
    tick = st.session_state.tick
    req = st.session_state.reqs[tick]
    pid = req[0]
    request = req[1]

    # 模拟分配
    alloc = st.session_state.alloc
    need = st.session_state.need

    # 检查请求是否合法
    if all(request[j] <= need[pid][j] for j in range(len(request))):
        # 尝试分配
        for j in range(len(request)):
            alloc[pid][j] += request[j]
            need[pid][j] -= request[j]

        # 检查是否需要释放资源
        if all(n == 0 for n in need[pid]):
            # 释放资源
            for j in range(len(alloc[pid])):
                st.session_state.available[j] += alloc[pid][j]
                alloc[pid][j] = 0

        st.session_state.tick += 1


def process_skip():
    st.session_state.tick += 1


# 主程序
def main():
    st.sidebar.title("导航")
    page = st.sidebar.radio("选择页面",
                            ["Welcome", "config", "simulator"],
                            index=["Welcome", "config", "simulator"].index(st.session_state.page))

    if page == "Welcome":
        welcome_page()
    elif page == "config":
        config_page()
    elif page == "simulator":
        simulator_page()


if __name__ == "__main__":
    main()
