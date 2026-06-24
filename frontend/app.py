import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap

st.set_page_config(
    page_title="Urban Heat Intelligence Platform",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Urban Heat Intelligence Platform")
st.markdown("Analyze urban heat islands and discover cooling interventions.")

st.sidebar.title("Navigation")
st.sidebar.info("Map & GIS Module Active")

# 1. City Search
st.header("City Search & Geolocation")
city_name = st.text_input("Enter a City Name to Analyze:", value="New York")

if st.button("Analyze City"):
    st.session_state.show_analysis = True

if st.session_state.get("show_analysis", False):
    # 2. Fetch Heatmap Data from Backend
    with st.spinner(f"Analyzing heat data for {city_name}..."):
        try:
            # We also hit the analyze-city endpoint to log it in DB
            requests.post(
                "https://urban-heat-app.onrender.com/analysis/analyze-city", 
                json={"city_name": city_name, "latitude": 40.7128, "longitude": -74.0060}
            )
            
            res_map = requests.get(f"https://urban-heat-app.onrender.com/analysis/heat-map?city_name={city_name}")
            res_hotspots = requests.get(f"https://urban-heat-app.onrender.com/analysis/hotspots?city_name={city_name}")
            
            if res_map.status_code == 200 and res_hotspots.status_code == 200:
                data = res_map.json()
                heatmap_data = data.get("heatmap_data", [])
                
                hotspot_data = res_hotspots.json()
                base_temp = hotspot_data.get("base_temperature")
                overall_risk = hotspot_data.get("overall_risk")
                
                # Display Risk Metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("Average Temperature", f"{base_temp} °C")
                col2.metric("Overall Heat Risk", overall_risk)
                col3.metric("Detected Hotspots", len(hotspot_data.get("hotspots", [])))
                
                st.write("### Hotspot Breakdown")
                for hs in hotspot_data.get("hotspots", []):
                    st.info(f"**{hs['name']}** - Estimated Temp: {hs['estimated_temp']}°C | Risk: {hs['risk']}")
                
                # 3. OpenStreetMap Integration via Folium
                start_coords = [40.7128, -74.0060] # Default center
                if heatmap_data:
                    start_coords = [heatmap_data[0]["lat"], heatmap_data[0]["lon"]]
                    
                m = folium.Map(location=start_coords, zoom_start=12, tiles="OpenStreetMap")
                
                # 4. Marker System
                folium.Marker(
                    start_coords,
                    popup=f"<b>{city_name}</b><br>City Center",
                    tooltip="Click for details",
                    icon=folium.Icon(color="red", icon="info-sign")
                ).add_to(m)
                
                # 5. Heat Visualization
                heat_data = [[point["lat"], point["lon"], point["intensity"]] for point in heatmap_data]
                HeatMap(heat_data, radius=20, blur=15, max_zoom=1).add_to(m)
                
                # Render the map in Streamlit
                st.subheader(f"Interactive Heat Map: {city_name}")
                st_folium(m, width=900, height=500)
                
                # 6. Recommendation Engine
                st.write("---")
                st.header("💡 Cooling Recommendations")
                res_recs = requests.post(f"https://urban-heat-app.onrender.com/interventions/recommendations", json={"city_name": city_name, "risk_category": overall_risk})
                if res_recs.status_code == 200:
                    recs_data = res_recs.json().get("recommendations", [])
                    for rec in recs_data:
                        with st.expander(f"{rec['type']} (Impact: {rec['impact']})"):
                            st.write(f"**Action:** {rec['details']}")
                            st.success(f"**Estimated Cooling Effect:** -{rec['cooling_effect_celsius']}°C")
                            st.info(f"**Environmental Impact:** {rec['environmental_impact']}")
                
            else:
                st.error("Error fetching map data from backend.")
                
            # Phase 6: What-If Simulator
            st.write("---")
            st.header("⚙️ What-If Simulator")
            st.write("Adjust the sliders below to simulate the cooling effect of interventions.")
            col_sim1, col_sim2, col_sim3 = st.columns(3)
            trees_to_add = col_sim1.slider("Trees to Plant", 0, 50000, 1000)
            roofs_area = col_sim2.slider("Cool Roofs Area (sqm)", 0.0, 100000.0, 5000.0)
            parks_to_add = col_sim3.slider("New Parks", 0, 20, 2)
            
            if st.button("Run Simulation"):
                sim_res = requests.post("https://urban-heat-app.onrender.com/interventions/simulate", json={
                    "city_name": city_name,
                    "trees_added": trees_to_add,
                    "cool_roofs_area": roofs_area,
                    "new_water_bodies": parks_to_add
                })
                if sim_res.status_code == 200:
                    sim_data = sim_res.json()
                    st.success(f"**Predicted Temperature Reduction:** -{sim_data['predicted_temp_reduction_celsius']}°C")
                    st.info(f"**Improvement Score:** {sim_data['improvement_score']}/100")
            
            # Phase 7: Future Heat Prediction
            st.write("---")
            st.header("📈 Future Heat Prediction")
            st.write("Projected temperature trend over the next 12 months.")
            pred_res = requests.post("https://urban-heat-app.onrender.com/ai/predict", json={"city_name": city_name, "months_ahead": 12})
            if pred_res.status_code == 200:
                forecast_data = pred_res.json().get("forecast", [])
                if forecast_data:
                    import pandas as pd
                    df = pd.DataFrame(forecast_data)
                    st.line_chart(df.set_index("month"))
            
            # Phase 8: AI City Planner Assistant
            st.write("---")
            st.header("🤖 AI City Planner Assistant")
            user_msg = st.text_input("Ask the AI about urban planning for this city:")
            if st.button("Send to AI"):
                ai_res = requests.post("https://urban-heat-app.onrender.com/ai/chat", json={
                    "message": user_msg,
                    "context": {"city": city_name, "risk": overall_risk, "temp": base_temp}
                })
                if ai_res.status_code == 200:
                    st.info(ai_res.json().get("response"))
            
            # Phase 9: Report Generation
            st.write("---")
            st.header("📄 Export Intelligence Report")
            if st.button("Generate PDF Report"):
                rep_res = requests.post("https://urban-heat-app.onrender.com/reports/generate-report", json={
                    "city_name": city_name,
                    "data_summary": {"Average Temp": f"{base_temp}°C", "Risk Level": overall_risk}
                })
                if rep_res.status_code == 200:
                    report_url = rep_res.json().get("report_url")
                    st.success("Report generated successfully!")
                    st.markdown(f"[📥 Download PDF Report](https://urban-heat-app.onrender.com{report_url})")

        except Exception as e:
            st.error("Failed to connect to the backend server. (If you aren't running the backend locally right now, you will see this error).")

st.markdown("---")
st.caption("Phase 10: All Hackathon Modules Active")
