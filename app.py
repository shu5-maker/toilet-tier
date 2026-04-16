import streamlit as st 
import pandas as pd 
import os 
DATA_FILE = "toilet_data.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["名前","Tier","合計点","便器","清潔感","匂い","洗面台","物置","レバー","広さ","感覚"
        ])
        
st.title("トイレTier")
with st.form("evaluation_form",clear_on_submit=True):
     
     
    st.subheader("トイレの場所")
    toilet_name=st.text_input("例:ルクア大阪10階トイレ")
    q_benki = st.selectbox("便器",["0:和式","1:洋式","2:洋式ウォシュレット","3:洋式ウォシュレット（便器温かい）"])
    q_seiketukan=st.selectbox("清潔感",["0:使いたくない","1:明らかな汚れ","2:多少の汚れ","3:完璧"])
    q_nioi=st.selectbox("匂い",["0:耐えられない","1:明らかに臭い","2:多少気になる","3:完璧"])
    q_senmendai=st.selectbox("洗面台",["0:手動","1:自動、手動石鹸","2:自動、自動石鹸、乾燥機orペーパー"])
    q_monooki=st.selectbox('物置',["0:何もない","1:フックだけ","2:バック置く場所あり"])
    q_reba=st.selectbox("レバー",["0:手動","1:手動（回すやつ）","2:センサー、ボタン"])
    q_hirosa=st.selectbox("広さ",["0:極端に狭い","1:普通","2:広々使える"])
    q_kankaku=st.selectbox("感覚",["0:もう使いたくない","1:可もなく不可もなく","2:普通","3:いい感じ","4:神"])

    submitted = st.form_submit_button("評価を記録する")

if submitted:
    if toilet_name == "":
        st.error("トイレの名前を入力してください")
    else:
        scores = [
            int(q_benki[0]),int(q_seiketukan[0]),int(q_nioi[0]),int(q_senmendai[0]),int(q_monooki[0]),int(q_reba[0]),int(q_hirosa[0]),int(q_kankaku[0])
        ]
        total_score = sum(scores)

        if   total_score >= 21: tier ="SS"
        elif total_score >= 18: tier="S"
        elif total_score >=14: tier="A"
        elif total_score >= 10: tier ="B"
        elif total_score >=6: tier ="C"
        else:tier = "D"

        new_data = pd.DataFrame([{
    "名前":toilet_name,"Tier":tier,"合計点":total_score,"便器":q_benki,"清潔感":q_seiketukan,"匂い":q_nioi,"洗面台":q_senmendai,"物置":q_monooki,"レバー":q_reba,"広さ":q_hirosa,"感覚":q_kankaku
}])

        df=load_data()
        df=pd.concat([df,new_data],ignore_index=True)
        df.to_csv(DATA_FILE,index=False,encoding="utf-8-sig")

        st.success(f"{toilet_name}を{total_score}点(Tier{tier})で記録しました")

st.divider()
st.subheader("現在のTierリスト")
current_df = load_data()
if not current_df.empty:
    st.dataframe(current_df,use_container_width=True)
    