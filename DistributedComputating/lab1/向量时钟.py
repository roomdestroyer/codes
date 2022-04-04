from multiprocessing import Process, Queue, Lock
import random
import time


def task(i, msg_q, lock, p_num, MaxTime):
    # 初始化每个结点自身的向量时钟数组
    vector_clock = [0] * p_num
    # 模拟MaxTime个时间点
    for i_ in range(MaxTime):
        # 非最终时刻，更新数据 | 发送信息
        if i_ != MaxTime - 1:
            # 结点自身数据有4/10=0.4的概率更新
            if random.randint(0, 9) < 5:
                vector_clock[i] += 1
            # 结点有2/10=0.2的概率与另一个随机结点发生通信
            if random.randint(0, 9) < 3:
                msg_q.put([random.randint(0, p_num - 1), vector_clock])
        # 最终时刻，只同步信息
        else:
            time.sleep(1)
        # 倒数第二时刻，广播同步信息(如果并发进程数目过多，该循环会消耗大量时间，
        # 导致即使在最后时刻不time.sleep(1)也能同步全网时间)
        if i_ == MaxTime - 2:
            for j in range(p_num):
                msg_q.put([j, vector_clock])

        # 结点从消息队列中依次取出消息，看哪些是与自己通信的
        # 在最坏的情况，队列中同时存在 p_num * MaxTime 条消息
        for j in range(p_num * MaxTime):
            value = msg_q.get(True)
            # -1为中止标志，防止队列为空阻塞进程
            if value == -1:
                msg_q.put(-1)
                continue
            # 当前消息的目标结点是自己
            if value[0] == i:
                from_clock = value[1]
                # 比较自己的向量时钟和源结点的向量时钟，更新自身信息
                for index in list(range(p_num)):
                    if vector_clock[index] < from_clock[index]:
                        vector_clock[index] = from_clock[index]
                # 同时
            else:
                msg_q.put(value)

    lock.acquire()
    print('子进程', i, ": ", end=" ")
    print(vector_clock)
    lock.release()


if __name__ == '__main__':
    start = time.time()

    q = Queue()
    lock_ = Lock()
    q.put(-1)

    # 设置并发进程数量及模拟进程运行时间
    process_num = 3
    max_time = 20

    p = []
    for pi in range(process_num):
        p.append(Process(target=task, args=(pi, q, lock_, process_num, max_time)))
    for item in p:
        item.start()
    for item in p:
        item.join()

    end = time.time()
    print("总共用时{}秒".format((end - start)))
