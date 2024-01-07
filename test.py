from currency_converter import CurrencyConverter

currency_conv = CurrencyConverter()
newArr = [1, 0]
print(currency_conv.convert(100, "USD", "EUR"))
for i in newArr:
    i = currency_conv.convert(100, "USD", "EUR")
    
print(newArr)