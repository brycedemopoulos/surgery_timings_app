import streamlit as st
from multiapp import MultiApp
from apps import home, fake, real # import your app modules here

app = MultiApp()

st.markdown("""
# Surgery Timings Database

This multi-page app was created using the [streamlit-multiapps](https://github.com/upraneelnihar/streamlit-multiapps) framework. """)

# Add all your application here
app.add_app("Home", home.app)
app.add_app("Deformity Cases of 3 Surgeons", real.app)
app.add_app("Example Data", fake.app)
# The main app
app.run()
