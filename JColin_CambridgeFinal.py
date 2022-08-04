#Jacqueline Colin Vazquez
#Data set: Cambridge
#URL:
#Description: This app considers the users preferences on properties at Cambridge and provides insights to drive informed decision making.

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk
import plotly.express as px

#Load Data
df = pd.read_csv("Cambridge_Property_Database_FY2022_8000_sample.csv",encoding= "UTF-8")

st.title("Cambridge Property Finder")
st.header("Let's find you the Cambridge property of your dreams!")

#Create a function to add a line for design purposes
def horizontal_line(color='black'):
    st.markdown('<hr style="height:8px;border:none;color:' + color + ';background-color:' + color + ';" /> ', unsafe_allow_html=True)

#Create a function for calculating a Numeric Range (with 4 parameters)
def NumRange(min1,max1,df,column="SalePrice"):
    numeric_range = df[df[column].between(min1,max1)]
    return numeric_range

#UI Control 1. Text Box

#Price Range
st.subheader("Price Range")
st.write("Submit desired price range :")
min1 = st.number_input('Minimum', 0, 360000,value=1000)
max1 =  st.number_input('Maximum', 0, 360000,value=50000)
p = NumRange(min1,max1,df)
st.write('There are',len(p.index), 'properties with a price range between $', min1, 'and $', max1)

#UI Control 2. Slider

#Living area
st.subheader("Living Area Range")
area = st.slider('Select Living Area Range',0,3000, (650, 1100))
a = NumRange(area[0],area[1],p, column= "Interior_LivingArea") #use p as initial data base
st.write("You've selected properties larger than ",area[0], "but smaller than ", area[1])
st.write("There are ",len(a.index), "properties that fill both parameters.")

#Merge Parking Colums with a loop
park = a.loc[:, ['Parking_Open', 'Parking_Covered','Parking_Garage']]
park_merge = park.sum(axis = 1)
parking = []
for line in range(0,len(a.index)):
    if park_merge.iloc[line] > 0:
        parking.append("With")
    else:
        parking.append("Without")

#UI Control 3. Selectbox
st.subheader("Parking Availability")
parking_select = st.selectbox(
    'I am looking for a property ___ parking: ',
    ("With","Without")
)
st.write("You have selected a property ",parking_select.lower()," parking available.")

#Parking Criteria
a["With_Parking"] = parking
x = a[a["With_Parking"]== parking_select]
st.write("There are ",len(x.index),"properties that match all criteria.")

horizontal_line()

st.header("Find below all details about your potential properties:")

#Create a function to sort new data set "x" for properties that meet the user's criteria
def PropertiesCriteria(x,n = 25,ascending_order = True):
    props = x.loc[:,["Address","SalePrice","Interior_LivingArea","Interior_TotalRooms","Interior_Bedrooms","Interior_FullBaths","With_Parking","PropertyTaxAmount", "Latitude","Longitude"]]
    props = props.sort_values(by = "SalePrice",ascending = ascending_order)
    props = props.head(n)
    st.dataframe(props)
    return props

props = PropertiesCriteria(x)

#Chart 1: Map
st.subheader("Where in Cambridge?")
map_info = props
map_info.rename({'Latitude': 'lat', 'Longitude': 'lon'}, axis=1, inplace=True)
#map_info = map_info.loc[:,["lat","lon"]]
#st.map(map_info)

view_state = pdk.ViewState(
    latitude = map_info["lat"].mean(),
    longitude = map_info["lon"].mean(),
    zoom=11,
    pitch=0)

layer1 = pdk.Layer('ScatterplotLayer',
                  data = map_info,
                  get_position='[lon, lat]',
                  get_radius=250,
                  get_color=[100,0,155],
                  pickable=True
                  )

map = pdk.Deck(
    map_style='mapbox://styles/mapbox/outdoors-v11',
    initial_view_state = view_state,
    layers = layer1
)

st.pydeck_chart(map)

#Chart 2: Barchart
st.subheader("How much?")
def line_plot(props, title):
    plt.bar(props.loc[:,"Address"], color='orange',height = props.loc[:,"SalePrice"])
    plt.title(title)
    plt.xticks(rotation = 90)
    plt.xlabel("Property Address")
    plt.ylabel("Sale Price ($)")
    return plt

st.set_option('deprecation.showPyplotGlobalUse', False) #turns off a warning in streamlit
st.pyplot(line_plot(props,title= "Your Top Cambridge Properties"))

#Chart 3:
st.subheader("How many bedrooms?")
fig = px.scatter(props, y="Address", x="Interior_TotalRooms",symbol="Interior_Bedrooms")
fig.update_traces(marker_size=10)
st.write(fig)

horizontal_line('white')
