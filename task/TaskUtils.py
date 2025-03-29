from typing import Callable
from inspect import signature


def fn_filter(fn: Callable, *args, **kwargs):
    """根据函数的参数列表过滤输入，并验证参数数量和类型"""
    sig = signature(fn)

    # 过滤kwargs
    filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}

    # 获取函数参数信息
    parameters = list(sig.parameters.values())

    # 检查位置参数数量是否匹配
    if len(args) != len(
        [p for p in parameters if p.default == p.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
    ):
        raise RuntimeError(f"函数 {fn.__name__} 需要 {len(parameters)} 个位置参数，但传入了 {len(args)} 个")

    # 检查位置参数类型是否匹配
    for i, (arg, param) in enumerate(zip(args, parameters)):
        if not isinstance(arg, param.annotation) and param.annotation != param.empty:
            raise RuntimeError(
                f"函数 {fn.__name__} 的第 {i + 1} 个参数需要 {param.annotation} 类型，但传入了 {type(arg)} 类型"
            )

    # 检查关键字参数类型是否匹配
    for name, value in filtered_kwargs.items():
        param = sig.parameters[name]
        if not isinstance(value, param.annotation) and param.annotation != param.empty:
            raise RuntimeError(
                f"函数 {fn.__name__} 的关键字参数 {name} 需要 {param.annotation} 类型，但传入了 {type(value)} 类型"
            )

    # 执行函数
    fn(*args, **filtered_kwargs)