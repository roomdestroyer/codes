import random
from multiprocessing import Process, Queue, Lock
import time


def task(i, msg_q, lock):
    # 初始化每个结点自身的向量时钟数组
    vector_clock = [0, 0, 0]
    MaxTime = 50
    # 模拟MaxTime个时间点
    for i_ in range(MaxTime):
        # 结点自身数据有4/10=0.4的概率更新
        if random.randint(0, 9) < 5:
            vector_clock[i] += 1
        # 结点有2/10=0.2的概率与另一个随机结点发生通信
        if random.randint(0, 10) < 3:
            msg_q.put([random.randint(0, 2), vector_clock])

        # 在最终时间，结点广播自身时钟全网同步
        """
        if i_ == MaxTime - 1:
            time.sleep(10)
            msg_q.put([0, vector_clock])
            msg_q.put([1, vector_clock])
            msg_q.put([2, vector_clock])
        """
        # 结点从消息队列中依次取出消息，看哪些是与自己通信的
        for j in range(20):
            value = msg_q.get(True)
            # -1为中止标志，防止队列为空阻塞进程
            if value == -1:
                msg_q.put(-1)
                continue
            # 当前消息的目标结点是自己
            if value[0] == i:
                from_clock = value[1]
                # 比较自己的向量时钟和源结点的向量时钟，更新自身信息
                for index in [0, 1, 2]:
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
    p1 = Process(target=task, args=(0, q, lock_))
    p2 = Process(target=task, args=(1, q, lock_))
    p3 = Process(target=task, args=(2, q, lock_))
    p1.start()
    p2.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()

    end = time.time()
    print("总共用时{}秒".format((end - start)))
