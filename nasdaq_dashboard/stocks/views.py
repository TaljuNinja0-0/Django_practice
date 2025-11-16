from django.shortcuts import render, redirect, get_object_or_404
from .models import Stock
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import yfinance as yf
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io, base64

plt.rcParams['font.family'] = 'Malgun Gothic'  # 한글 폰트
plt.rcParams['axes.unicode_minus'] = False     # 마이너스 기호 깨짐 방지

# 회원가입
def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, "비밀번호가 일치하지 않습니다.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "이미 존재하는 아이디입니다.")
            return redirect('signup')

        User.objects.create_user(username=username, password=password)
        messages.success(request, "회원가입 성공! 로그인하세요.")
        return redirect('login')

    return render(request, 'stocks/signup.html')

# 로그인
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('stock_list')
        else:
            messages.error(request, "아이디 또는 비밀번호가 잘못되었습니다.")
    return render(request, 'stocks/login.html')

# 로그아웃
def user_logout(request):
    logout(request)
    return redirect('user_login')

# 관심 종목 리스트
def stock_list(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    stocks = Stock.objects.filter(user=request.user)
    return render(request, 'stocks/stock_list.html', {'stocks': stocks})

# 종목 추가
def stock_add(request):
    if request.method == 'POST':
        symbol = request.POST['symbol']
        name = request.POST['name']
        sector = request.POST['sector']
        Stock.objects.create(
            user=request.user,
            symbol=symbol,
            name=name,
            sector=sector
        )
        messages.success(request, f"{symbol} 등록 완료")
        return redirect('stock_list')
    return render(request, 'stocks/stock_form.html')

# 종목 수정
def stock_edit(request, pk):
    if not request.user.is_authenticated:
        return redirect('user_login')
    stock = get_object_or_404(Stock, pk=pk, user=request.user)
    if request.method == 'POST':
        stock.symbol = request.POST['symbol']
        stock.name = request.POST['name']
        stock.sector = request.POST['sector']
        stock.save()
        messages.success(request, f"{stock.symbol} 수정 완료")
        return redirect('stock_list')
    return render(request, 'stocks/stock_form.html', {'stock': stock})

# 종목 삭제
def stock_delete(request, pk):
    if not request.user.is_authenticated:
        return redirect('user_login')
    stock = get_object_or_404(Stock, pk=pk, user=request.user)
    stock.delete()
    messages.success(request, f"{stock.symbol} 삭제 완료")
    return redirect('stock_list')

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


def dashboard(request):
    stocks = Stock.objects.all()
    dashboard_data = []
    sector_rows = []

    for s in stocks:
        try:
            df = yf.download(s.symbol, period="7d", interval="1d", progress=False)
            if df.empty:
                continue

            latest = float(df['Close'].iloc[-1])
            prev = float(df['Close'].iloc[-2]) if len(df) > 1 else latest
            change = round(latest - prev, 2)
            change_percent = round((change / prev) * 100, 2) if prev != 0 else 0

            # 미니 차트 생성
            plt.figure(figsize=(3, 1.5), dpi=100)
            plt.plot(df.index, df['Close'], color=('green' if change > 0 else 'red'))
            plt.xticks([])
            plt.yticks([])
            plt.tight_layout()

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            plt.close()

            dashboard_data.append({
                'symbol': s.symbol,
                'name': s.name,
                'latest': round(latest, 2),
                'change': change,
                'change_percent': change_percent,
                'chart': base64.b64encode(image_png).decode('utf-8'),  # graph -> chart
                'trend': 'up' if change > 0 else 'down'
            })

            # 섹터 분석용
            sector_rows.append({
                'sector': s.sector if s.sector else 'Unknown',
                'change_percent': change_percent
            })

        except Exception as e:
            print(f"Error fetching data for {s.symbol}: {e}")
            continue

    sector_summary = {}
    sector_chart = None

    if sector_rows:
        df_sector = pd.DataFrame(sector_rows)
        grouped = df_sector.groupby('sector')['change_percent'].mean().round(2)
        sector_summary = grouped.to_dict()

        # 섹터 bar chart 생성
        try:
            plt.figure(figsize=(6, 3), dpi=100)
            grouped.plot(kind='bar')
            plt.title("섹터별 평균 상승률 (%)")
            plt.ylabel("상승률 (%)")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            sector_chart = base64.b64encode(buf.getvalue()).decode('utf-8')
            buf.close()
            plt.close()
        except Exception as e:
            print("Sector chart error:", e)
            plt.close()

    # 최종 템플릿 전달
    context = {
        'data': dashboard_data,
        'sector_summary': sector_summary,
        'sector_chart': sector_chart,
    }
    return render(request, 'stocks/dashboard.html', context)