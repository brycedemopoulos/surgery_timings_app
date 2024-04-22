import streamlit as st
from multiapp import MultiApp
from apps import home, fake, real # import your app modules here

app = MultiApp()

st.markdown("""
# Surgery Timings Database

This multi-page app was created using the [streamlit-multiapps](https://github.com/upraneelnihar/streamlit-multiapps) framework. Create the graph of your dreams using the new interactive Surgey Timings Database. 

""")

# Add all your application here
app.add_app("Home", home.app)
app.add_app("Real Data", real.app)
app.add_app("Fake Data", fake.app)
# The main app
app.run()
