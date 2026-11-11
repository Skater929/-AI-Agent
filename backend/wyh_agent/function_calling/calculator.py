def calculator(a, b, operation):
    if operation == "add":
        return str(a + b)
    if operation == "multiply":
        return str(a * b)
    if operation == "divide":
        # 三元运算符
        # 先判断 b == 0，为真就返回 "除数不能为0"，为假就返回 str(a / b)
        return "除数不能为0" if b == 0 else str(a / b)
    return "不支持"
