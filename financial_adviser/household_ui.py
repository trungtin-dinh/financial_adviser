"""Straightforward localized household life-cycle editor for Streamlit.

Interface-only module: the financial model is in households.py and engine.py.
"""
from __future__ import annotations

from dataclasses import asdict, replace

import streamlit as st

from .households import AdultBudget, ChildBudget, CHILD_AGE_BANDS, ADULT_AGE_BANDS, child_example

_COPY = {
"fr": {
"title": "Composition du foyer et dépenses selon l'âge", "intro": "Planifiez les changements de coût des enfants et les revenus/dépenses des adultes. Ces profils sont facultatifs, entièrement modifiables et distincts des événements ponctuels.",
"child_title": "Enfants et personnes à charge", "adult_title": "Adultes, âge et retraite", "add_child": "Ajouter un enfant", "add_adult": "Ajouter un adulte", "remove": "Supprimer", "empty_children": "Aucun enfant suivi par âge.", "empty_adults": "Aucun adulte suivi par âge.",
"example_warning": "Les montants initiaux proposés sont de simples EXEMPLES proportionnels à votre budget, non des médianes officielles ni une estimation des besoins de l'enfant.",
"child_name": "Nom ou repère", "adult_name": "Nom ou repère", "child_label": "Enfant {n}", "adult_label": "Adulte {n}",
"child_age": "Âge (années) au début de la prise en charge", "arrival_year": "Début de prise en charge : année", "arrival_month": "Mois", "end_age": "Âge de fin de prise en charge (exclusif)",
"existing": "Ces coûts sont-ils DÉJÀ compris dans les dépenses mensuelles principales ?", "existing_hint": "Oui : on ajoute seulement la différence par rapport aux dépenses actuelles, puis on retire leur part quand le soutien s'arrête. Non : on ajoute le montant complet. Choisissez Oui pour un enfant déjà inclus dans votre budget actuel.",
"existing_future": "Pour un enfant attendu dans le futur, ces dépenses ne sont pas encore dans le budget courant : le modèle ajoutera tous les coûts à son arrivée.",
"living": "Vie quotidienne : alimentation, vêtements, transport, logement supplémentaire, santé courante", "care": "Garde, éducation, activités et études", "age_band": "Âges {start}–{end} ans", "monthly": "Montants mensuels à la date de départ, dans la devise du scénario", "end_note": "À partir de l'âge de fin de soutien, les dépenses additionnelles cessent. Si elles figuraient déjà dans le budget de base, leur part en est retirée.",
"adult_age": "Âge actuel (années)", "income_share": "Part du revenu net actuel du foyer attribuée à cet adulte (%)", "retirement_age": "Âge hypothétique de départ à la retraite", "replacement": "Pension nette hypothétique (% du dernier revenu net de cet adulte)", "retirement_spending": "Changement mensuel de dépenses à la retraite (+ ou −)", "adult_stage": "Dépenses mensuelles associées à l'âge {start}–{end} ans", "adult_baseline": "Les dépenses de cette tranche d'âge sont déjà dans les dépenses principales", "share_warning": "La somme des parts de revenu des adultes dépasse 100 %. Réduisez certaines parts avant de lancer la projection.", "baseline_over": "Les montants déclarés comme déjà inclus dépassent les dépenses mensuelles principales. Corrigez le budget ou les montants avant de calculer.", "retired_note": "Si l'adulte est déjà retraité, le revenu actuel est considéré comme comprenant sa pension. Le taux de remplacement n'est pas réappliqué.",
"adult_note": "Le taux de remplacement est une hypothèse de scénario, PAS une pension prédite. Les dépenses de santé, la dépendance et les droits à pension ne sont pas calculés automatiquement.",
"nophases": "Sans profil ajouté, les revenus et les dépenses continuent selon les hypothèses générales du scénario.", "overlap_note": "Attention : n'ajoutez pas aussi les mêmes frais de garde, santé ou aides familiales sous forme d'événements de vie.",
},
"en": {
"title": "Household members and age-related expenses", "intro": "Model how children's costs and adults' income and expenses change over time. Profiles are optional, fully editable, and separate from one-off events.",
"child_title": "Children and dependents", "adult_title": "Adults, age and retirement", "add_child": "Add a child", "add_adult": "Add an adult", "remove": "Remove", "empty_children": "No age-based child profiles.", "empty_adults": "No age-based adult profiles.",
"example_warning": "Suggested initial amounts are ILLUSTRATIVE fractions of your budget, NOT official medians or estimates of actual child needs.",
"child_name": "Name or label", "adult_name": "Name or label", "child_label": "Child {n}", "adult_label": "Adult {n}",
"child_age": "Age (years) when support begins", "arrival_year": "Start of support: year", "arrival_month": "Month", "end_age": "Age when financial support stops (exclusive)",
"existing": "Are these costs ALREADY included in the main monthly spending?", "existing_hint": "Yes: only future changes from today's cost are added; that cost is removed when support ends. No: full costs are added. Choose Yes if your existing child is already included in your current budget.",
"existing_future": "For a future child, these costs are not yet in your baseline budget: full costs begin upon arrival.",
"living": "Everyday living: food, clothes, transport, extra housing, routine healthcare", "care": "Childcare, education, activities and further studies", "age_band": "Age {start}–{end}", "monthly": "Monthly amounts in scenario currency at the projection start", "end_note": "Additional costs stop at the chosen age. If they were already in your base budget, the corresponding baseline amount is then removed.",
"adult_age": "Current age (years)", "income_share": "Share of current household net income earned by this adult (%)", "retirement_age": "Assumed retirement age", "replacement": "Assumed net pension (% of this adult's final net working income)", "retirement_spending": "Monthly spending change upon retirement (+ or −)", "adult_stage": "Age-related monthly spending at {start}–{end}", "adult_baseline": "Current age-band spending already included in main monthly expenses", "share_warning": "Adults' income shares exceed 100%. Reduce the shares before projecting.", "baseline_over": "Amounts marked as already included exceed your total monthly spending. Adjust the base budget or those amounts before projecting.", "retired_note": "For someone already retired, current net income is treated as including their pension. The replacement rate is not applied again.",
"adult_note": "The replacement rate is a hypothetical scenario, NOT an entitlement forecast. Pension law, healthcare and long-term care are not computed automatically.",
"nophases": "Without household profiles, income and spending follow the general plan assumptions.", "overlap_note": "Avoid adding the same childcare, healthcare or family support costs again as life events.",
},
"vi": {
"title": "Thành viên gia đình và chi tiêu theo độ tuổi", "intro": "Mô phỏng chi phí nuôi con và thu nhập, chi tiêu của người lớn theo thời gian. Các hồ sơ là tùy chọn, có thể chỉnh sửa, khác với sự kiện phát sinh một lần.",
"child_title": "Con và người phụ thuộc", "adult_title": "Người lớn, tuổi và hưu trí", "add_child": "Thêm một người con", "add_adult": "Thêm người lớn", "remove": "Xóa", "empty_children": "Chưa có hồ sơ chi phí theo tuổi của con.", "empty_adults": "Chưa có hồ sơ người lớn theo tuổi.",
"example_warning": "Các khoản đề xuất chỉ là VÍ DỤ giả định theo tỷ lệ ngân sách của bạn, KHÔNG phải số trung vị chính thức hay dự báo chi phí nuôi con.",
"child_name": "Tên hoặc nhãn", "adult_name": "Tên hoặc nhãn", "child_label": "Con {n}", "adult_label": "Người lớn {n}",
"child_age": "Tuổi (năm) khi bắt đầu chu cấp", "arrival_year": "Bắt đầu chu cấp: năm", "arrival_month": "Tháng", "end_age": "Tuổi kết thúc chu cấp (không bao gồm tuổi này)",
"existing": "Các chi phí này ĐÃ có trong tổng chi tiêu hằng tháng chưa?", "existing_hint": "Có: chỉ tính phần thay đổi so với chi phí hiện tại; phần chi ban đầu được trừ khi kết thúc chu cấp. Chưa: thêm toàn bộ chi phí. Chọn Có nếu chi phí cho con đã nằm trong ngân sách hiện tại.",
"existing_future": "Với trẻ dự kiến sinh trong tương lai, chi phí chưa có trong ngân sách hiện tại: sẽ cộng toàn bộ từ lúc bắt đầu chu cấp.",
"living": "Sinh hoạt: ăn uống, quần áo, đi lại, nhà ở phát sinh, chăm sóc sức khỏe thường ngày", "care": "Trông trẻ, giáo dục, hoạt động và học lên cao", "age_band": "Tuổi {start}–{end}", "monthly": "Số tiền hằng tháng theo đơn vị tiền của kế hoạch tại thời điểm bắt đầu dự phóng", "end_note": "Chi phí bổ sung kết thúc ở độ tuổi được chọn. Nếu đã nằm trong ngân sách gốc, phần tương ứng sẽ được trừ khỏi ngân sách khi kết thúc chu cấp.",
"adult_age": "Tuổi hiện tại (năm)", "income_share": "Tỷ trọng thu nhập ròng hiện tại của hộ thuộc người này (%)", "retirement_age": "Tuổi nghỉ hưu giả định", "replacement": "Lương hưu ròng giả định (% thu nhập ròng cuối cùng từ công việc)", "retirement_spending": "Mức thay đổi chi tiêu hằng tháng khi nghỉ hưu (+ hoặc −)", "adult_stage": "Chi tiêu hằng tháng theo tuổi {start}–{end}", "adult_baseline": "Chi phí theo nhóm tuổi hiện tại đã tính trong tổng chi tiêu", "share_warning": "Tổng tỷ trọng thu nhập của người lớn vượt 100%. Hãy điều chỉnh trước khi tính.", "baseline_over": "Các khoản đánh dấu đã tính trong chi tiêu lớn hơn tổng chi tiêu hằng tháng. Hãy điều chỉnh trước khi dự phóng.", "retired_note": "Nếu đã nghỉ hưu, thu nhập hiện tại được xem là đã bao gồm lương hưu. Không áp dụng tỷ lệ thay thế lần nữa.",
"adult_note": "Tỷ lệ thay thế chỉ là giả định, KHÔNG phải quyền lợi hưu trí dự báo. Mô hình chưa tự tính luật hưu trí, y tế hay chăm sóc dài hạn.",
"nophases": "Nếu không thêm hồ sơ gia đình, thu nhập và chi tiêu tuân theo giả định chung.", "overlap_note": "Tránh cộng trùng chi phí trông trẻ, y tế hoặc hỗ trợ người thân trong mục sự kiện cuộc sống.",
}}


def _h(lang: str, key: str, **kwargs: object) -> str:
    return _COPY[lang][key].format(**kwargs)


def _initial(plan) -> None:
    if "household_children" not in st.session_state:
        st.session_state.household_children = [dict(asdict(c), id=i + 1) for i, c in enumerate(plan.children)]
        st.session_state.household_child_id = len(plan.children) + 1
    if "household_adults" not in st.session_state:
        st.session_state.household_adults = [dict(asdict(a), id=i + 1) for i, a in enumerate(plan.adults)]
        st.session_state.household_adult_id = len(plan.adults) + 1


def render_household(plan, years: int, start_year: int, monthly_expenses: float, language: str, step: float):
    """Draw editable household profiles and return immutable typed schedules."""
    _initial(plan)
    with st.container(border=True):
        st.subheader(_h(language, "title"))
        st.caption(_h(language, "intro"))
        st.warning(_h(language, "overlap_note"))
        st.markdown("**" + _h(language, "child_title") + "**")
        if st.button("＋ " + _h(language, "add_child"), key="household_add_child", width="stretch"):
            if len(st.session_state.household_children) < 12:
                cid = st.session_state.household_child_id
                st.session_state.household_child_id += 1
                profile = replace(child_example(monthly_expenses, _h(language, "child_label", n=cid)),
                    included_in_baseline=True)
                st.session_state.household_children.append(dict(asdict(profile), id=cid))
        if st.session_state.household_children:
            st.caption(_h(language, "example_warning"))
        else:
            st.caption(_h(language, "empty_children"))
        for index, draft in enumerate(st.session_state.household_children, start=1):
            cid = draft["id"]
            key = f"child_{cid}_"
            with st.container(border=True):
                a, b = st.columns([4, 1], wrap=True)
                a.markdown("**" + _h(language, "child_label", n=index) + "**")
                if b.button(_h(language, "remove"), key=key + "remove", width="stretch"):
                    st.session_state.household_children = [x for x in st.session_state.household_children if x["id"] != cid]
                    for old_key in list(st.session_state):
                        if old_key.startswith(key):
                            del st.session_state[old_key]
                    st.rerun()
                label = st.text_input(_h(language, "child_name"), value=draft["label"], key=key + "label")
                a, b = st.columns(2, wrap=True)
                with a:
                    age = int(st.number_input(_h(language, "child_age"), 0, 29, int(draft["age_years"]),
                                              key=key + "age"))
                    support = int(st.number_input(_h(language, "end_age"), min_value=age + 1,
                        max_value=30, value=max(age + 1, int(draft["support_until_age"])), key=key + "support"))
                with b:
                    original_month = int(draft["arrival_month"])
                    arrival_year = int(st.number_input(_h(language, "arrival_year"), start_year,
                        start_year + years - 1, min(start_year + (original_month - 1)//12, start_year + years - 1),
                        key=key + "year"))
                    month = st.selectbox(_h(language, "arrival_month"), list(range(1, 13)),
                        index=(original_month - 1)%12, key=key + "month")
                arrival_month = (arrival_year - start_year) * 12 + int(month)
                if arrival_month == 1:
                    included = st.checkbox(_h(language, "existing"), value=bool(draft["included_in_baseline"]),
                        help=_h(language, "existing_hint"), key=key + "included")
                else:
                    included = False
                    st.caption(_h(language, "existing_future"))
                st.caption(_h(language, "monthly"))
                living, care = [], []
                for j, (start, end) in enumerate(CHILD_AGE_BANDS):
                    st.markdown("*" + _h(language, "age_band", start=start, end=end - 1) + "*")
                    a, b = st.columns(2, wrap=True)
                    with a:
                        living.append(float(st.number_input(_h(language, "living"), min_value=0.,
                            value=float(draft["living"][j]), step=step, key=key+f"living_{j}")))
                    with b:
                        care.append(float(st.number_input(_h(language, "care"), min_value=0.,
                            value=float(draft["care_education"][j]), step=step, key=key+f"care_{j}")))
                draft.update(label=label, age_years=age, arrival_month=arrival_month,
                    support_until_age=support, included_in_baseline=included,
                    living=tuple(living), care_education=tuple(care))
                st.caption(_h(language, "end_note"))
        st.divider()
        st.markdown("**" + _h(language, "adult_title") + "**")
        if st.button("＋ " + _h(language, "add_adult"), key="household_add_adult", width="stretch"):
            if len(st.session_state.household_adults) < 8:
                aid = st.session_state.household_adult_id
                st.session_state.household_adult_id += 1
                remaining = max(0., 100. - sum(a["income_share_pct"] for a in st.session_state.household_adults))
                st.session_state.household_adults.append(dict(asdict(AdultBudget(
                    label=_h(language, "adult_label", n=aid), income_share_pct=remaining)), id=aid))
        if not st.session_state.household_adults:
            st.caption(_h(language, "empty_adults"))
        else:
            st.caption(_h(language, "adult_note"))
        for index, draft in enumerate(st.session_state.household_adults, start=1):
            aid = draft["id"]
            key = f"adult_{aid}_"
            with st.container(border=True):
                a, b = st.columns([4, 1], wrap=True)
                a.markdown("**" + _h(language, "adult_label", n=index) + "**")
                if b.button(_h(language, "remove"), key=key+"remove", width="stretch"):
                    st.session_state.household_adults = [x for x in st.session_state.household_adults if x["id"] != aid]
                    for old_key in list(st.session_state):
                        if old_key.startswith(key):
                            del st.session_state[old_key]
                    st.rerun()
                label = st.text_input(_h(language, "adult_name"), value=draft["label"], key=key+"label")
                a, b = st.columns(2, wrap=True)
                with a:
                    age = int(st.number_input(_h(language, "adult_age"), min_value=18, max_value=120,
                        value=int(draft["age_years"]), key=key + "age"))
                    retirement_age = int(st.number_input(_h(language, "retirement_age"), min_value=18,
                        max_value=100, value=int(draft["retirement_age"]), key=key+"retirement"))
                with b:
                    income_share = float(st.number_input(_h(language, "income_share"), min_value=0.,
                        max_value=100., value=float(draft["income_share_pct"]), step=5., key=key+"share"))
                    replace_pct = float(st.number_input(_h(language, "replacement"), min_value=0.,
                        max_value=200., value=float(draft["retirement_replacement_pct"]), step=5.,
                        key=key+"replace"))
                if age >= retirement_age:
                    st.info(_h(language, "retired_note"))
                change = float(st.number_input(_h(language, "retirement_spending"),
                    value=float(draft["retirement_expense_change"]), step=step,
                    key=key+"retirement_spending"))
                already_included = st.checkbox(_h(language, "adult_baseline"),
                    value=bool(draft["included_in_baseline"]), key=key + "included")
                st.caption(_h(language, "monthly"))
                cost = []
                for j, (start, end) in enumerate(ADULT_AGE_BANDS):
                    cost.append(float(st.number_input(_h(language,"adult_stage",start=start,end=end-1),
                        min_value=0., value=float(draft["expenses_by_age"][j]), step=step,
                        key=key+f"stage_{j}")))
                draft.update(label=label, age_years=age, retirement_age=retirement_age,
                    income_share_pct=income_share, retirement_replacement_pct=replace_pct,
                    retirement_expense_change=change, expenses_by_age=tuple(cost),
                    included_in_baseline=already_included)
        if sum(d["income_share_pct"] for d in st.session_state.household_adults) > 100.:
            st.error(_h(language, "share_warning"))
        already_included = 0.0
        for draft in st.session_state.household_children:
            if draft["included_in_baseline"]:
                band = next(j for j, (first, last) in enumerate(CHILD_AGE_BANDS)
                    if first <= draft["age_years"] < last)
                already_included += draft["living"][band] + draft["care_education"][band]
        for draft in st.session_state.household_adults:
            if draft["included_in_baseline"]:
                band = next(j for j, (first, last) in enumerate(ADULT_AGE_BANDS)
                    if first <= draft["age_years"] < last)
                already_included += draft["expenses_by_age"][band]
        if already_included > monthly_expenses + 1e-7:
            st.error(_h(language, "baseline_over"))
        if not st.session_state.household_children and not st.session_state.household_adults:
            st.caption(_h(language, "nophases"))
    children = tuple(ChildBudget(**{k:v for k,v in child.items() if k != "id"})
        for child in st.session_state.household_children)
    adults = tuple(AdultBudget(**{k:v for k,v in adult.items() if k != "id"})
        for adult in st.session_state.household_adults)
    return children, adults
