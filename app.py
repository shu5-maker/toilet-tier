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
df = load_data()
existing_names=df["名前"].unique().tolist() if not df.empty else[]
name_options = ["新しく登録する"]+existing_names
with st.form("evaluation_form",clear_on_submit=True):
    st.subheader("どこにあるトイレ？")
    
    selected_name=st.selectbox("登録済みの場所から選ぶ",name_options)
    
    new_name=""
    if selected_name == "新しく登録する":
        new_name = st.text_input("新しいトイレの名前を入力（例：ルクア大阪10階トイレ）")
     
     
    st.subheader("評価（すべて必須です）")
    q_benki = st.selectbox("便器",["未選択","0:和式","1:洋式","2:洋式ウォシュレット","3:洋式ウォシュレット（便器温かい）"])
    q_seiketukan=st.selectbox("清潔感",["未選択","0:使いたくない","1:明らかな汚れ","2:多少の汚れ","3:完璧"])
    q_nioi=st.selectbox("匂い",["未選択","0:耐えられない","1:明らかに臭い","2:多少気になる","3:完璧"])
    q_senmendai=st.selectbox("洗面台",["未選択","0:手動","1:自動、手動石鹸","2:自動、自動石鹸、乾燥機orペーパー"])
    q_monooki=st.selectbox('物置',["未選択","0:何もない","1:フックだけ","2:バック置く場所あり"])
    q_reba=st.selectbox("レバー",["未選択","0:手動","1:手動（回すやつ）","2:センサー、ボタン"])
    q_hirosa=st.selectbox("広さ",["未選択","0:極端に狭い","1:普通","2:広々使える"])
    q_kankaku=st.selectbox("感覚",["未選択","0:もう使いたくない","1:可もなく不可もなく","2:普通","3:いい感じ","4:神"])

    submitted = st.form_submit_button("評価を記録する")

if submitted:
    final_name = new_name if selected_name == "新しく登録する"else selected_name
    
    all_responses = [q_benki,q_seiketukan,q_nioi,q_senmendai,q_monooki,q_reba,q_hirosa,q_kankaku]
    
    if final_name == ""or"未選択" in all_responses:
        st.error("すべての項目を回答してください!名前が空欄または未選択の項目があります")
    else:
        scores = [int(r.split(":")[0])for r in all_responses]
        total_score = sum(scores)

        if   total_score >= 21: tier ="SS"
        elif total_score >= 18: tier="S"
        elif total_score >=14: tier="A"
        elif total_score >= 10: tier ="B"
        elif total_score >=6: tier ="C"
        else:tier = "D"

        new_row = pd.DataFrame([{
    "名前":final_name,"Tier":tier,"合計点":total_score,"便器":q_benki,"清潔感":q_seiketukan,"匂い":q_nioi,"洗面台":q_senmendai,"物置":q_monooki,"レバー":q_reba,"広さ":q_hirosa,"感覚":q_kankaku
}])
        
        df=pd.concat([load_data(),new_row],ignore_index=True)
        df.to_csv(DATA_FILE,index=False,encoding="utf-8-sig")

        st.success(f"{final_name}を{total_score}点(Tier{tier})で記録しました")

st.divider()
st.subheader("現在のTierリスト")
current_df = load_data()
if not current_df.empty:
    st.dataframe(current_df,use_container_width=True)
    
