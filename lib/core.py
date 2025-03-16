# lib/core.py
import numpy as np
import random
from typing import List, Dict


def initsysresource(m: int, maxnum: int, lowestnum: int) -> np.ndarray:
    """初始化系统总资源"""
    base = np.random.randint(lowestnum, maxnum, size=m)
    return base


def initmaxalloc(n: int, m: int, sysresource: np.ndarray) -> np.ndarray:
    """初始化最大需求矩阵"""
    max_alloc = np.zeros((n, m), dtype=int)
    for i in range(n):
        for j in range(m):
            max_alloc[i][j] = random.randint(0, sysresource[j])
    return max_alloc


def initalloc(max_alloc: np.ndarray) -> np.ndarray:
    """初始化已分配矩阵"""
    alloc = np.zeros_like(max_alloc)
    for i in range(max_alloc.shape[0]):
        for j in range(max_alloc.shape[1]):
            alloc[i][j] = random.randint(0, max_alloc[i][j])
    return alloc


def calneed(max_alloc: np.ndarray, alloc: np.ndarray) -> np.ndarray:
    """计算需求矩阵"""
    return max_alloc - alloc


def initreqs(n: int, m: int, need: np.ndarray) -> List[Dict]:
    """生成请求序列"""
    reqs = []
    need_cp = need.copy()

    for pid in range(n):
        while np.any(need_cp[pid] > 0):
            req = []
            for j in range(m):
                if need_cp[pid][j] > 0:
                    val = random.randint(1, need_cp[pid][j])
                    req.append(val)
                    need_cp[pid][j] -= val
                else:
                    req.append(0)
            reqs.append({"pid": pid, "request": np.array(req)})

    # 打乱请求顺序
    random.shuffle(reqs)

    # 添加padding
    for _ in range(5):
        reqs.append({"pid": 0, "request": np.zeros(m, dtype=int)})

    return reqs


def refreshavailable(n: int, m: int, sysresource: np.ndarray, alloc: np.ndarray) -> np.ndarray:
    """计算可用资源向量"""
    return sysresource - np.sum(alloc, axis=0)


def bankers_algorithm(alloc: np.ndarray, need: np.ndarray,
                      available: np.ndarray, request: Dict) -> (bool, List):
    """银行家算法核心实现"""
    pid = request['pid']
    req = request['request']

    # 步骤1：检查请求是否超过需求
    if np.any(req > need[pid]):
        return False, []

    # 步骤2：检查系统是否有足够资源
    if np.any(req > available):
        return False, []

    # 尝试分配
    alloc_test = alloc.copy()
    need_test = need.copy()
    available_test = available.copy()

    alloc_test[pid] += req
    need_test[pid] -= req
    available_test -= req

    # 安全检查
    work = available_test.copy()
    finish = np.zeros(alloc.shape[0], dtype=bool)
    safe_seq = []

    while True:
        found = False
        for i in range(alloc.shape[0]):
            if not finish[i] and np.all(need_test[i] <= work):
                work += alloc_test[i]
                finish[i] = True
                safe_seq.append(i)
                found = True
                break
        if not found:
            break

    if np.all(finish):
        return True, safe_seq
    else:
        return False, []
