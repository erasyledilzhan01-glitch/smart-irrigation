import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime
import time

# ==========================================
# 1. КОНФИГУРАЦИЯ
# ==========================================
st.set_page_config(page_title="SmartIrrigation Pro", page_icon="💧", layout="wide")

# Десктопные стили
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }

    .block-container {
        padding-top: 2rem;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
    }

    h1, h2, h3 {
        color: white !important;
        font-weight: 700;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
    }

    [data-testid="stContainer"] {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(10px);
    }

    [data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ПОЛНЫЙ СЛОВАРЬ ПЕРЕВОДОВ
# ==========================================
TRANSLATIONS = {
    'login_title': {'ru': 'Вход в систему', 'kz': 'Жүйеге кіру'},
    'phone': {'ru': 'Номер телефона', 'kz': 'Телефон нөмірі'},
    'otp': {'ru': 'Код из SMS', 'kz': 'SMS коды'},
    'login_btn': {'ru': 'Войти', 'kz': 'Кіру'},
    'role_select': {'ru': 'Выберите роль', 'kz': 'Рөлді таңдаңыз'},
    'role_farmer': {'ru': '👨‍🌾 Фермер', 'kz': '👨‍🌾 Фермер'},
    'role_coop': {'ru': '🏢 Кооператив', 'kz': '🏢 Кооператив'},
    'dashboard': {'ru': '🏠 Главная панель', 'kz': '🏠 Басты панель'},
    'scheme_map': {'ru': '🗺️ Карта полей', 'kz': '🗺️ Алқаптар картасы'},
    'ai_advisor': {'ru': '🤖 AI Советник', 'kz': '🤖 AI Кеңесші'},
    'profile': {'ru': '👤 Профиль', 'kz': '👤 Профиль'},
    'logout': {'ru': '🚪 Выйти', 'kz': '🚪 Шығу'},
    'weather': {'ru': 'Погода', 'kz': 'Ауа райы'},
    'rescued': {'ru': 'Спасено насосов', 'kz': 'Құтқарылған насостар'},
    'consumption': {'ru': 'Расход воды', 'kz': 'Су шығыны'},
    'savings': {'ru': 'Экономия', 'kz': 'Үнемдеу'},
    'active_fields': {'ru': 'Активных полей', 'kz': 'Белсенді алқаптар'},
    'all_working': {'ru': 'Все работают', 'kz': 'Барлығы жұмыс істейді'},
    'forecast': {'ru': 'Прогноз погоды', 'kz': 'Ауа райы болжамы'},
    'today': {'ru': 'Сегодня', 'kz': 'Бүгін'},
    'tomorrow': {'ru': 'Завтра', 'kz': 'Ертең'},
    'after_tomorrow': {'ru': 'Послезавтра', 'kz': 'Арғы күні'},
    'scheduled_tasks': {'ru': 'Запланированный полив', 'kz': 'Жоспарланған суару'},
    'fields_control': {'ru': 'Управление полями', 'kz': 'Алқаптарды басқару'},
    'area': {'ru': 'Площадь', 'kz': 'Аудан'},
    'pressure': {'ru': 'Давление', 'kz': 'Қысым'},
    'emergency': {'ru': 'АВАРИЯ', 'kz': 'АПАТ'},
    'normal': {'ru': 'НОРМА', 'kz': 'ҚАЛЫПТЫ'},
    'humidity': {'ru': 'Влажность', 'kz': 'Ылғалдылық'},
    'temperature': {'ru': 'Температура', 'kz': 'Температура'},
    'pump': {'ru': 'Насос', 'kz': 'Насос'},
    'on': {'ru': 'ВКЛ', 'kz': 'ҚОС'},
    'off': {'ru': 'ВЫКЛ', 'kz': 'ӨШІР'},
    'start_now': {'ru': '▶ Запустить сейчас', 'kz': '▶ Қазір қосу'},
    'schedule': {'ru': '⏰ Запланировать', 'kz': '⏰ Жоспарлау'},
    'stop': {'ru': '⏹ Остановить', 'kz': '⏹ Тоқтату'},
    'call_master': {'ru': '🛠 Вызвать мастера', 'kz': '🛠 Шеберді шақыру'},
    'activity_log': {'ru': 'История действий', 'kz': 'Әрекеттер тарихы'},
    'map_title': {'ru': 'Карта полей (Сетка 1 га)', 'kz': 'Алқаптар картасы (1 га тор)'},
    'map_legend': {'ru': 'Легенда', 'kz': 'Шартты белгілер'},
    'pump_location': {'ru': 'Насос', 'kz': 'Насос'},
    'field_normal': {'ru': 'Поле (норма)', 'kz': 'Алқап (қалыпты)'},
    'field_error': {'ru': 'Поле (авария)', 'kz': 'Алқап (апат)'},
    'ai_title': {'ru': 'AI Советник', 'kz': 'AI Кеңесші'},
    'diagnosis': {'ru': 'ДИАГНОЗ', 'kz': 'ДИАГНОЗ'},
    'recommendation': {'ru': 'РЕКОМЕНДАЦИЯ', 'kz': 'ҰСЫНЫС'},
    'critical': {'ru': 'КРИТИЧНО: Падение давления', 'kz': 'СЫНДЫҚ: Қысым төмендеді'},
    'critical_action': {'ru': 'Автоматика перекрыла клапан. Вызовите мастера',
                        'kz': 'Автоматика қақпақты жапты. Шеберді шақырыңыз'},
    'attention': {'ru': 'ВНИМАНИЕ: Низкая влажность', 'kz': 'НАЗАР: Ылғалдылық төмен'},
    'attention_action': {'ru': 'Запланируйте полив на 90 минут', 'kz': '90 минутқа суаруды жоспарлаңыз'},
    'excellent': {'ru': 'ВСЁ ОТЛИЧНО: Параметры в норме', 'kz': 'ТАМАША: Параметрлер қалыпты'},
    'excellent_action': {'ru': 'Следующий плановый полив завтра в 06:00', 'kz': 'Келесі жоспарлы суару ертең 06:00'},
    'profile_title': {'ru': 'Мой профиль', 'kz': 'Менің профилім'},
    'subscription': {'ru': 'Premium подписка', 'kz': 'Premium жазылым'},
    'until': {'ru': 'до', 'kz': 'дейін'},
    'farm_stats': {'ru': 'Статистика хозяйства', 'kz': 'Шаруашылық статистикасы'},
    'crops': {'ru': 'Культуры', 'kz': 'Дақылдар'},
    'pumps': {'ru': 'Насосы', 'kz': 'Насостар'},
    'reports': {'ru': 'Отчеты и документы', 'kz': 'Есептер және құжаттар'},
    'download_excel': {'ru': 'Скачать Excel', 'kz': 'Excel жүктеу'},
    'download_pdf': {'ru': 'Скачать PDF (Pro)', 'kz': 'PDF жүктеу (Pro)'},
    'field': {'ru': 'Поле', 'kz': 'Алқап'},
    'crop': {'ru': 'Культура', 'kz': 'Дақыл'},
    'status': {'ru': 'Статус', 'kz': 'Күй'},
    'hello': {'ru': 'Привет', 'kz': 'Сәлем'},
    'precipitation': {'ru': 'Осадки', 'kz': 'Жауын-шашын'},
    'week': {'ru': 'за неделю', 'kz': 'апта бойы'},
}


def t(key):
    """Функция перевода"""
    lang = st.session_state.get('language', 'ru')
    return TRANSLATIONS.get(key, {}).get(lang, key)


# ==========================================
# 3. ДАННЫЕ
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.update({
        'logged_in': False,
        'language': 'ru',
        'user_type': 'farmer',
        'pump_states': {},
        'scheduled_tasks': [],
        'activity_log': []
    })

FIELDS_DB = {
    'farmer': [
        {'id': 1, 'name': 'Томаты (Южный)', 'name_kz': 'Қызанақ (Оңтүстік)', 'icon': '🍅', 'area_ha': 5, 'x': 0, 'y': 0,
         'status': 'ok', 'hum': 45, 'temp': 18, 'pressure': 2.3, 'pump_pos': (2, 2)},
        {'id': 2, 'name': 'Люцерна (Север)', 'name_kz': 'Беде (Солтүстік)', 'icon': '🌿', 'area_ha': 12, 'x': 6, 'y': 0,
         'status': 'error', 'hum': 28, 'temp': 20, 'pressure': 0.8, 'pump_pos': (9, 2)},
        {'id': 3, 'name': 'Яблоневый сад', 'name_kz': 'Алма бағы', 'icon': '🍎', 'area_ha': 8, 'x': 0, 'y': 4,
         'status': 'ok', 'hum': 50, 'temp': 17, 'pressure': 2.5, 'pump_pos': (2, 6)}
    ],
    'coop': [
        {'id': 4, 'name': 'Сектор А (Пшеница)', 'name_kz': 'А секторы (Бидай)', 'icon': '🌾', 'area_ha': 36, 'x': 0,
         'y': 0, 'status': 'ok', 'hum': 55, 'temp': 16, 'pressure': 2.4, 'pump_pos': (3, 3)},
        {'id': 5, 'name': 'Сектор Б (Кукуруза)', 'name_kz': 'Б секторы (Жүгері)', 'icon': '🌽', 'area_ha': 25, 'x': 8,
         'y': 0, 'status': 'ok', 'hum': 60, 'temp': 19, 'pressure': 2.6, 'pump_pos': (11, 3)},
        {'id': 6, 'name': 'Сектор В (Овощи)', 'name_kz': 'В секторы (Көкөністер)', 'icon': '🥕', 'area_ha': 16, 'x': 0,
         'y': 7, 'status': 'error', 'hum': 30, 'temp': 22, 'pressure': 0.5, 'pump_pos': (2, 9)},
    ]
}

USER_INFO = {
    'farmer': {'name': 'Арнур Адилкан', 'phone': '+7 777 123 4567', 'total_ha': '25 га', 'sub_end': '01.03.2026'},
    'coop': {'name': 'ТОО "Агро-Юг"', 'phone': '+7 701 987 6543', 'total_ha': '410 га', 'sub_end': '15.12.2026'}
}

WEATHER_DATA = [
    {"day_key": "today", "temp": "+18°C", "icon": "☁️", "rain": "0%"},
    {"day_key": "tomorrow", "temp": "+22°C", "icon": "☀️", "rain": "10%"},
    {"day_key": "after_tomorrow", "temp": "+16°C", "icon": "🌧️", "rain": "80%"}
]


# ==========================================
# 4. СЕТОЧНАЯ КАРТА (1 га = 1 клетка)
# ==========================================
def draw_grid_map(user_type):
    """Рисует карту клетками. Каждая клетка = 1 га земли"""
    fields = FIELDS_DB[user_type]

    fig = go.Figure()

    # Определяем размер сетки
    max_x = max([f['x'] + int(f['area_ha'] ** 0.5) for f in fields]) + 2
    max_y = max([f['y'] + int(f['area_ha'] ** 0.5) for f in fields]) + 2

    # Рисуем каждое поле клетками
    for f in fields:
        # Размер квадрата (примерно корень из площади)
        size = int(f['area_ha'] ** 0.5)

        # Цвет поля
        color = '#86efac' if f['status'] == 'ok' else '#fca5a5'  # Светло-зеленый / Светло-красный

        # Рисуем клетки поля (каждая клетка = 1 га)
        for i in range(size):
            for j in range(size):
                x_pos = f['x'] + i
                y_pos = f['y'] + j

                fig.add_trace(go.Scatter(
                    x=[x_pos, x_pos + 1, x_pos + 1, x_pos, x_pos],
                    y=[y_pos, y_pos, y_pos + 1, y_pos + 1, y_pos],
                    mode='lines',
                    fill='toself',
                    fillcolor=color,
                    line=dict(color='white', width=2),
                    hovertext=f"{f['name' if st.session_state['language'] == 'ru' else 'name_kz']}<br>{t('humidity')}: {f['hum']}%<br>{t('temperature')}: {f['temp']}°C",
                    hoverinfo='text',
                    showlegend=False
                ))

        # Иконка культуры в центре поля
        center_x = f['x'] + size / 2
        center_y = f['y'] + size / 2

        fig.add_trace(go.Scatter(
            x=[center_x],
            y=[center_y],
            mode='text',
            text=[f"{f['icon']}"],
            textfont=dict(size=40),
            hoverinfo='skip',
            showlegend=False
        ))

        # НАСОС (синяя клетка с иконкой ⚙️)
        pump_x, pump_y = f['pump_pos']
        fig.add_trace(go.Scatter(
            x=[pump_x, pump_x + 1, pump_x + 1, pump_x, pump_x],
            y=[pump_y, pump_y, pump_y + 1, pump_y + 1, pump_y],
            mode='lines',
            fill='toself',
            fillcolor='#3b82f6',  # Синий
            line=dict(color='white', width=3),
            hovertext=f"⚙️ {t('pump_location')} #{f['id']}<br>{t('pressure')}: {f['pressure']} бар",
            hoverinfo='text',
            showlegend=False
        ))

        # Иконка насоса
        fig.add_trace(go.Scatter(
            x=[pump_x + 0.5],
            y=[pump_y + 0.5],
            mode='text',
            text=["⚙️"],
            textfont=dict(size=30, color='white'),
            hoverinfo='skip',
            showlegend=False
        ))

    # Сетка фона (пунктирные линии)
    for i in range(max_x + 1):
        fig.add_trace(go.Scatter(
            x=[i, i], y=[0, max_y],
            mode='lines',
            line=dict(color='lightgray', width=0.5, dash='dot'),
            hoverinfo='skip',
            showlegend=False
        ))

    for j in range(max_y + 1):
        fig.add_trace(go.Scatter(
            x=[0, max_x], y=[j, j],
            mode='lines',
            line=dict(color='lightgray', width=0.5, dash='dot'),
            hoverinfo='skip',
            showlegend=False
        ))

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, max_x + 0.5]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, max_y + 0.5], scaleanchor="x",
                   scaleratio=1),
        height=550,
        plot_bgcolor='#f3f4f6',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='closest'
    )

    return fig


# ==========================================
# 5. МОДАЛЬНЫЕ ОКНА
# ==========================================
@st.dialog(f"⏰ {t('schedule')}")
def schedule_irrigation(field_name, field_id):
    st.write(f"**{t('field')}:** {field_name}")

    col1, col2 = st.columns(2)
    with col1:
        start_time = st.time_input("🕐 " + t('start_now').replace('▶ ', ''), value=datetime.now().time())
    with col2:
        duration = st.slider(
            "⏱️ " + ("Длительность (минут)" if st.session_state['language'] == 'ru' else "Ұзақтық (минут)"), 15, 240,
            60, 15)

    repeat = st.checkbox(
        "🔄 " + ("Повторять ежедневно" if st.session_state['language'] == 'ru' else "Күн сайын қайталау"))

    st.info(f"💧 " + ("Прогноз расхода воды" if st.session_state[
                                                   'language'] == 'ru' else "Су шығынының болжамы") + f": ~{duration * 2} " + (
                "литров" if st.session_state['language'] == 'ru' else "литр"))

    if st.button("✅ " + ("Запланировать полив" if st.session_state['language'] == 'ru' else "Суаруды жоспарлау"),
                 type="primary", use_container_width=True):
        st.session_state['scheduled_tasks'].append({
            'field_id': field_id,
            'field_name': field_name,
            'start_time': start_time.strftime("%H:%M"),
            'duration': duration,
            'repeat': repeat
        })
        st.session_state['activity_log'].append({
            'time': datetime.now().strftime("%H:%M"),
            'action': f"{('Запланирован полив' if st.session_state['language'] == 'ru' else 'Суару жоспарланды')}: {field_name}"
        })
        st.success("✅ " + (
            "Полив успешно запланирован!" if st.session_state['language'] == 'ru' else "Суару сәтті жоспарланды!"))
        st.balloons()
        time.sleep(1)
        st.rerun()


@st.dialog(f"🛠 {t('call_master')}")
def show_master_call_form(field_name, field_id):
    st.write(f"**{t('field')}:** {field_name}")
    st.error(f"**{('Проблема' if st.session_state['language'] == 'ru' else 'Мәселе')}:** {t('emergency')}")

    st.divider()

    master = st.selectbox(("Выберите специалиста:" if st.session_state['language'] == 'ru' else "Маманды таңдаңыз:"), [
        "👨‍🔧 Иванов Сергей (+7 777 111 2233) — ⭐ 4.9",
        "👨‍🔧 Нурлан Касым (+7 701 555 6677) — ⭐ 4.7",
        "🚨 " + ("Дежурная бригада (Круглосуточно)" if st.session_state[
                                                          'language'] == 'ru' else "Кезекші бригада (Тәулік бойы)") + " — ⭐ 4.8"
    ])

    urgency = st.radio(("Срочность:" if st.session_state['language'] == 'ru' else "Асығыстық:"), [
        "🔴 " + ("Критично (1 час)" if st.session_state['language'] == 'ru' else "Сындық (1 сағат)"),
        "🟡 " + ("Важно (в течение дня)" if st.session_state['language'] == 'ru' else "Маңызды (күн ішінде)")
    ])

    notes = st.text_area(("Описание проблемы (опционально):" if st.session_state[
                                                                    'language'] == 'ru' else "Мәселе сипаттамасы (міндетті емес):"),
                         placeholder=("Например: Утечка воды возле насоса..." if st.session_state[
                                                                                     'language'] == 'ru' else "Мысалы: Насос маңында су ағуы..."))

    if st.button("📞 " + ("Подтвердить вызов" if st.session_state['language'] == 'ru' else "Шақыруды растау"),
                 type="primary", use_container_width=True):
        st.session_state['activity_log'].append({
            'time': datetime.now().strftime("%H:%M"),
            'action': f"{('Вызван мастер для поля' if st.session_state['language'] == 'ru' else 'Алқапқа шебер шақырылды')}: {field_name}"
        })
        st.success("✅ " + ("Заявка отправлена! Мастер получил уведомление." if st.session_state[
                                                                                   'language'] == 'ru' else "Өтінім жіберілді! Шебер хабарлама алды."))
        st.balloons()
        time.sleep(1)
        st.rerun()


def generate_excel():
    output = BytesIO()
    df = pd.DataFrame({
        t('field'): ["Field 1", "Field 2", "Field 3"],
        t('consumption') + " (м³)": [120, 110, 115],
        t('savings') + " (₸)": [1200, 1500, 1300]
    })
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=t('reports'))
    return output.getvalue()


# ==========================================
# 6. ИНТЕРФЕЙС
# ==========================================
def login_page():
    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>💧 SmartIrrigation Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: white; font-size: 18px;'>" +
                    ("Умная система орошения нового поколения" if st.session_state.get('language',
                                                                                       'ru') == 'ru' else "Жаңа буын ақылды суару жүйесі") +
                    "</p>", unsafe_allow_html=True)

        with st.container(border=True):
            st.subheader(t('login_title'))

            # Выбор языка влияет на ВСЁ приложение
            lang = st.selectbox("🌐 Язык / Тіл", ('ru', 'kz'),
                                format_func=lambda x: "🇷🇺 Русский" if x == 'ru' else "🇰🇿 Қазақша")
            st.session_state['language'] = lang

            role = st.radio(t('role_select'), [t('role_farmer'), t('role_coop')])
            st.text_input(t('phone'), placeholder="+7 777 123 4567")
            st.text_input(t('otp'), type="password", placeholder="• • • •")

            if st.button(t('login_btn'), type="primary", use_container_width=True):
                st.session_state['logged_in'] = True
                st.session_state['user_type'] = 'farmer' if '👨‍🌾' in role else 'coop'
                st.rerun()


def main_app():
    # SIDEBAR (Десктопное меню)
    with st.sidebar:
        st.markdown("# 💧 SmartIrrigation")
        user = USER_INFO[st.session_state['user_type']]
        st.markdown(f"### {t('hello')}, {user['name'].split()[0]}! 👋")

        st.divider()

        # Вертикальное меню
        menu = st.radio("", [
            t('dashboard'),
            t('scheme_map'),
            t('ai_advisor'),
            t('profile')
        ], label_visibility="collapsed")

        st.divider()

        if st.button(t('logout'), use_container_width=True):
            st.session_state['logged_in'] = False
            st.rerun()

    fields = FIELDS_DB[st.session_state['user_type']]

    # === ГЛАВНАЯ ===
    if menu == t('dashboard'):
        st.title("📊 " + t('dashboard'))

        # Прогноз погоды
        st.subheader("🌤️ " + t('forecast'))
        wcols = st.columns(3)
        for i, w in enumerate(WEATHER_DATA):
            with wcols[i]:
                st.metric(f"{w['icon']} {t(w['day_key'])}", w['temp'], f"{t('precipitation')}: {w['rain']}")

        st.divider()

        # KPI метрики
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🛡️ " + t('rescued'), "3", "↑ +1")
        c2.metric("💧 " + t('consumption'), "340 м³", f"↓ -15% {t('week')}")
        c3.metric("💰 " + t('savings'), "15,200 ₸", "↑ +2,100 ₸")
        c4.metric("✅ " + t('active_fields'), str(len(fields)), t('all_working'))

        st.divider()

        # Запланированные задачи
        if st.session_state['scheduled_tasks']:
            st.subheader("⏰ " + t('scheduled_tasks'))
            for task in st.session_state['scheduled_tasks'][-3:]:
                st.info(f"🌱 **{task['field_name']}** — " +
                        ("Старт в" if st.session_state['language'] == 'ru' else "Басталуы") +
                        f" {task['start_time']}, " +
                        ("длительность" if st.session_state['language'] == 'ru' else "ұзақтық") +
                        f" {task['duration']} " +
                        ("мин" if st.session_state['language'] == 'ru' else "мин"))

        # Управление полями
        st.subheader("🌱 " + t('fields_control'))

        for f in fields:
            with st.container(border=True):
                # Заголовок
                field_name = f['name'] if st.session_state['language'] == 'ru' else f['name_kz']

                col_h, col_s = st.columns([4, 1])
                with col_h:
                    st.markdown(f"### {f['icon']} {field_name}")
                    st.caption(f"📏 {t('area')}: {f['area_ha']} га | ⚡ {t('pressure')}: {f['pressure']} бар")
                with col_s:
                    if f['status'] == 'error':
                        st.error(f"🔴 {t('emergency')}")
                    else:
                        st.success(f"🟢 {t('normal')}")

                # Метрики
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("💧 " + t('humidity'), f"{f['hum']}%")
                m2.metric("🌡️ " + t('temperature'), f"{f['temp']}°C")
                m3.metric("⚡ " + t('pressure'), f"{f['pressure']} бар")

                is_on = st.session_state['pump_states'].get(f['id'], False)
                m4.metric(t('pump'), f"🟢 {t('on')}" if is_on else f"⚪ {t('off')}")

                # Кнопки управления
                if f['status'] != 'error':
                    b1, b2, b3 = st.columns(3)
                    if not is_on:
                        if b1.button(t('start_now'), key=f"on_{f['id']}", type="primary"):
                            st.session_state['pump_states'][f['id']] = True
                            st.toast(f"✅ {t('pump')} {f['id']} " + (
                                "запущен!" if st.session_state['language'] == 'ru' else "қосылды!"))
                            st.rerun()
                        if b2.button(t('schedule'), key=f"sched_{f['id']}"):
                            schedule_irrigation(field_name, f['id'])
                    else:
                        if b1.button(t('stop'), key=f"stop_{f['id']}"):
                            st.session_state['pump_states'][f['id']] = False
                            st.toast(f"⏹ {t('pump')} {f['id']} " + (
                                "остановлен" if st.session_state['language'] == 'ru' else "тоқтатылды"))
                            st.rerun()
                else:
                    if st.button(t('call_master'), key=f"master_{f['id']}", type="primary"):
                        show_master_call_form(field_name, f['id'])

        # Лог активности
        if st.session_state['activity_log']:
            st.divider()
            with st.expander(f"📋 {t('activity_log')}", expanded=False):
                for log in reversed(st.session_state['activity_log'][-10:]):
                    st.caption(f"🕐 {log['time']} — {log['action']}")

    # === КАРТА ===
    elif menu == t('scheme_map'):
        st.title(t('map_title'))
        st.caption(("Наведите курсор на клетки для подробной информации. Каждая клетка = 1 гектар земли." if
                    st.session_state['language'] == 'ru' else
                    "Толық ақпарат алу үшін торларға курсорды апарыңыз. Әр тор = 1 гектар жер."))

        fig = draw_grid_map(st.session_state['user_type'])
        st.plotly_chart(fig, use_container_width=True)

        # Легенда
        col_leg1, col_leg2, col_leg3 = st.columns(3)
        col_leg1.success(f"🟩 {t('field_normal')}")
        col_leg2.error(f"🟥 {t('field_error')}")
        col_leg3.info(f"🟦 {t('pump_location')}")

    # === AI ===
    elif menu == t('ai_advisor'):
        st.title(t('ai_title'))

        for f in fields:
            field_name = f['name'] if st.session_state['language'] == 'ru' else f['name_kz']

            with st.expander(f"{f['icon']} {field_name}", expanded=True):
                if f['status'] == 'error':
                    st.error(f"🔴 **{t('diagnosis')}:** {t('critical')}")
                    st.warning(f"🔧 **{t('recommendation')}:** {t('critical_action')}")
                elif f['hum'] < 35:
                    st.warning(f"💧 **{t('diagnosis')}:** {t('attention')}")
                    st.info(f"💡 **{t('recommendation')}:** {t('attention_action')}")
                else:
                    st.success(f"✅ **{t('diagnosis')}:** {t('excellent')}")
                    st.info(f"😴 **{t('recommendation')}:** {t('excellent_action')}")

    # === ПРОФИЛЬ ===
    elif menu == t('profile'):
        st.title(t('profile_title'))
        u = USER_INFO[st.session_state['user_type']]

        # Карточка пользователя
        with st.container(border=True):
            c_img, c_info = st.columns([1, 3])
            with c_img:
                st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
            with c_info:
                st.markdown(f"### {u['name']}")
                st.write(f"📞 {u['phone']}")
                st.success(f"💎 {t('subscription')} ({t('until')} {u['sub_end']})")

        st.divider()

        # Статистика
        st.subheader(t('farm_stats'))
        c1, c2, c3 = st.columns(3)
        c1.metric(t('area'), u['total_ha'])
        c2.metric(t('crops'), str(len(fields)))
        c3.metric(t('pumps'), str(len(fields)))

        # Таблица культур
        crop_df = pd.DataFrame([{
            t('field'): f['name'] if st.session_state['language'] == 'ru' else f['name_kz'],
            t('crop'): f['icon'],
            t('area'): f'{f["area_ha"]} га',
            t('status'): "✅" if f['status'] == 'ok' else "❌"
        } for f in fields])
        st.dataframe(crop_df, use_container_width=True, hide_index=True)

        st.divider()

        # Отчеты
        st.subheader(t('reports'))
        st.write(("Скачать историю полива и журнал аварий для бухгалтерии." if st.session_state['language'] == 'ru' else
                  "Бухгалтерия үшін суару тарихы мен апат журналын жүктеу."))

        r1, r2 = st.columns(2)
        r1.download_button(
            label=f"📥 {t('download_excel')}",
            data=generate_excel(),
            file_name="irrigation_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        r2.button(f"📥 {t('download_pdf')}", disabled=True, use_container_width=True)


if __name__ == "__main__":
    if st.session_state['logged_in']:
        main_app()
    else:
        login_page()
