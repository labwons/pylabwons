from datetime import datetime
import pprint, os


class classproperty:
    """
    @classmethod를 @property 형식으로 사용

    사용 예시)
        class MyClass:
            _something:str = ''

            @classmethod
            def getSomething(cls) -> str:
                return cls._something

            @classproperty
            def something(cls) -> str:
                return cls._something
    """
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        return self.func(owner)

    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError("can't set attribute (no setter defined)")
        # instance는 None (클래스 접근)일 때가 많음
        owner = instance if instance is not None else type(instance)
        return self.fset(owner, value)

    def setter(self, func):
        self.fset = func
        return self

class metaclass(type):
    """
    클래스의 던더 메소드 정의를 위한 메타 클래스
    메타 클래스로 지정할 경우 하위 클래스 변수를 명시적으로 지정해주어야 함.
    """
    _iter_ = None
    _str_ = None

    def __iter__(cls) -> iter:
        if cls._iter_ is None:
            raise TypeError('Not Iterable: {cls._iter_} is not defined')
        return iter(cls._iter_)

    def __str__(cls) -> str:
        if cls._str_ is None:
            raise TypeError('Not Printable: {cls._str_} is not defined')
        return str(cls._str_)

class DataDictionary(dict):
    """
    데이터 저장 Dictionary
    built-in: dict의 확장으로 저장 요소에 대해 attribute 접근 방식을 허용
    기본 제공 Alias (별칭): dD, dDict

    사용 예시)
        myData = DataDictionary(name='JEHYEUK', age=34, division='Vehicle Solution Team')
        print(myData.name, myData['name'], myData.name == myData['name'])

    출력)
        JEHYEUK JEHYEUK True
    """
    def __init__(self, data=None, **kwargs):
        super().__init__()
        self._methods = {}

        data = data or {}
        data.update(kwargs)
        for key, value in data.items():
            self.__setattr__(key, value)

    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        if attr in self._methods:
            return self._methods[attr]
        return super().__getattribute__(attr)

    def __setattr__(self, attr, value):
        if attr.startswith("_"):
            return super().__setattr__(attr, value)
        if callable(value) and not value in [int, float, str, datetime]:
            self._methods[attr] = value
        elif isinstance(value, dict):
            self[attr] = DataDictionary(**value)
        else:
            self[attr] = value

    def __str__(self):
        return pprint.pformat(dict(self))


class Path(str):

    def __new__(cls, path:str):
        if os.path.isfile(path):
            raise TypeError(f'Invalid Path Type: {path}')
        os.makedirs(path, exist_ok=True)
        return super().__new__(cls, path)

    def __init__(self, path:str):
        self._path = path

    def __getitem__(self, item):
        if isinstance(item, int) or isinstance(item, slice):
            return super().__getitem__(item)
        if isinstance(item, str):
            if '.' in item:
                return os.path.join(self._path, item)
            return Path(os.path.join(self._path, item))
        if isinstance(item, (list, tuple)):
            sub = self._path
            for dr in item[:-1]:
                sub = os.path.join(sub, dr)
                os.makedirs(sub, exist_ok=True)
            if '.' in item[-1]:
                return os.path.join(self._path, *item)
            return Path(os.path.join(self._path, *item))

        raise TypeError(f'Invalid Path Type: {item}')


if __name__ == "__main__":
    path = Path(r'E:\SIDEPROJ\pylabwons\labwons-archive\tickers')
    print(path['test', 'test.txt'])