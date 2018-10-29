from django import template
from . import PyExchangeRates

exchange = PyExchangeRates.Exchange('7481ea7007ab448cbc7d40094e1225a6') 

register = template.Library()

@register.filter(name='convert_price')

def convert_price(price, choice):
	a = exchange.withdraw(float(price), 'EUR')
	return a.convert(choice)
