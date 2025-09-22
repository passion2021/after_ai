from datetime import timedelta, datetime


class TimerTools:
    _instance = None

    def __init__(self):
        self.now_time = datetime.now()

    def preview_now_time(self):
        return f'{self.now_time.strftime("%Y/%m/%d %H时%M分")} {self.zh_weekday()}'

    def preview_time(self, input_time: datetime = None):
        return f'{input_time.strftime("%Y/%m/%d %H时%M分")} {self.zh_weekday(input_time)}'

    def zh_weekday(self, input_time: datetime = None):
        if input_time is None:
            input_time = self.now_time
        return f"周{['一', '二', '三', '四', '五', '六', '日'][input_time.weekday()]}"

    def wechat_preview_past_time(self, past_time: datetime | str = None):
        """
         模拟微信的时间显示方式。
         如果是当天，显示格式为“12：23”，
         如果是昨天则显示为“昨天 12：23”，
         如果是更早则显示为星期“周二 23：31” ，
         如果是超越一周的过去则显示“10月10日 下午15：23”
         如果是一年前的则显示具体“2023年10月24日 晚上20：49”
        """
        sep = "时"
        if past_time is None:
            past_time = self.now_time
        if isinstance(past_time, str):
            past_time = datetime.strptime(past_time, '%Y-%m-%d %H:%M:%S')

        delta = self.now_time - past_time
        today_start = self.now_time.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        week_start = self.now_time.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(
            days=self.now_time.weekday())

        def get_time_period(hour):
            if 5 <= hour < 12:
                return "上午"
            elif 12 <= hour < 18:
                return "下午"
            return "晚上"

        if today_start <= past_time <= self.now_time:
            return f"今天 {get_time_period(past_time.hour)}{past_time.strftime(f'%H{sep}%M')}"
        elif yesterday_start <= past_time < today_start:
            return f"昨天 {get_time_period(past_time.hour)}{past_time.strftime(f'%H{sep}%M')}"
        elif 1 < delta.days < 7 and (past_time >= week_start):
            return f"{self.zh_weekday(past_time)} {get_time_period(past_time.hour)}{past_time.strftime(f'%H{sep}%M')}"
        elif delta.days < 365:
            return f"{past_time.strftime('%m月%d日')} {get_time_period(past_time.hour)}{past_time.strftime(f'%H{sep}%M')}"
        return f"{past_time.strftime('%Y年%m月%d日')} {get_time_period(past_time.hour)}{past_time.strftime(f'%H{sep}%M')}"


Timer = TimerTools()

if __name__ == '__main__':
    print(TimerTools().preview_time(datetime.now()))
    # test_times = [
    #     datetime.now(),
    #     datetime.now() - timedelta(days=1),
    #     datetime.now() - timedelta(days=3),  # 这个显示 周日 12:14 但是不应该显示这个 因为周日已经是上周了，最多显示到周一
    #     datetime.now() - timedelta(days=20),
    #     datetime.now() - timedelta(days=400)
    # ]
    #
    # for test_time in test_times:
    #     print(f"原始时间: {test_time}")
    #     print(f"格式化后: {Timer.wechat_preview_past_time(test_time)}")
    #     print()
