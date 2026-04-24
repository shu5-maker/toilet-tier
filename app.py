import streamlit as st 
import pandas as pd 
import os 
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
from streamlit_gsheets import GSheetsConnection
DATA_FILE = "toilet_data.csv"

conn = st.connection("gsheets",type=GSheetsConnection)
def load_data():
    try:
        # 🌟 0（毎回通信）をやめて、600（10分間は記憶する）に変更！
        df = conn.read(ttl=600)
        df = df.dropna(how="all") 
        if df.empty or len(df.columns) == 0:
            return pd.DataFrame(columns=["名前","Tier","合計点","lat","lng","便器","清潔感","匂い","洗面台","物置","レバー","広さ","感覚"])
        df['lat'] = pd.to_numeric(df['lat'],errors='coerce')
        df['lng'] = pd.to_numeric(df['lng'],errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"🚨 Googleからの本当のエラーメッセージ: {e}")
        st.stop()
        
st.set_page_config(page_title="トイレTier",layout="centered")
st.title("トイレTier")
tab1,tab2=st.tabs(["評価を記録する","マップで探す"])
with tab1:
    loc = streamlit_geolocation()
    curr_lat = loc.get('latitude') if loc else None
    curr_lng = loc.get('logtiude') if loc else None
    st.info("※スマホの場合は、ブラウザの位置情報許可を「許可」にしてください")
    location_method=st.radio("位置情報の入力方法",["GPSで取得","地図から選択"],horizontal = True)
    selected_lat,selected_lng = None,None
    
    if location_method =="GPSで取得":
       if curr_lat and curr_lng:
           selected_lat,selected_lng = curr_lat,curr_lng
           st.success("現在地を取得しました。下のフォームを入力してください")
       else:
           st.warning("GPSボタンを押して現在地を取得してください")
    else:
        if curr_lat is not None and curr_lng is not None:
            center_coords = [curr_lat,curr_lng]
        else:
            center_coords =[34.7024,135.4959]
        st.info("地図をタップして位置を指定してください")
        
         
        m_reg = folium.Map(location = center_coords,zoom_start=17)
        
        df = load_data()
        for _, row in df.iterrows():
            try:
                lat = float(row['lat'])
                lng = float(row['lng'])
                
                if pd.isna(lat) or pd.isna(lng):
                    continue
                
                folium.CircleMarker(
                    location=[lat,lng],
                    radius = 5,
                    color ='blue' if row ['Tier'] != 'SS' else 'gold',
                    tooltip =f"{row['名前']}(Tier:{row['Tier']})"
                ).add_to(m_reg)
            except (ValueError,TypeError):
                pass
        reg_map_data = st_folium(m_reg,width=700,height=400,key='reg_map')
        
        if reg_map_data.get("last_clicked"):
            selected_lat = reg_map_data["last_clicked"]["lat"]
            selected_lng = reg_map_data["lact_clicked"]["lng"]
            st.success(f"選択中の位置:({selected_lat:.5f},{selected_lng:.5f})")
            
       
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
        q_nioi=st.selectbox("匂い",["未選択","0:耐えられない","1:明らかに臭い","2:多少気になる","3:無臭"])
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
    elif selected_lat is None or selected_lng is None:
        st.error("位置情報が選択されていません。GPSボタンを押すか、地図をクリックしてください")
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
    "名前":final_name,"Tier":tier,"合計点":total_score,"lat":selected_lat,"lng":selected_lng,"便器":q_benki,"清潔感":q_seiketukan,"匂い":q_nioi,"洗面台":q_senmendai,"物置":q_monooki,"レバー":q_reba,"広さ":q_hirosa,"感覚":q_kankaku
}])
        
        df=pd.concat([load_data(),new_row],ignore_index=True)

        conn.update(data=df)
        st.cache_data.clear()

        st.success(f"{final_name}を{total_score}点(Tier{tier})で記録しました")
# 🚨 データの全削除ボタン（管理者用）
if st.button("⚠️ 全データを削除してリセットする"):
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE) # ファイルそのものを削除
        st.warning("データをすべて削除しました。ページを再読み込みしてください。")
        st.rerun()
with tab2:
    st.subheader("梅田エリア　トイレマップ")
    df = load_data()
    m = folium.Map(location=[34.7024,135.4959],zoom_start=15)
    for index,row in df.iterrows():
        try:
            lat = float(row['lat'])
            lng = float(row['lng'])

            if pd.isna(lat) or pd.isna(lng):
                continue
            
            google_map_url=f"https://www.google.com/maps/dir/?api=1&destination={row['lat']},{row['lng']}"
            popup_html = f"""
                <b>{row['名前']}</b><br>
                Tier:{row['Tier']}({row['合計点']}点)<br>
                <a href = "{google_map_url}" target="_blank">　Googleマップでルート表示</a>
            """
            folium.Marker(
                location=[lat,lng],
                popup=folium.Popup(popup_html,max_width=300),
                tooltip=row['名前'],
                icon=folium.Icon(color="red"if row['Tier']in["SS","S"]else "blue")
            ).add_to(m)
        except:
            pass
    st_folium(m,width=700,height=500)
    
st.divider()
st.subheader("現在のTierリスト")
current_df = load_data()
if not current_df.empty:
    st.dataframe(current_df,use_container_width=True)
    
