# app.py
import streamlit as st
import numpy as np
import pandas as pd
from lib import core


def welcome_page():
    col1, col2 = st.columns([3, 2])

    with col1:
        st.title("银行家算法教学模拟系统")
        st.image("https://upload.wikimedia.org/wikipedia/commons/d/d9/Edsger_Wybe_Dijkstra.jpg",
                 caption="Edsger W. Dijkstra - 银行家算法提出者",
                 width=300)

    with col2:
        st.markdown("### 算法简介")
        st.write("银行家算法是避免死锁的经典算法，由Edsger Dijkstra于1965年提出...")

        if st.button("开始实验"):
            st.session_state.current_page = "home"
            st.rerun()
        if st.button("关于Dijkstra"):
            st.session_state.current_page = "about"
            st.rerun()


def display_vector(name, vector, col_name="资源"):
    """显示资源向量"""
    st.subheader(name)
    df = pd.DataFrame([vector],
                      columns=[f"{col_name}{i + 1}" for i in range(len(vector))],
                      index=["系统资源"])
    st.dataframe(df, use_container_width=True)


def display_matrix(name, matrix, row_name="进程", col_name="资源"):
    """显示二维矩阵"""
    st.subheader(name)
    df = pd.DataFrame(matrix,
                      columns=[f"{col_name}{i + 1}" for i in range(matrix.shape[1])],
                      index=[f"{row_name}{i + 1}" for i in range(matrix.shape[0])])
    st.dataframe(df.style.format(precision=0), use_container_width=True)


def display_list(name, data_list, col_titles):
    """显示请求列表"""
    st.subheader(name)
    if isinstance(data_list[0], dict):
        formatted_data = []
        for item in data_list:
            formatted = {
                col_titles[0]: item["pid"] + 1,
                col_titles[1]: str(item["request"].tolist())
            }
            formatted_data.append(formatted)
        df = pd.DataFrame(formatted_data)
    else:
        df = pd.DataFrame(data_list, columns=col_titles)

    st.dataframe(df,
                 column_config={
                     col_titles[1]: {"width": "large"}
                 },
                 use_container_width=True,
                 hide_index=True)


def home_page():
    st.title("实验参数配置")

    if "current_step" not in st.session_state:
        st.session_state.current_step = 0

    # 步骤1：输入基本参数
    if st.session_state.current_step == 0:
        with st.form("basic_params"):
            cols = st.columns(2)
            with cols[0]:
                n = st.number_input("进程数量 (n)", min_value=1, max_value=10, step=4)
                m = st.number_input("资源类型数 (m)", min_value=1, max_value=5, step=2)
            with cols[1]:
                lowest = st.number_input("每类资源最低数量", min_value=0, max_value=10, value=3)
                sourcemaxnum = st.number_input("每类资源最大数量", min_value=0, max_value=100, value=20)

            if st.form_submit_button("确认"):
                st.session_state.n = int(n)
                st.session_state.m = int(m)
                st.session_state.lowest = int(lowest)
                st.session_state.current_step = 1
                st.session_state.sourcemaxnum = int(sourcemaxnum)
                st.rerun()

    # 步骤2：系统初始化
    elif st.session_state.current_step == 1:
        # 初始化系统资源
        sys_resource = core.initsysresource(
            m=st.session_state.m,
            maxnum=st.session_state.sourcemaxnum,
            lowestnum=st.session_state.lowest
        )

        # 初始化最大分配矩阵
        max_alloc = core.initmaxalloc(
            n=st.session_state.n,
            m=st.session_state.m,
            sysresource=sys_resource
        )

        # 初始化已分配矩阵
        alloc = core.initalloc(max_alloc)

        # 计算需求矩阵
        need = core.calneed(max_alloc, alloc)

        # 生成请求序列
        reqs = core.initreqs(
            n=st.session_state.n,
            m=st.session_state.m,
            need=need
        )

        # 保存到session
        st.session_state.update({
            "sys_resource": sys_resource,
            "max_alloc": max_alloc,
            "alloc": alloc,
            "need": need,
            "reqs": reqs,
            "tick": 0,
            "available": core.refreshavailable(
                st.session_state.n,
                st.session_state.m,
                sys_resource,
                alloc
            )
        })

        # 显示结果
        st.success("系统初始化完成！")

        display_vector("总资源向量", sys_resource, "资源类型")
        display_matrix("最大需求矩阵", max_alloc, "进程", "资源类型")
        display_matrix("已分配矩阵", alloc, "进程", "资源类型")
        display_matrix("需求矩阵", need, "进程", "资源类型")
        display_list("请求序列", reqs, ["进程ID", "请求资源"])
        display_vector("当前可用资源", st.session_state.available, "资源类型")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ 确认配置进入模拟"):
                st.session_state.current_page = "sim"
                st.rerun()
        with col2:
            if st.button("🔄 重新生成配置"):
                st.session_state.current_step = 0
                st.rerun()


def sim_page():
    st.title("算法模拟执行")

    # 显示当前状态
    st.subheader(f"🕒 当前时钟周期: {st.session_state.tick}")

    cols = st.columns(2)
    with cols[0]:
        display_vector("当前可用资源", st.session_state.available, "资源类型")
    with cols[1]:
        display_matrix("已分配矩阵", st.session_state.alloc, "进程", "资源类型")

    # 获取当前请求
    current_req = st.session_state.reqs[st.session_state.tick]
    st.subheader(f"📨 当前请求: 进程{current_req['pid'] + 1} -> {current_req['request'].tolist()}")

    # 执行银行家算法
    if st.button("🔒 执行安全检查"):
        safe, seq = core.bankers_algorithm(
            st.session_state.alloc,
            st.session_state.need,
            st.session_state.available.copy(),
            current_req
        )

        if safe:
            st.success("✅ 安全！允许分配")
            st.write("🔑 安全序列:", [f"进程{i + 1}" for i in seq])

            # 更新资源分配
            st.session_state.alloc[current_req['pid']] += current_req['request']
            st.session_state.available = core.refreshavailable(
                st.session_state.n,
                st.session_state.m,
                st.session_state.sys_resource,
                st.session_state.alloc
            )
            st.session_state.tick += 1
            st.rerun()
        else:
            st.error("❌ 不安全！拒绝请求")
            st.session_state.tick += 1
            st.rerun()


def main():
    st.set_page_config(page_title="银行家算法模拟",
                       layout="wide",
                       page_icon="🏦")

    if "current_page" not in st.session_state:
        st.session_state.current_page = "welcome"

    if st.session_state.current_page == "welcome":
        welcome_page()
    elif st.session_state.current_page == "home":
        home_page()
    elif st.session_state.current_page == "sim":
        sim_page()


if __name__ == "__main__":
    main()
