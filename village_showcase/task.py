
class Task:
    def __init__(self, name, description):
        """
        初始化任务对象。

        :param name: 任务名
        :param description: 任务描述
        """
        self.name = name
        self.description = description
        self.progress = 0.0  # 当前进度，0.0 到 1.0 之间
        self.subtasks = []  # 子任务列表

    def add_subtask(self, subtask):
        """ 将一个子任务添加到当前任务 """
        self.subtasks.append(subtask)

    def remove_subtask(self, subtask):
        """ 从当前任务中移除一个子任务 """
        self.subtasks.remove(subtask)

    def update_progress(self):
        """ 更新当前任务的进度。进度等于所有子任务进度的平均值。"""
        if not self.subtasks:
            return self.progress  # 如果没有子任务，保持当前进度

        total_progress = 0.0
        for subtask in self.subtasks:
            total_progress += subtask.progress

        self.progress = total_progress / len(self.subtasks)  # 计算子任务的平均进度

        return self.progress

    def __repr__(self):
        return f"Task({self.name}, progress={self.progress:.2f})"
