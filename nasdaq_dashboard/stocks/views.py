from django.shortcuts import render, redirect
from .models import Stock
#from django.contrib.auth.decorators import login_required
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io, base64

plt.rcParams['font.family'] = 'Malgun Gothic'  # 한글 폰트
plt.rcParams['axes.unicode_minus'] = False     # 마이너스 기호 깨짐 방지

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

# 종목 상세 페이지
def stock_detail(request, symbol):
    try:
        stock = Stock.objects.get(symbol=symbol)
    except Stock.DoesNotExist:
        return render(request, 'stocks/stock_detail.html', {
            'error': f"'{symbol}' 종목이 존재하지 않습니다."
        })

    # yfinance로 1개월 데이터 가져오기
    df = yf.download(symbol, period="1mo", group_by='ticker')

    # DataFrame이 MultiIndex인지 확인 후 처리
    if isinstance(df, pd.DataFrame):
        if symbol in df.columns:  # MultiIndex인 경우
            df = df[symbol]

    # Matplotlib으로 종가 차트 생성
    graphic = None
    if not df.empty:
        plt.figure(figsize=(10, 4))
        plt.plot(df.index, df['Close'], marker='o', linestyle='-')
        plt.title(f"{symbol} (1개월 종가)")
        plt.xlabel("Date")
        plt.ylabel("Close Price")
        plt.grid(True)

        buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        graphic = base64.b64encode(image_png).decode('utf-8')

        latest_price = float(df['Close'].iloc[-1])
        open_price = float(df['Open'].iloc[-1])
        high_price = float(df['High'].iloc[-1])
        low_price = float(df['Low'].iloc[-1])
    else:
        latest_price = open_price = high_price = low_price = "데이터 없음"

    # HTML에 데이터 전달
    context = {
        'stock': stock,
        'graph': graphic,
        'latest_price': latest_price,
        'open_price': open_price,
        'high_price': high_price,
        'low_price': low_price,
    }

    return render(request, 'stocks/stock_detail.html', context)