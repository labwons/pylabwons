import pprint

class DataDict(dict):
    """
    데이터 저장 Dictionary
    built-in: dict의 확장으로 저장 요소에 대해 attribute 접근 방식을 허용
    기본 제공 Alias (별칭): dD, dDict

    사용 예시)
        myData = DataDict(name='JEHYEUK', age=34, division='Vehicle Solution Team')
        print(myData.name, myData['name'], myData.name == myData['name'])

        /* ----------------------------------------------------------------------------------------
        | 결과
        -------------------------------------------------------------------------------------------
        | JEHYEUK JEHYEUK True
        ---------------------------------------------------------------------------------------- */
    """
    def __init__(self, data=None, **kwargs):
        super().__init__()

        data = data or {}
        data.update(kwargs)
        for key, value in data.items():
            if isinstance(value, dict):
                value = DataDict(**value)
            self[key] = value

    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        return super().__getattribute__(attr)

    def __setattr__(self, attr, value):
        if isinstance(value, dict):
            self[attr] = DataDict(**value)
        else:
            self[attr] = value

    def __str__(self) -> str:
        return pprint.pformat(self)


# Alias
DataDictionary = DataDict