import streamlit as st
import streamlit.components.v1 as components

def get_coordinates():
    # JavaScript to get user's coordinates
    components.html(
        """
        <script>
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const coords = {
                    lat: position.coords.latitude,
                    lon: position.coords.longitude
                };
                window.parent.postMessage(coords, "*");
            },
            (error) => {
                window.parent.postMessage({error: error.message}, "*");
            }
        );
        </script>
        """,
        height=0,
    )
