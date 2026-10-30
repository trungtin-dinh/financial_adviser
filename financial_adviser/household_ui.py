"""Straightforward localized household life-cycle editor for Streamlit.

Interface-only module: the financial model is in households.py and engine.py.
"""
from __future__ import annotations

from dataclasses import asdict, replace

import streamlit as st

from .households import (AdultBudget, ChildBudget, DependentBudget,
                         CHILD_AGE_BANDS, ADULT_AGE_BANDS, DEPENDENT_RELATIONS, child_example)

_COPY = {
"fr": {
"title": "Composition du foyer et dépenses selon l'âge", "intro": "Planifiez les changements de coût des enfants et les revenus/dépenses des adultes. Ces profils sont facultatifs, entièrement modifiables et distincts des événements ponctuels.",
"child_title": "Enfants", "dependent_title": "Autres personnes à charge", "add_dependent": "Ajouter une personne à charge", "dependent_empty": "Aucun autre proche à charge.", "dependent_label": "Proche {n}", "dependent_relation": "Lien", "dependent_parent": "Parent âgé", "dependent_adult_relative": "Adulte dépendant / autre membre de la famille", "dependent_partner": "Conjoint ou partenaire à charge", "dependent_other": "Autre proche", "dependent_start": "Année de début", "dependent_month": "Mois", "dependent_duration": "Durée (mois)", "dependent_support": "Soutien mensuel", "dependent_care": "Soins / accompagnement mensuels", "dependent_included": "Déjà inclus dans les dépenses actuelles", "dependent_hint": "Hypothèses de dépenses déclarées : aucune dépendance médicale ni prestation publique n’est prédite.", "dependent_cost": "Dépense mensuelle : {value}", "dependent_summary": "{relation} · dès {year}-{month:02d} · {duration} mois", "card_remove_help": "Supprimer cette fiche", "child_details": "Enfant {n} · Modifier / réduire les détails", "adult_details": "Adulte {n} · Modifier / réduire les détails", "adult_title": "Adultes, âge et retraite", "add_child": "Ajouter un enfant", "add_adult": "Ajouter un adulte", "remove": "Supprimer", "empty_children": "Aucun enfant suivi par âge.", "empty_adults": "Aucun adulte suivi par âge.",
"example_warning": "Les montants initiaux proposés sont de simples EXEMPLES proportionnels à votre budget, non des médianes officielles ni une estimation des besoins de l'enfant.",
"child_name": "Nom ou repère", "adult_name": "Nom ou repère", "child_label": "Enfant {n}", "adult_label": "Adulte {n}",
"child_age": "Âge au début", "child_age_help": "Âge de l’enfant au premier mois de prise en charge.", "arrival_year": "Année de début", "arrival_month": "Mois de début", "end_age": "Âge de fin", "end_age_help": "Âge auquel le soutien financier prend fin (exclusif).", "child_summary": "Début : {age} ans · {year}-{month:02d} · Soutien jusqu’à {end} ans", "adult_summary": "{age} ans · Revenu du foyer : {share:g} % · Retraite : {retire} ans",
"existing": "Ces coûts sont-ils DÉJÀ compris dans les dépenses mensuelles principales ?", "existing_hint": "Oui : on ajoute seulement la différence par rapport aux dépenses actuelles, puis on retire leur part quand le soutien s'arrête. Non : on ajoute le montant complet. Choisissez Oui pour un enfant déjà inclus dans votre budget actuel.",
"existing_future": "Pour un enfant attendu dans le futur, ces dépenses ne sont pas encore dans le budget courant : le modèle ajoutera tous les coûts à son arrivée.",
"living": "Vie quotidienne", "living_help": "Alimentation, vêtements, transport, logement supplémentaire et santé courante.", "care": "Garde et études", "care_help": "Garde, éducation, activités, études et formation.", "age_band": "Âges {start}–{end} ans", "monthly": "Montants mensuels à la date de départ, dans la devise du scénario", "end_note": "À partir de l'âge de fin de soutien, les dépenses additionnelles cessent. Si elles figuraient déjà dans le budget de base, leur part en est retirée.", "horizon_short": "La projection se termine avant la fin du soutien. Augmentez la durée du scénario pour calculer toutes les années de prise en charge.",
"adult_age": "Âge actuel", "income_share": "Part du revenu (%)", "income_share_help": "Part du revenu net actuel du foyer attribuée à cet adulte. La somme des parts ne peut pas dépasser 100 %.", "retirement_age": "Âge retraite", "retirement_age_help": "Âge hypothétique de départ à la retraite.", "replacement": "Pension hypothétique (%)", "replacement_help": "Pension nette hypothétique en pourcentage du dernier revenu net de cet adulte. Ce n’est pas une prévision de droits.", "retirement_spending": "Changement mensuel de dépenses à la retraite (+ ou −)", "adult_stage": "Dépenses mensuelles associées à l'âge {start}–{end} ans", "adult_baseline": "Les dépenses de cette tranche d'âge sont déjà dans les dépenses principales", "share_warning": "La somme des parts de revenu des adultes dépasse 100 %. Réduisez certaines parts avant de lancer la projection.", "baseline_over": "Les montants déclarés comme déjà inclus dépassent les dépenses mensuelles principales. Corrigez le budget ou les montants avant de calculer.", "retired_note": "Si l'adulte est déjà retraité, le revenu actuel est considéré comme comprenant sa pension. Le taux de remplacement n'est pas réappliqué.",
"adult_note": "Le taux de remplacement est une hypothèse de scénario, PAS une pension prédite. Les dépenses de santé, la dépendance et les droits à pension ne sont pas calculés automatiquement.",
"nophases": "Sans profil ajouté, les revenus et les dépenses continuent selon les hypothèses générales du scénario.", "overlap_note": "Attention : n'ajoutez pas aussi les mêmes frais de garde, santé ou aides familiales sous forme d'événements de vie.",
},
"en": {
"title": "Household members and age-related expenses", "intro": "Model how children's costs and adults' income and expenses change over time. Profiles are optional, fully editable, and separate from one-off events.",
"child_title": "Children", "dependent_title": "Other dependents", "add_dependent": "Add another dependent", "dependent_empty": "No other dependents.", "dependent_label": "Dependent {n}", "dependent_relation": "Relationship", "dependent_parent": "Older parent", "dependent_adult_relative": "Dependent adult / another family member", "dependent_partner": "Dependent partner", "dependent_other": "Other relative", "dependent_start": "Start year", "dependent_month": "Month", "dependent_duration": "Duration (months)", "dependent_support": "Monthly support", "dependent_care": "Monthly care costs", "dependent_included": "Already included in current monthly expenses", "dependent_hint": "User-entered cost assumptions; no medical outcome or public benefits are predicted.", "dependent_cost": "Monthly cost: {value}", "dependent_summary": "{relation} · from {year}-{month:02d} · {duration} months", "card_remove_help": "Remove this card", "child_details": "Child {n} · Edit / collapse details", "adult_details": "Adult {n} · Edit / collapse details", "adult_title": "Adults, age and retirement", "add_child": "Add a child", "add_adult": "Add an adult", "remove": "Remove", "empty_children": "No age-based child profiles.", "empty_adults": "No age-based adult profiles.",
"example_warning": "Suggested initial amounts are ILLUSTRATIVE fractions of your budget, NOT official medians or estimates of actual child needs.",
"child_name": "Name or label", "adult_name": "Name or label", "child_label": "Child {n}", "adult_label": "Adult {n}",
"child_age": "Age at start", "child_age_help": "Age at the first month of support.", "arrival_year": "Start year", "arrival_month": "Start month", "end_age": "Support ends at age", "end_age_help": "Exclusive end age of support.", "child_summary": "Starts age {age} · {year}-{month:02d} · Support to age {end}", "adult_summary": "Age {age} · Household income: {share:g}% · Retirement age {retire}",
"existing": "Are these costs ALREADY included in the main monthly spending?", "existing_hint": "Yes: only future changes from today's cost are added; that cost is removed when support ends. No: full costs are added. Choose Yes if your existing child is already included in your current budget.",
"existing_future": "For a future child, these costs are not yet in your baseline budget: full costs begin upon arrival.",
"living": "Everyday living", "living_help": "Food, clothes, transport, extra housing and routine healthcare.", "care": "Childcare and studies", "care_help": "Childcare, education, activities and further studies.", "age_band": "Age {start}–{end}", "monthly": "Monthly amounts in scenario currency at the projection start", "end_note": "Additional costs stop at the chosen age. If they were already in your base budget, the corresponding baseline amount is then removed.", "horizon_short": "The projection ends before financial support does. Extend the scenario horizon to include every year of support.",
"adult_age": "Current age", "income_share": "Income share (%)", "income_share_help": "Share of the household current net income earned by this adult; combined shares cannot exceed 100%.", "retirement_age": "Retirement age", "retirement_age_help": "Hypothetical retirement age.", "replacement": "Assumed pension (%)", "replacement_help": "Hypothetical net pension as a percentage of this adult’s last working income; not an entitlement estimate.", "retirement_spending": "Monthly spending change upon retirement (+ or −)", "adult_stage": "Age-related monthly spending at {start}–{end}", "adult_baseline": "Current age-band spending already included in main monthly expenses", "share_warning": "Adults' income shares exceed 100%. Reduce the shares before projecting.", "baseline_over": "Amounts marked as already included exceed your total monthly spending. Adjust the base budget or those amounts before projecting.", "retired_note": "For someone already retired, current net income is treated as including their pension. The replacement rate is not applied again.",
"adult_note": "The replacement rate is a hypothetical scenario, NOT an entitlement forecast. Pension law, healthcare and long-term care are not computed automatically.",
"nophases": "Without household profiles, income and spending follow the general plan assumptions.", "overlap_note": "Avoid adding the same childcare, healthcare or family support costs again as life events.",
},
"vi": {
"title": "Thành viên gia đình và chi tiêu theo độ tuổi", "intro": "Mô phỏng chi phí nuôi con và thu nhập, chi tiêu của người lớn theo thời gian. Các hồ sơ là tùy chọn, có thể chỉnh sửa, khác với sự kiện phát sinh một lần.",
"child_title": "Con cái", "dependent_title": "Người phụ thuộc khác", "add_dependent": "Thêm người phụ thuộc", "dependent_empty": "Chưa có người phụ thuộc khác.", "dependent_label": "Người phụ thuộc {n}", "dependent_relation": "Quan hệ", "dependent_parent": "Cha mẹ lớn tuổi", "dependent_adult_relative": "Người lớn phụ thuộc / thân nhân khác", "dependent_partner": "Vợ/chồng hoặc bạn đời phụ thuộc", "dependent_other": "Người thân khác", "dependent_start": "Năm bắt đầu", "dependent_month": "Tháng", "dependent_duration": "Thời gian (tháng)", "dependent_support": "Trợ cấp hàng tháng", "dependent_care": "Chi phí chăm sóc hàng tháng", "dependent_included": "Đã có trong chi tiêu hiện tại", "dependent_hint": "Chi phí do người dùng nhập; không dự báo tình trạng y tế hay trợ cấp nhà nước.", "dependent_cost": "Chi phí mỗi tháng: {value}", "dependent_summary": "{relation} · từ {year}-{month:02d} · {duration} tháng", "card_remove_help": "Xóa thẻ này", "child_details": "Con {n} · Sửa / thu gọn chi tiết", "adult_details": "Người lớn {n} · Sửa / thu gọn chi tiết", "adult_title": "Người lớn, tuổi và hưu trí", "add_child": "Thêm một người con", "add_adult": "Thêm người lớn", "remove": "Xóa", "empty_children": "Chưa có hồ sơ chi phí theo tuổi của con.", "empty_adults": "Chưa có hồ sơ người lớn theo tuổi.",
"example_warning": "Các khoản đề xuất chỉ là VÍ DỤ giả định theo tỷ lệ ngân sách của bạn, KHÔNG phải số trung vị chính thức hay dự báo chi phí nuôi con.",
"child_name": "Tên hoặc nhãn", "adult_name": "Tên hoặc nhãn", "child_label": "Con {n}", "adult_label": "Người lớn {n}",
"child_age": "Tuổi lúc bắt đầu", "child_age_help": "Tuổi tại tháng đầu tiên bắt đầu chu cấp.", "arrival_year": "Năm bắt đầu", "arrival_month": "Tháng bắt đầu", "end_age": "Tuổi ngừng chu cấp", "end_age_help": "Không bao gồm tuổi kết thúc chu cấp.", "child_summary": "Bắt đầu {age} tuổi · {year}-{month:02d} · Chu cấp đến {end} tuổi", "adult_summary": "{age} tuổi · Thu nhập hộ: {share:g}% · Nghỉ hưu {retire} tuổi",
"existing": "Các chi phí này ĐÃ có trong tổng chi tiêu hằng tháng chưa?", "existing_hint": "Có: chỉ tính phần thay đổi so với chi phí hiện tại; phần chi ban đầu được trừ khi kết thúc chu cấp. Chưa: thêm toàn bộ chi phí. Chọn Có nếu chi phí cho con đã nằm trong ngân sách hiện tại.",
"existing_future": "Với trẻ dự kiến sinh trong tương lai, chi phí chưa có trong ngân sách hiện tại: sẽ cộng toàn bộ từ lúc bắt đầu chu cấp.",
"living": "Sinh hoạt", "living_help": "Ăn uống, quần áo, đi lại, nhà ở và chăm sóc sức khỏe thường ngày.", "care": "Chăm sóc và học tập", "care_help": "Trông trẻ, giáo dục, hoạt động và học lên cao.", "age_band": "Tuổi {start}–{end}", "monthly": "Số tiền hằng tháng theo đơn vị tiền của kế hoạch tại thời điểm bắt đầu dự phóng", "end_note": "Chi phí bổ sung kết thúc ở độ tuổi được chọn. Nếu đã nằm trong ngân sách gốc, phần tương ứng sẽ được trừ khỏi ngân sách khi kết thúc chu cấp.", "horizon_short": "Thời gian dự phóng kết thúc trước khi hết thời gian chu cấp. Hãy kéo dài kỳ dự phóng để tính tất cả các năm hỗ trợ.",
"adult_age": "Tuổi hiện tại", "income_share": "Tỷ trọng thu nhập (%)", "income_share_help": "Tỷ trọng thu nhập ròng hiện tại của hộ thuộc người này. Tổng các tỷ trọng không được vượt quá 100%.", "retirement_age": "Tuổi nghỉ hưu", "retirement_age_help": "Tuổi nghỉ hưu giả định.", "replacement": "Lương hưu giả định (%)", "replacement_help": "Lương hưu ròng giả định tính theo phần trăm thu nhập ròng cuối cùng từ công việc; không phải quyền lợi được dự báo.", "retirement_spending": "Mức thay đổi chi tiêu hằng tháng khi nghỉ hưu (+ hoặc −)", "adult_stage": "Chi tiêu hằng tháng theo tuổi {start}–{end}", "adult_baseline": "Chi phí theo nhóm tuổi hiện tại đã tính trong tổng chi tiêu", "share_warning": "Tổng tỷ trọng thu nhập của người lớn vượt 100%. Hãy điều chỉnh trước khi tính.", "baseline_over": "Các khoản đánh dấu đã tính trong chi tiêu lớn hơn tổng chi tiêu hằng tháng. Hãy điều chỉnh trước khi dự phóng.", "retired_note": "Nếu đã nghỉ hưu, thu nhập hiện tại được xem là đã bao gồm lương hưu. Không áp dụng tỷ lệ thay thế lần nữa.",
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
    if "household_dependents" not in st.session_state:
        st.session_state.household_dependents = [
            dict(asdict(person), id=i + 1) for i, person in enumerate(plan.dependents)]
        st.session_state.household_dependent_id = len(plan.dependents) + 1


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
                st.rerun()
        if st.session_state.household_children:
            st.caption(_h(language, "example_warning"))
        else:
            st.caption(_h(language, "empty_children"))
        for index, draft in enumerate(st.session_state.household_children, start=1):
            cid = draft["id"]
            key = f"child_{cid}_"
            arrival = int(draft["arrival_month"])
            child_summary = _h(language, "child_summary", age=draft["age_years"],
                year=start_year + (arrival - 1) // 12, month=(arrival - 1) % 12 + 1,
                end=draft["support_until_age"])
            child_name = str(draft["label"]).strip() or _h(language, "child_label", n=index)
            open_key = key + "open"
            with st.container(border=True):
                is_open = st.session_state.get(open_key, False)
                head, delete = st.columns([8, 2], vertical_alignment="center", gap="small", wrap=False)
                if head.button(f"{'▾' if is_open else '▸'} 👶 {child_name} · {child_summary}",
                               key=key + "toggle", width="stretch", type="tertiary"):
                    st.session_state[open_key] = not is_open
                    st.rerun()
                if delete.button("✕", key=key + "remove",
                                 help=_h(language, "card_remove_help"), width="stretch"):
                    st.session_state.household_children = [
                        x for x in st.session_state.household_children if x["id"] != cid]
                    for old_key in list(st.session_state):
                        if old_key.startswith(key):
                            del st.session_state[old_key]
                    st.rerun()
                if is_open:
                    label = st.text_input(_h(language, "child_name"), value=draft["label"], key=key + "label")
                    # Align fields by semantic row, not by uneven vertical stacks.
                    a, b = st.columns(2, wrap=True)
                    with a:
                        age = int(st.number_input(_h(language, "child_age"), 0, 29,
                            int(draft["age_years"]), help=_h(language, "child_age_help"),
                            key=key + "age"))
                    with b:
                        support = int(st.number_input(_h(language, "end_age"), min_value=age + 1,
                            max_value=30, value=max(age + 1, int(draft["support_until_age"])),
                            help=_h(language, "end_age_help"), key=key + "support"))
                    a, b = st.columns(2, wrap=True)
                    original_month = int(draft["arrival_month"])
                    with a:
                        arrival_year = int(st.number_input(_h(language, "arrival_year"), start_year,
                            start_year + years - 1, min(start_year + (original_month - 1)//12, start_year + years - 1),
                            key=key + "year"))
                    with b:
                        month = st.selectbox(_h(language, "arrival_month"), list(range(1, 13)),
                            index=(original_month - 1)%12, key=key + "month")
                    arrival_month = (arrival_year - start_year) * 12 + int(month)
                    if arrival_month + (support - age) * 12 - 1 > years * 12:
                        st.info(_h(language, "horizon_short"))
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
                                value=float(draft["living"][j]), step=step,
                                help=_h(language, "living_help"), key=key+f"living_{j}")))
                        with b:
                            care.append(float(st.number_input(_h(language, "care"), min_value=0.,
                                value=float(draft["care_education"][j]), step=step,
                                help=_h(language, "care_help"), key=key+f"care_{j}")))
                    draft.update(label=label, age_years=age, arrival_month=arrival_month,
                        support_until_age=support, included_in_baseline=included,
                        living=tuple(living), care_education=tuple(care))
                    st.caption(_h(language, "end_note"))
        st.divider()
        st.markdown("**" + _h(language, "dependent_title") + "**")
        st.caption(_h(language, "dependent_hint"))
        if st.button("＋ " + _h(language, "add_dependent"),
                     key="household_add_dependent", width="stretch"):
            if len(st.session_state.household_dependents) < 12:
                did = st.session_state.household_dependent_id
                st.session_state.household_dependent_id += 1
                st.session_state.household_dependents.append(dict(asdict(DependentBudget(
                    label=_h(language, "dependent_label", n=did),
                    duration_months=min(120, years * 12))), id=did))
                st.rerun()
        if not st.session_state.household_dependents:
            st.caption(_h(language, "dependent_empty"))
        for index, draft in enumerate(st.session_state.household_dependents, start=1):
            did = draft["id"]
            key = f"dependent_{did}_"
            month0 = max(1, int(draft["first_month"]))
            start_y = start_year + (month0 - 1) // 12
            start_m = (month0 - 1) % 12 + 1
            relation_name = _h(language, "dependent_" + draft["relation"])
            name = str(draft["label"]).strip() or _h(language, "dependent_label", n=index)
            summary = _h(language, "dependent_summary", relation=relation_name,
                year=start_y, month=start_m, duration=draft["duration_months"])
            open_key = key + "open"
            with st.container(border=True):
                is_open = st.session_state.get(open_key, False)
                head, delete = st.columns([8, 2], vertical_alignment="center", gap="small", wrap=False)
                if head.button(f"{'▾' if is_open else '▸'} 🤝 {name} · {summary}",
                               key=key + "toggle", type="tertiary", width="stretch"):
                    st.session_state[open_key] = not is_open
                    st.rerun()
                if delete.button("✕", key=key + "remove",
                                 help=_h(language, "card_remove_help"), width="stretch"):
                    st.session_state.household_dependents = [
                        x for x in st.session_state.household_dependents if x["id"] != did]
                    for old_key in list(st.session_state):
                        if old_key.startswith(key):
                            del st.session_state[old_key]
                    st.rerun()
                if is_open:
                    label = st.text_input(_h(language, "dependent_label", n=index),
                        value=draft["label"], key=key + "label")
                    relation = st.selectbox(_h(language, "dependent_relation"),
                        DEPENDENT_RELATIONS, index=DEPENDENT_RELATIONS.index(draft["relation"]),
                        format_func=lambda x: _h(language, "dependent_" + x), key=key + "relation")
                    col_y, col_m = st.columns(2, wrap=True)
                    with col_y:
                        year = st.number_input(_h(language, "dependent_start"),
                            min_value=start_year, max_value=start_year + years - 1,
                            value=min(start_y, start_year + years - 1), step=1, key=key + "year")
                    with col_m:
                        month = st.selectbox(_h(language, "dependent_month"),
                            list(range(1, 13)), index=start_m - 1, key=key + "month")
                    first_month = (int(year) - start_year) * 12 + int(month)
                    duration = st.number_input(_h(language, "dependent_duration"),
                        min_value=1, max_value=years * 12 - first_month + 1,
                        value=min(int(draft["duration_months"]), years * 12 - first_month + 1),
                        step=1, key=key + "duration")
                    col_s, col_c = st.columns(2, wrap=True)
                    with col_s:
                        support = st.number_input(_h(language, "dependent_support"),
                            min_value=0., value=float(draft["monthly_support"]),
                            step=step, key=key + "support")
                    with col_c:
                        care = st.number_input(_h(language, "dependent_care"),
                            min_value=0., value=float(draft["monthly_care"]),
                            step=step, key=key + "care")
                    if first_month == 1:
                        included = st.checkbox(_h(language, "dependent_included"),
                            value=bool(draft["included_in_baseline"]), key=key + "included")
                    else:
                        included = False
                    draft.update(label=label, relation=relation, first_month=first_month,
                        duration_months=int(duration), monthly_support=float(support),
                        monthly_care=float(care), included_in_baseline=bool(included))
        st.divider()
        st.markdown("**" + _h(language, "adult_title") + "**")
        if st.button("＋ " + _h(language, "add_adult"), key="household_add_adult", width="stretch"):
            if len(st.session_state.household_adults) < 8:
                aid = st.session_state.household_adult_id
                st.session_state.household_adult_id += 1
                remaining = max(0., 100. - sum(a["income_share_pct"] for a in st.session_state.household_adults))
                st.session_state.household_adults.append(dict(asdict(AdultBudget(
                    label=_h(language, "adult_label", n=aid), income_share_pct=remaining)), id=aid))
                st.rerun()
        if not st.session_state.household_adults:
            st.caption(_h(language, "empty_adults"))
        else:
            st.caption(_h(language, "adult_note"))
        for index, draft in enumerate(st.session_state.household_adults, start=1):
            aid = draft["id"]
            key = f"adult_{aid}_"
            adult_name = str(draft["label"]).strip() or _h(language, "adult_label", n=index)
            adult_summary = _h(language, "adult_summary", age=draft["age_years"],
                share=draft["income_share_pct"], retire=draft["retirement_age"])
            open_key = key + "open"
            with st.container(border=True):
                is_open = st.session_state.get(open_key, False)
                head, delete = st.columns([8, 2], vertical_alignment="center", gap="small", wrap=False)
                if head.button(f"{'▾' if is_open else '▸'} 🧑 {adult_name} · {adult_summary}",
                               key=key + "toggle", width="stretch", type="tertiary"):
                    st.session_state[open_key] = not is_open
                    st.rerun()
                if delete.button("✕", key=key + "remove",
                                 help=_h(language, "card_remove_help"), width="stretch"):
                    st.session_state.household_adults = [
                        x for x in st.session_state.household_adults if x["id"] != aid]
                    for old_key in list(st.session_state):
                        if old_key.startswith(key):
                            del st.session_state[old_key]
                    st.rerun()
                if is_open:
                    label = st.text_input(_h(language, "adult_name"), value=draft["label"], key=key+"label")
                    a, b = st.columns(2, wrap=True)
                    with a:
                        age = int(st.number_input(_h(language, "adult_age"), min_value=18, max_value=120,
                            value=int(draft["age_years"]), key=key + "age"))
                    with b:
                        income_share = float(st.number_input(_h(language, "income_share"), min_value=0.,
                            max_value=100., value=float(draft["income_share_pct"]), step=5., help=_h(language, "income_share_help"), key=key+"share"))
                    a, b = st.columns(2, wrap=True)
                    with a:
                        retirement_age = int(st.number_input(_h(language, "retirement_age"), min_value=18,
                            max_value=100, value=int(draft["retirement_age"]), help=_h(language, "retirement_age_help"), key=key+"retirement"))
                    with b:
                        replace_pct = float(st.number_input(_h(language, "replacement"), min_value=0.,
                            max_value=200., value=float(draft["retirement_replacement_pct"]), step=5.,
                            help=_h(language, "replacement_help"), key=key+"replace"))
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
        for draft in st.session_state.household_dependents:
            if draft["included_in_baseline"]:
                already_included += draft["monthly_support"] + draft["monthly_care"]
        if already_included > monthly_expenses + 1e-7:
            st.error(_h(language, "baseline_over"))
        if (not st.session_state.household_children and not st.session_state.household_adults
                and not st.session_state.household_dependents):
            st.caption(_h(language, "nophases"))
    children = tuple(ChildBudget(**{k:v for k,v in child.items() if k != "id"})
        for child in st.session_state.household_children)
    adults = tuple(AdultBudget(**{k:v for k,v in adult.items() if k != "id"})
        for adult in st.session_state.household_adults)
    dependents = tuple(DependentBudget(**{k:v for k,v in person.items() if k != "id"})
        for person in st.session_state.household_dependents)
    return children, adults, dependents
