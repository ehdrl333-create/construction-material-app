import streamlit as st
import pandas as pd
import math
from io import BytesIO
from openpyxl.styles import Font, PatternFill

st.set_page_config(page_title="건축 자재 분석 프로그램", layout="wide")

st.title("🏗️ 건축 자재 분석 프로그램 (웹 버전)")

# ======================
# 입력 방식 선택
# ======================

st.header("입력 방식")

input_mode = st.radio(
    "입력 방식 선택",
    ["면적 입력", "치수 입력"],
    horizontal=True
)

# ======================
# 면적 입력 방식
# ======================

if input_mode == "면적 입력":

    wall_area = st.number_input(
        "총 벽 면적(㎡)",
        min_value=0.0,
        value=20.0
    )

    door_area = st.number_input(
        "문 면적(㎡)",
        min_value=0.0,
        value=0.0
    )

    window_area = st.number_input(
        "창문 면적(㎡)",
        min_value=0.0,
        value=0.0
    )

# ======================
# 치수 입력 방식
# ======================

else:

    wall_count = st.number_input(
        "벽 개수",
        min_value=1,
        value=1,
        step=1
    )

    door_count = st.number_input(
        "문 개수",
        min_value=0,
        value=0,
        step=1
    )

    window_count = st.number_input(
        "창문 개수",
        min_value=0,
        value=0,
        step=1
    )

    wall_area = 0
    door_area = 0
    window_area = 0

    st.subheader("벽 치수 입력")

    for i in range(int(wall_count)):

        col1, col2 = st.columns(2)

        with col1:
            width = st.number_input(
                f"벽{i+1} 가로(mm)",
                min_value=0.0,
                key=f"wall_w_{i}"
            )

        with col2:
            height = st.number_input(
                f"벽{i+1} 세로(mm)",
                min_value=0.0,
                key=f"wall_h_{i}"
            )

        wall_area += (width * height) / 1000000

    if door_count > 0:

        st.subheader("문 치수 입력")

        for i in range(int(door_count)):

            col1, col2 = st.columns(2)

            with col1:
                width = st.number_input(
                    f"문{i+1} 가로(mm)",
                    min_value=0.0,
                    key=f"door_w_{i}"
                )

            with col2:
                height = st.number_input(
                    f"문{i+1} 세로(mm)",
                    min_value=0.0,
                    key=f"door_h_{i}"
                )

            door_area += (width * height) / 1000000

    if window_count > 0:

        st.subheader("창문 치수 입력")

        for i in range(int(window_count)):

            col1, col2 = st.columns(2)

            with col1:
                width = st.number_input(
                    f"창문{i+1} 가로(mm)",
                    min_value=0.0,
                    key=f"window_w_{i}"
                )

            with col2:
                height = st.number_input(
                    f"창문{i+1} 세로(mm)",
                    min_value=0.0,
                    key=f"window_h_{i}"
                )

            window_area += (width * height) / 1000000

# ======================
# 실제 시공 면적
# ======================

net_area = wall_area - door_area - window_area

st.success(
    f"""
총 벽 면적 : {wall_area:.2f}㎡

문 면적 : {door_area:.2f}㎡

창문 면적 : {window_area:.2f}㎡

실제 시공 면적 : {net_area:.2f}㎡
"""
)

# ======================
# 자재 DB
# ======================

materials = {
    "일반 자재": {
        "carbon": 5,
        "sizes": ["900x1800", "1200x2400", "직접입력"]
    },
    "바닥 타일": {
        "carbon": 15,
        "sizes": ["300x300", "600x600", "800x800", "직접입력"]
    },
    "벽 타일": {
        "carbon": 12,
        "sizes": ["300x600", "600x1200", "직접입력"]
    },
    "단열재": {
        "carbon": 8,
        "sizes": ["900x1800", "900x2400", "1200x2400", "직접입력"]
    },
    "벽돌": {
        "carbon": 0.25,
        "sizes": ["0.5B", "1.0B", "1.5B"]
    },
    "페인트": {
        "carbon": 6,
        "sizes": ["자동 계산"]
    },
    "콘크리트": {
        "carbon": 350,
        "sizes": ["부피 계산"]
    },
    "몰탈": {
        "carbon": 120,
        "sizes": ["부피 계산"]
    }
}

company_list = [
    "A업체",
    "B업체",
    "C업체",
    "D업체"
]

# ======================
# 자재 추가
# ======================

st.header("자재 추가")

if "material_count" not in st.session_state:
    st.session_state.material_count = 1

if "deleted_items" not in st.session_state:
    st.session_state.deleted_items = []

col1, col2 = st.columns(2)

active_count = (
    st.session_state.material_count
    - len(st.session_state.deleted_items)
)

with col1:
    if st.button("➕ 자재 추가"):

        if active_count < 4:
            st.session_state.material_count += 1

        else:
            st.warning("최대 4개 자재까지만 비교 가능합니다.")

with col2:
    if st.button("초기화"):
        st.session_state.material_count = 1
        st.session_state.deleted_items = []
        st.rerun()

materials_result = []

for i in range(st.session_state.material_count):

    if i in st.session_state.deleted_items:
        continue

    col1, col2 = st.columns([5,1])

    with col1:
        st.subheader(f"자재 {i+1}")

    with col2:
        if st.button("🗑️", key=f"delete_{i}"):

            st.session_state.deleted_items.append(i)
            st.rerun()

    company = st.selectbox(
        "업체 선택",
        company_list,
        key=f"company_{i}"
    )

    material = st.selectbox(
        "자재 선택",
        list(materials.keys()),
        key=f"material_{i}"
    )

    size = st.selectbox(
        "규격 선택",
        materials[material]["sizes"],
        key=f"size_{i}"
    )

    custom_width = 0
    custom_height = 0

    if size == "직접입력":

        custom_width = st.number_input(
            "가로(mm)",
            min_value=1,
            value=600,
            key=f"custom_w_{i}"
        )

        custom_height = st.number_input(
            "세로(mm)",
            min_value=1,
            value=600,
            key=f"custom_h_{i}"
        )

    waste = st.number_input(
        "할증률 (%)",
        min_value=0.0,
        value=5.0,
        key=f"waste_{i}"
    )

    price = st.number_input(
        "단가(원)",
        min_value=0.0,
        value=1000.0,
        key=f"price_{i}"
    )

    paint_coat = 1

    if material == "페인트":

        paint_coat = st.number_input(
            "도장 횟수",
            min_value=1,
            value=2,
            step=1,
            key=f"coat_{i}"
        )

    thickness = 0

    if material in ["콘크리트", "몰탈"]:

        thickness = st.number_input(
            "두께(mm)",
            min_value=0.0,
            value=100.0,
            key=f"thickness_{i}"
        )

    materials_result.append({
        "company": company,
        "material": material,
        "size": size,
        "custom_width": custom_width if size == "직접입력" else 0,
        "custom_height": custom_height if size == "직접입력" else 0,
        "paint_coat": paint_coat,
        "thickness": thickness,
        "waste": waste,
        "price": price
    })

# ======================
# 계산
# ======================

if st.button("📊 계산하기"):

    results = []

    for item in materials_result:

        material = item["material"]

        size_area_map = {
            "300x300": 0.09,
            "300x600": 0.18,
            "600x600": 0.36,
            "600x1200": 0.72,
            "800x800": 0.64,
            "900x1800": 1.62,
            "900x2400": 2.16,
            "1200x2400": 2.88
        }

# ======================
# 벽돌
# ======================

        if material == "벽돌":

            brick_map = {
                "0.5B": 75,
                "1.0B": 149,
                "1.5B": 224
            }

            quantity = (
                net_area *
                brick_map[item["size"]]
            )

# ======================
# 페인트
# ======================

        elif material == "페인트":

            quantity = (
                net_area *
                item["paint_coat"]
            )

# ======================
# 콘크리트 / 몰탈
# ======================

        elif material in ["콘크리트", "몰탈"]:

            quantity = (
                net_area *
                (item["thickness"] / 1000)
            )

# ======================
# 일반 자재
# ======================

        else:

            if item["size"] == "직접입력":

                area_per_piece = (
                    item["custom_width"]
                    * item["custom_height"]
                ) / 1000000

                quantity = (
                    net_area /
                    area_per_piece
                )

            elif item["size"] in size_area_map:

                quantity = (
                    net_area /
                    size_area_map[item["size"]]
                )

            else:

                quantity = net_area

# ======================
# 할증률 적용
# ======================

        quantity = quantity * (
            1 + item["waste"] / 100
        )

        if material not in [
            "콘크리트",
            "몰탈"
        ]:
            quantity = math.ceil(quantity)

        total_price = quantity * item["price"]

        carbon = (
            quantity *
            materials[material]["carbon"]
        )

        results.append({
                "업체": item["company"],
                "자재": material,
                "규격": item["size"],
                "수량": round(quantity, 2),
                "단가": item["price"],
                "총비용": round(total_price, 0),
                "탄소배출량": round(carbon, 2)
            })

    df = pd.DataFrame(results)

    ranking_df = df.sort_values(
        by="총비용",
        ascending=True
    )

    best_row = ranking_df.iloc[0]

    st.subheader("계산 결과")

    st.dataframe(
        df,
        use_container_width=True
    )

    st.subheader("총 비용")

    st.metric(
        "합계",
        f"{df['총비용'].sum():,.0f} 원"
    )



# ======================
# 엑셀 다운로드
# ======================

    st.subheader("📊 업체별 비용 비교")

    chart_df = df.set_index("업체")

    st.bar_chart(
        chart_df["총비용"]
    )

    st.subheader("🏆 추천 자재")

    best_row = df.loc[df["총비용"].idxmin()]

    st.success(
        f"""
    추천 업체 : {best_row['업체']}

    추천 자재 : {best_row['자재']}

    총비용 : {best_row['총비용']:,.0f} 원

    탄소배출량 : {best_row['탄소배출량']:,.2f}
    """
    )

    ranking_df = df.sort_values(
        by="총비용",
        ascending=True
    )

    st.subheader("🏆 업체 순위")

    for idx, row in enumerate(
        ranking_df.itertuples(),
        start=1
    ):

        st.write(
            f"{idx}위 | {row.업체} | {row.자재} | {row.총비용:,.0f}원"
        )

    best_row = ranking_df.iloc[0]

    st.success(
        f"""
    🏆 추천 업체 : {best_row['업체']}

    추천 자재 : {best_row['자재']}

    총비용 : {best_row['총비용']:,.0f}원
    """
    )

    cost_diff = (
        ranking_df.iloc[1]["총비용"]
        - ranking_df.iloc[0]["총비용"]
    )

    st.info(
        f"""
    💰 비용 절감 효과

    1위 업체 선택 시

    약 {cost_diff:,.0f}원 절감 가능합니다.
    """
    )

    carbon_best = df.loc[
        df["탄소배출량"].idxmin()
    ]

    st.success(
        f"""
    🌱 친환경 추천

    업체 : {carbon_best['업체']}

    자재 : {carbon_best['자재']}

    탄소배출량 : {carbon_best['탄소배출량']:,.2f}
    """
    )
