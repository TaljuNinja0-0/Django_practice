from django.shortcuts import render, redirect
from .models import Stock
#from django.contrib.auth.decorators import login_required

#@login_required
def stock_list(request):
    #stocks = Stock.objects.filter(user=request.user)
    #Stock.objects.create(symbol=symbol, name=name, sector=sector, user=request.user)
    stocks = Stock.objects.all()
    return render(request, 'stocks/stock_list.html', {'stocks': stocks})


#@login_required
def stock_add(request):
    if request.method == 'POST':
        symbol = request.POST['symbol']
        name = request.POST['name']
        sector = request.POST['sector']
        #Stock.objects.create(user=request.user, symbol=symbol, name=name, sector=sector)
        Stock.objects.create(symbol=symbol, name=name, sector=sector)
        return redirect('stock_list')
    return render(request, 'stocks/stock_form.html')