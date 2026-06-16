# app.py -- 지점 매출 분석 대시보드 (화면)
import streamlit as st
from utils import (total_sales, average_sales, to_grade, grade_to_incentive,
                   quarter_average, quarter_top, grade_distribution,
                   rank_list, achievement_rate)

st.set_page_config(page_title="매출 분석 대시보드", layout="wide")

# 1. 화면 최상단: 배너 이미지
st.image("banner.png", use_container_width=True) # width="stretch" 대신 최신 Streamlit 규격 적용
st.title("지점 매출 분석 대시보드")

QUARTERS = ["1분기", "2분기", "3분기"]

# 처음 실행 시 샘플 지점 데이터를 세션에 넣어 둔다. (다시 실행돼도 유지) / 단위: 백만원
if "branches" not in st.session_state:
    st.session_state.branches = [
        {"지점": "강남점", "1분기": 150, "2분기": 130, "3분기": 140},
        {"지점": "홍대점", "1분기": 90,  "2분기": 110, "3분기": 100},
        {"지점": "판교점", "1분기": 120, "2분기": 100, "3분기": 95},
        {"지점": "부산점", "1분기": 80,  "2분기": 90,  "3분기": 85},
        {"지점": "대전점", "1분기": 50,  "2분기": 55,  "3분기": 45},
    ]

branches = st.session_state.branches

# 2. 화면 상단: 요약 지표 (탭 위에 배치하여 항상 고정 노출되도록 수정)
col1, col2, col3 = st.columns(3)
col1.metric("지점 수", f"{len(branches)}개")

if len(branches) > 0:
    avgs = [average_sales(b) for b in branches]
    overall = sum(avgs) / len(avgs)
else:
    overall = 0
col2.metric("전체 평균(분기)", round(overall, 2))
col3.metric("목표 달성률", f"{achievement_rate(branches):.1f}%")

st.markdown("---") # 시각적 구분을 위한 구분선

# 3. 하단: 탭 4개 구성
tab1, tab2, tab3, tab4 = st.tabs(["지점 입력", "지점별 실적", "분기별 통계", "순위 & 등급 분포"])

# --- Tab 1 : 지점 추가 ---
with tab1:
    st.header("지점 추가")
    # 폼(form)을 사용하면 입력 시마다 화면이 새로고침되는 현상을 방지할 수 있어 매끄럽습니다.
    with st.form("add_branch_form", clear_on_submit=True):
        name = st.text_input("지점명")
        q1 = st.number_input("1분기 매출", 0, 1000, 0)
        q2 = st.number_input("2분기 매출", 0, 1000, 0)
        q3 = st.number_input("3분기 매출", 0, 1000, 0)
        submit_button = st.form_submit_button("추가")
        
        if submit_button:
            if name.strip() == "":
                st.error("지점명을 입력해주세요.")
            else:
                branches.append({"지점": name, "1분기": q1, "2분기": q2, "3분기": q3})
                st.success(f"{name} 지점을 추가했습니다.")
                st.rerun() # 상단 지표 실시간 갱신을 위해 앱 재실행 예외처리

# --- Tab 2 : 지점별 실적표 ---
with tab2:
    st.header("지점별 실적표")
    table = []
    for b in branches:
        avg = average_sales(b)
        grade = to_grade(avg)
        table.append({
            "지점": b["지점"],
            "1분기": b["1분기"], 
            "2분기": b["2분기"], 
            "3분기": b["3분기"],
            "총매출": total_sales(b),
            "평균": round(avg, 2),
            "등급": grade,
            "성과급률(%)": f"{grade_to_incentive(grade):.1f}%", # 가시성 개선
        })
    st.table(table)

# --- Tab 3 : 분기별 통계 ---
with tab3:
    st.header("분기별 통계")
    cols = st.columns(3)
    for i in range(len(QUARTERS)):
        quarter = QUARTERS[i]
        with cols[i]:
            st.subheader(quarter)
            # 안전하게 f-string 구조로 변경하여 문자열-숫자 연산 에러 원천 차단
            st.write(f"평균: {quarter_average(branches, quarter)}")
            st.write(f"최고: {quarter_top(branches, quarter)}")

    st.markdown("### 분기별 평균 매출 추이")
    chart_data = []
    for quarter in QUARTERS:
        # 데이터 유효성 확보를 위해 float 캐스팅 후 차트 삽입
        q_avg = quarter_average(branches, quarter)
        chart_data.append({"분기": quarter, "평균": float(q_avg)})
    
    # x축과 y축 맵핑이 올바르게 나타나도록 세로 막대그래프로 수정
    st.bar_chart(chart_data, x="분기", y="평균", height=400)

# --- Tab 4 : 순위 & 등급 분포 ---
with tab4:
    st.header("매출 순위")
    ranked = rank_list(branches)
    rank_table = []
    rank = 1
    for b in ranked:
        rank_table.append({"순위": rank, "지점": b["지점"], "총매출": total_sales(b)})
        rank = rank + 1
    st.table(rank_table)

    st.header("등급 분포")
    # 오타 수정: brnaches -> branches
    dist = grade_distribution(branches)
    dist_data = [{"등급": g, "지점수": dist[g]} for g in ["A", "B", "C", "D", "F"]]
    
    # 등급 분포 시각화가 꼬이지 않도록 세로 막대그래프로 안정화
    st.bar_chart(dist_data, x="등급", y="지점수", height=400)
