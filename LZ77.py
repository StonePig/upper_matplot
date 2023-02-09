

from typing import Any
from dataclasses import dataclass


def lz77_compress(message):
    pointer = 0  # 指针，初始指向第一个位置
    length = 0  # 匹配到的长度
    win = 200  # 窗口长度
    compressed_message = list()  # 使用元组存储
    while True:
        if pointer - win < 0:
            match = message[0:pointer]
        else:
            match = message[pointer - win:pointer]
        while match.find(message[pointer:pointer + length + 1]) != -1:
            length += 1
        first = match.find(message[pointer:pointer + length])
        if pointer - win > 0:
            first += pointer - win
        if length != 0:
            a = (pointer - first, length, message[pointer + length])
            compressed_message.append(a)
            pointer += length + 1
        else:
            b = (0, 0, message[pointer])
            compressed_message.append(b)
            pointer += 1
        length = 0
        if pointer == len(message):
            break
    # print(compressed_message)
    return compressed_message


def lz77_decompress(compressed_message):
    de_msg = b""
    for s in compressed_message:
        if s[0] != 0:
            de_msg += de_msg[(len(de_msg) - s[0]): (len(de_msg) - s[0] + s[1])]
        # de_msg += s[2]
        de_msg += int(s[2]).to_bytes(1, "little")
    # print(de_msg)
    return de_msg


message = b"abcdbbccaaabae1213213242343534532445324532453246aaabaee"  # 编码信息
compressed_message = list()
compressed_message = lz77_compress(message)
lz77_decompress(compressed_message)


@dataclass
class TreeStru:
    weights: int
    left_node: Any = None
    right_node: Any = None


@dataclass
class QueueNodeStru:
    node_content: Any
    wights: int


def construct_tree(node_arry: list) -> list:
    if len(node_arry) > 1:
        # 队列排序
        node_arry.sort(key=lambda x: (x.wights), reverse=False)
        # 获得队列中最小的两个
        node_min_1 = node_arry[0]
        node_min_2 = node_arry[1]

        # 使用最小的两个节点构建树
        new_weghts = node_min_1.wights + node_min_2.wights
        new_tree = TreeStru(
            weights=new_weghts,
            left_node=node_min_1.node_content,
            right_node=node_min_2.node_content,
        )
        # 去掉队列中最小的两个节点，并加入新构造的树
        new_node_arry = node_arry[2:]
        new_node_arry.append(QueueNodeStru(
            node_content=new_tree, wights=new_weghts))

        node_arry = construct_tree(new_node_arry)
    return node_arry


def get_hfm_code_dict(node_dict: dict, root_node: Any, path: str) -> dict:
    if getattr(root_node, "left_node", None) is not None:
        left_node_path = path + "0"
        get_hfm_code_dict(node_dict, root_node.left_node, left_node_path)
        right_node_path = path + "1"
        get_hfm_code_dict(node_dict, root_node.right_node, right_node_path)
    else:
        node_dict[root_node] = path
    return node_dict


def compression_hfm(words_str: str):
    pl = {}
    #  计算字符串中每个字符出现的频率
    for i in words_str:
        if i not in pl.keys():
            pl[i] = words_str.count(i)
    # 构建节点队列
    node_arry = [
        QueueNodeStru(node_content=key, wights=value) for key, value in pl.items()
    ]

    # 生成只有一个节点的队列，该节点就是 霍夫曼树
    node_arry = construct_tree(node_arry)
    hfm_tree = node_arry[0].node_content
    node_dict = get_hfm_code_dict({}, hfm_tree, "")

    code_str = ""
    # 用霍夫曼树压缩字符串，获得编码
    for i in words_str:
        code_str = code_str + node_dict[i]
    return code_str, hfm_tree


def decompression_hfm(hfm_code_str: str, hfm_tree: TreeStru):
    htm_tree_backup = hfm_tree
    words_str = b""
    for i in hfm_code_str:
        if i == "0":
            hfm_tree = hfm_tree.left_node
            if getattr(hfm_tree, "left_node", None) is None:
                words_str = words_str + hfm_tree.to_bytes(1, "little")
                hfm_tree = htm_tree_backup

        elif i == "1":
            hfm_tree = hfm_tree.right_node
            # 根据霍夫曼的构成原理，左子树或右子树若存在必定结对存在
            if getattr(hfm_tree, "left_node", None) is None:
                words_str = words_str + hfm_tree.to_bytes(1, "little")
                hfm_tree = htm_tree_backup
    return words_str


if __name__ == "__main__":
    words_str = b"do or do not"
    hfm_code_str, hfm_tree = compression_hfm(words_str)
    print(hfm_code_str)
    print(hfm_tree)

    words_str = decompression_hfm(hfm_code_str, hfm_tree)
    print(words_str)
