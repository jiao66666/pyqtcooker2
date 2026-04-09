class PotTask:
    def __init__(self, pot_id, action_func, *args, **kwargs):
        self.pot_id = pot_id
        self.action_func = action_func
        self.args = args
        self.kwargs = kwargs

    def execute(self):
        print(f"锅 {self.pot_id} 开始执行")
        self.action_func(*self.args, **self.kwargs)
        print(f"锅 {self.pot_id} 执行完成")
